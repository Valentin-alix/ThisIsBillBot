# Détecteur d'archimonstres / monstres « Recherchés » (idée de port depuis Bubble)

> Statut : **idée archivée, non implémentée.** ROI jugé faible à court terme, gardé pour plus tard.
> Source : `Bubble.D3.Bot` — `BubbleBot.Cli/Services/Clients/Game/GameMonsterDiscoveryService.cs` +
> `Services/Clients/MonsterDiscoveryRegistry.cs`.

## But

Malgré son nom, le système de Bubble n'est pas un « bestiaire » : c'est un **détecteur d'archimonstres et
de monstres Recherchés** qui scanne les groupes de monstres de **chaque nouvelle map** et **alerte** (chez
Bubble : Discord) avec le nom, le niveau, le type, la position `[x, y]`, une commande `/travel x y` et le
zaap le plus proche. Une **déduplication** par `(map, monstre)` évite le spam si la map est re-rendue.

Pour un bot multi-compte qui enchaîne les maps, c'est un gain passif (repérer un archimonstre = âme de
capture / drop rare de forte valeur), en **lecture seule**, sans aucun impact sur le gameplay.

## Ce que fait Bubble (référence)

- `GameMonsterDiscoveryService.ScanMapActors(map, actors)` : pour chaque acteur de type groupe de monstres,
  parcourt la créature principale + les sous-fifres.
- `ParseMonsters` : pour chaque monstre, `MapRepository.GetMonster(gid)` → filtre sur **`Race == 78`
  (Archimonstre)** ou **`Race == 32` (Recherché)**. Construit un résumé `Nom (Lv. X) *Type*`.
- `MonsterDiscoveryRegistry.TryMarkLogged(mapId, monsterId)` : `ConcurrentDictionary` imbriqué, `TryAdd`
  renvoie `false` si déjà vu → **dédup**.
- Alerte Discord : `Trouvé <résumé> en [x, y]. /travel x y. Zaap le plus proche : <zaap>`.

## État des lieux Voldemort (tout est déjà dispo)

- `DataReader().monsters_by_id[gid] -> MonsterItem` avec `.race`, `.nameId`, **`.isBounty`**.
- `DataReader().monsters_by_race[race] -> list[MonsterItem]` (déjà indexé par race).
- `I18N().name_by_id[nameId]` pour le nom localisé.
- `DataReader().map_info_by_map_id[map_id] -> MapInformationRootItem` avec `.posX`, `.posY`.
- `get_monster_groups(actor_by_id)` (`src/core/engine/monsters/monster_group.py`) extrait déjà les groupes
  `(actor_id, MapPoint, MonsterGroupActor)` ; chaque `MonsterGroupActor.identification` a `main_creature`
  et `underlings` (chacun `gid`, `level`).
- Acteurs d'une map peuplés par `EntityFrame.on_map_complementary_info_event` via
  `set_actors(message.actors)` ; même payload `MapComplementaryInformationEvent` exploitable directement.

> Remarque : Voldemort expose `MonsterItem.isBounty`, plus propre que le `Race == 32` magique de Bubble
> pour les « Recherchés ». À privilégier (sous réserve de confirmation en jeu).

## Design proposé

Trois pièces isolées et testables (calque la séparation de Bubble) :

1. **Détection pure** — `src/core/engine/monsters/notable_monsters.py`
   - `NotableKind = Literal["archimonster", "wanted"]`.
   - `NotableMonster` (dataclass) : `gid: int`, `name: str`, `level: int`, `kind: NotableKind`.
   - `scan_notable_monsters(actors: dict[int, ActorPositionInformation]) -> list[NotableMonster]` :
     réutilise `get_monster_groups`, parcourt `main_creature` + `underlings`,
     `monster = DataReader().monsters_by_id.get(gid)` (ignore si absent), classe :
     `archimonster` si `monster.race == ARCHIMONSTER_RACE_ID`, sinon `wanted` si `monster.isBounty`,
     sinon ignore. `name = I18N().name_by_id.get(monster.nameId, str(gid))`.
   - **Constante** `ARCHIMONSTER_RACE_ID` : Bubble = `78`. À confirmer via `DataReader().monsters_by_race`.
     Conformément à la convention du repo (ids en dur dans les enums), l'ajouter de préférence à un
     `MonsterRaceEnum` dans `DBDofusUnity/dofus_unity_reader/game_constants/` (commit submodule deux
     niveaux), sinon constante nommée locale avec commentaire de vérification.

2. **Déduplication + alerte** — `ArchimonsterNotifier`
   - garde `set[tuple[int, int]]` des `(map_id, gid)` déjà signalés (équivalent `TryMarkLogged`) ;
   - `notify(map_id, monsters)` : filtre les nouveaux ; pour chacun :
     - **toujours** : log `BotLogger` en **warning** :
       `f"{kind} {name} (Niv. {level}) en [{x}, {y}] — /travel {x} {y}"` ;
     - **optionnel (config)** : webhook Discord (le projet utilise déjà `requests`, cf.
       `AnkamaLauncherEmulatorPremium/.../utils/internet.py`) — POST d'un embed si
       `VOLDEMORT_ARCHI_WEBHOOK_URL` est défini, en `try/except` (best-effort, jamais bloquant) ;
     - **optionnel (GUI)** : signal `archimonster_found = pyqtSignal(object)` dans `WorldSignals`
       (`src/core/signals/world_signals.py`) pour un toast.
   - position : `info = DataReader().map_info_by_map_id[map_id]` → `info.posX`, `info.posY`.
   - `clear()` vide la dédup ; zaap proche en option (réutiliser `get_near_waypoint`).

3. **Hook réseau** — `ArchimonsterFrame` (`src/core/frames/archimonster_frame.py`)
   - écoute `MapComplementaryInformationEvent`, lit **directement `message.actors`** (aucune dépendance à
     l'ordre de priorité entre frames) ;
   - `notifier.notify(message.map_id, scan_notable_monsters(actors))` ;
   - dédup vidée sur déconnexion : `self.game_info_signals.disconnected.connect(notifier.clear)` ;
   - instancié dans `src/core/bot/bot_factory.py` à côté de `map_frame` et ajouté à la collection de frames.

## À vérifier avant implémentation

- `ARCHIMONSTER_RACE_ID` (78 ?) en inspectant `DataReader().monsters_by_race` (races contenant des noms
  d'archimonstres connus).
- Sémantique de `MonsterItem.isBounty` (marque-t-il bien les Recherchés ?).

## Vérifications (tests)

- `scan_notable_monsters` : faux `monsters_by_id` (un archi race=78, un `isBounty`, un normal) + faux
  `actor_by_id` avec un `MonsterGroupActor` → récupère exactement l'archi + le recherché, bons
  `kind`/`name`/`level`.
- `ArchimonsterNotifier.notify` : deux appels sur le même `(map, gid)` → une seule alerte ; sans URL, pas
  de webhook ; `clear()` réarme.
- In-game : passer sur une map avec un archimonstre connu → alerte unique (pas de spam au re-rendu),
  position/`/travel` corrects.
