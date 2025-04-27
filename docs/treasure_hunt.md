# Chasse au trésor automatisée (idée de port depuis Bubble)

> Statut : **conception archivée, non implémentée.**
> Source : `Bubble.D3.Bot` — `BubbleBot.Cli/Services/TreasureHunts/` (`TreasureHuntData.cs`,
> `CluesSolver.cs`, `GiveUpReason.cs`), `Services/Clients/Game/GameTreasureHuntService.cs`,
> `Services/Clients/Game/GameFightHandler.cs`.

## Pourquoi c'est faisable rapidement

Toute l'infra réseau est déjà en place côté Voldemort :

- **Protos déjà mappés au runtime** (`DBDofusUnity/datas/protos/game_mappings.json`) :
  `TreasureHuntEvent`, `TreasureHuntFlagRequest`, `TreasureHuntDigRequest`, `TreasureHuntGiveUpRequest`,
  `TreasureHuntFlagAnswerEvent`, `TreasureHuntDigAnswerEvent`, `TreasureHuntFinishedEvent`,
  `TreasureHuntStep`. Champs disponibles : `known_steps`, `direction`, `poi_label_id`, `npc_id`,
  `map_count`, `quest_type`, `total_step_count`, `start_map_id`. → **aucun travail proto**.
- **Réutilisable** : `AutoTripBehavior.run(map_ids)` (A* cross-map,
  `src/core/behaviors/movements/auto_trip/auto_trip_behavior.py`), `directions.py`, le pattern `Behavior`
  (`start/finish/callback`, `src/core/behaviors/behavior.py`), les frames pour réagir aux events,
  `InteractiveBehavior`.

## Le point dur : la base d'indices (prérequis)

Les POI du jeu (`PointofinterestrootItem` = `id`, `nameId`, `categoryId`) **ne contiennent pas de
position**. Impossible donc de résoudre « va vers \<direction\> jusqu'à voir \<indice\> » avec les seules
données du client.

Comme Bubble, il faut **bundler une base d'indices externe** (export communautaire DofusPourLesNoobs) au
format minimal `maps: [{ x, y, clues: [poiId, ...] }]`, puis :

1. **Remapper** les `poiId` du dataset (ids DPLN) vers les `PointofinterestrootItem.id` du jeu par
   **correspondance de nom** : `I18N().name_by_id[poi.nameId]`, insensible à la casse/accents (porter
   `CluesSolver.RemoveAccents`).
2. **Résoudre** via le port de `SolveClueFromLocal(clue_poi_id, from_x, from_y, direction)` : scanne 1..10
   maps dans la direction, renvoie `(x, y)` de la première map contenant l'indice, sinon `None`.

(Le second solveur de Bubble, `SolveClue`, indexé `x_y_direction` depuis un cache DofusDB, est optionnel —
un cross-check ; la v1 peut se contenter du solveur local.)

## Flux d'une chasse (Bubble, référence)

1. **Prendre une chasse** : interactif de la machine à chasses (`ElementTypeId == 231`) sur la map de la
   salle des chasses.
2. **`TreasureHuntEvent` reçu** (`OnDataReceived`) :
   - si `flags_count == total_step_count` → `TreasureHuntDigRequest` (creuser) après ~2 s ;
   - sinon, `last_hint_map_id` = map du dernier flag (ou `start_map_id`), lit le dernier `known_step`
     (oneof) et remplit l'indice courant ;
   - `SolveNextClue()` calcule la map cible.
3. **Naviguer** vers la map cible (chez Bubble : `Map.GoToMap` ; chez nous : `AutoTripBehavior`).
4. **À l'arrivée** (`OnMapChanged`) : si la map courante = map cible → `TreasureHuntFlagRequest`
   (`quest_type`, `index = flags_count`). Le serveur répond par le `TreasureHuntEvent` suivant → boucle.
5. `OnFlagAnswer` ≠ Ok / `OnDigAnswer` Wrong* → **give-up**.
6. `TreasureHuntFinishedEvent` → succès, enchaîne la chasse suivante.

**Optimisation nav (Bubble)** : usage du **havre-sac** (`HavenBagEnterReason.GoToFirstStep`) pour se
téléporter au début d'étape plutôt que tout marcher.

**Maps interdites** : Bubble maintient une liste d'ids de maps qui déclenchent un give-up immédiat
(ex. 126878209, 147851781, 203685888, 121766912, sous-zone 469…). À porter.

## ⚠️ Le combat de chasse est SPÉCIAL

> Point vérifié et **important** — corrige une hypothèse initiale (« déléguer à l'IA de combat ») qui était
> **fausse**.

Vérifié dans `GameFightHandler.cs:86-234` + `TreasureHuntData.cs` : **quand une chasse est active
(`IsInTreasureHunt()`), TOUS les events de combat sont déroutés vers un handler dédié — l'IA de combat
normale (`FightInfo`) est totalement court-circuitée** :

```
GameActionFightEvent / FightTurnEvent / FightPlacement / FightEnd :
    if (IsInTreasureHunt()) TreasureHuntData.OnFight*(...)   // chemin spécial
    else                    FightInfo?.OnFight*(...)          // IA normale
```

Le combat de chasse fait :

1. **Cible désignée** : `FighterToHit` identifié par le **look `BonesId == 2672`** (gardien de chasse) dans
   le `FightSynchronizeEvent` ; fallback « tout combattant ≠ soi » ; rafraîchi via
   `ChangeLookValue.TargetId < 0`.
2. **Pas d'IA** : au tour, **spamme un sort fort N fois sur la cible** puis termine le tour — aucun
   déplacement, aucune pondération, pas de LoS, pas de ciblage multi-ennemis. (Bubble hardcode même un sort
   par classe.)
3. **Placement** : case « défensive » = celle qui maximise les voisins non-marchables / sans-LoS.
4. **Auto-acknowledge** des actions + **auto-ready**.

C'est spécial parce que ces combats sont triviaux et structurés autour d'**un gardien désigné**.

### Conséquence pour Voldemort

**Ne PAS déléguer à `AttackerBehavior` / `FightBehavior` (IA de farm)** : ça ferait tourner le
positionnement et la pondération inutilement, et ciblerait selon le poids de dégâts plutôt que le gardien
désigné. Implémenter un **`TreasureHuntFightBehavior` dédié** qui :

- identifie la cible par **bones id** — Voldemort expose déjà `actor.actor_information.look.bones_id` et des
  helpers `get_npc_id_by_bones` / `get_npc_id_by_cell_and_bones` dans `entity_state.py`. **Vérifier la
  valeur `2672`** dans les données Unity ; sinon fallback : combattant monstre (`AiFighter`/`MonsterGid`)
  ≠ soi ;
- réutilise **seulement les primitives de sélection de sort/dégâts** (ex. `Attacker`/sélection de sort) pour
  choisir le meilleur sort *sur cette cible précise*, puis le lance jusqu'à épuisement des PA, et termine
  le tour — **sans** la boucle de déplacement de l'IA de farm ;
- gère un **placement défensif** simple (port du scoring de voisins de Bubble).

## Architecture proposée (Voldemort)

- **Données + solveur** : `src/core/engine/treasure_hunt/clues_solver.py` (port `SolveClueFromLocal` +
  mapping nom→POI id avec `RemoveAccents`) ; charger les POI dans `DataReader`
  (`point_of_interest_by_id` + index nom→id) ; résolveur `(posX, posY, subAreaId) -> map_id` depuis
  `map_info_by_map_id`.
- **État** : `TreasureHuntState` (`src/core/states/treasure_hunt_state.py`) — `is_active`, `quest_type`,
  `flags_count`, `total_step_count`, `start_map_id`, `last_hint_map_id`, `next_clue`
  (clue_poi_id | npc_id | map_count, direction, from_x/y, target_map_id), `give_up_requested`,
  `last_give_up_reason`, compteurs anti-AFK ; vidé sur déconnexion. À ajouter dans `game_state.py`.
- **Frame** : `TreasureHuntFrame` (`src/core/frames/treasure_hunt_frame.py`) — `TreasureHuntEvent` → parse
  `known_steps.last` (oneof `follow_direction_to_poi` / `follow_direction_to_hint` / `follow_direction`) →
  remplit `next_clue` (ou état « dig » si flags complets) ; flag/dig answer KO → give-up ;
  `TreasureHuntFinishedEvent` → succès + réarme. Enregistré dans `bot_factory.py`.
- **Behavior** : `TreasureHuntBehavior` (`src/core/behaviors/farms/treasure_hunt/`) — driver événementiel :
  prendre une chasse (interactif 231, optionnel `DO_TAKE_HUNT`) → résoudre l'indice → `AutoTripBehavior`
  vers la map cible → `TreasureHuntFlagRequest` à l'arrivée → boucle ; flags complets →
  `TreasureHuntDigRequest` ; combat → `TreasureHuntFightBehavior` dédié, reprise au `FightEndEvent` ;
  give-up (indice introuvable / map interdite / AFK) ; anti-AFK simplifié.

## v1 / v2

- **v1** : indices **POI** uniquement + **combat de chasse dédié**. Indices `follow_direction_to_hint`
  (phorreur) et `follow_direction` (N maps) → **give-up propre**.
- **v2** : marcher N maps dans la direction via les transitions du **world graph** (`WorldPathFinder`/edges)
  ; **prise de chasse automatique** ; **navigation par havre-sac**.

## Vérifications (pour l'implémentation future)

- Solveur : tests `solve_clue_from_local` (trouve à distance 1..10, `None` si absent), `RemoveAccents`,
  mapping nom→POI id, résolveur coord→map_id.
- Frame : un `TreasureHuntEvent` POI → `next_clue` correct (direction/clue/from) ;
  `flags_count == total_step_count` → état « dig » ; flag/dig answer KO → give-up.
- In-game (séquentiel) :
  1. chasse prise manuellement → navigation → flag → étape suivante → dig ;
  2. chasse avec combat imposé → **handler dédié** (cible bones 2672, spam de sort, fin de tour) ;
  3. indice non résolvable → give-up propre + enchaînement de la chasse suivante.
