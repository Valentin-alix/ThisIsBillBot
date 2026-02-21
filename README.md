# Bot-DofusUnity

Framework Python 3.12 sous Windows pour la recherche protocolaire et
l’orchestration de bots Dofus Unity : GUI PyQt, runtime headless, pipeline de
messages, `GameState`, `Frame` et `Behavior`.

> Ankama interdit les bots et outils d’automatisation en jeu. Leur usage peut
> entraîner la fermeture définitive des comptes. Respectez les règles du jeu,
> les conditions des services utilisés et la loi applicable.

## Installation et exécution

```powershell
uv sync
Copy-Item .env.example .env
uv run python __main__.py
# ou
uv run python __main__.py --headless
```

Pour gÃ©nÃ©rer le paquet Windows autonome :

```powershell
uv run poe package
```

Le dossier distribuable est `dist/Bot-DofusUnity/`. Chaque push publie aussi
cette archive dans une GitHub pre-release associÃ©e au SHA du commit.

`.env` est local. Les fichiers de runtime restent aux emplacements existants :
`resources/` et `AnkamaLauncherEmulatorPremium/resources/`. Ils contiennent
notamment comptes, boîtes mail, proxies, profils, sessions et caches ; ils sont
ignorés par Git et ne doivent jamais être partagés.

Variables utiles : `DEBUG`, `OPENAI_API_KEY`, `SONJI_API_KEY`. Les workflows de mapping demandent aussi
`PROTOC_PATH`, `IDA_EXE`, `OBF_GAME_DIR` et `NON_OBF_GAME_DIR`; les exécutables
tiers peuvent être surchargés via `UABEA_EXECUTABLE`,
`IL2CPP_INSPECTOR_EXECUTABLE` et `PROTODEC_EXECUTABLE`.

## Personnalisation

- Ajouter un `Behavior` pour une opération de haut niveau.
- Ajouter un `Frame`, listener ou modifier pour faire évoluer `GameState`.
- Adapter les providers mail, les modes socket/MITM et les outils de mapping.
- Configurer les profils, proxies et comptes uniquement dans les JSON locaux,
  jamais dans le code, les tests ou les exemples.

Les outils Il2CppInspectorRedux (AGPL-3.0-only), protodec (MPL-2.0) et UABEA
(MIT) restent des dépendances séparées. Ne distribuez ni client du jeu,
artefacts extraits/générés, binaires tiers, identifiants, traces ni données de
paiement avec le projet. La licence MIT du dépôt couvre uniquement le code
original.

## Développement et publication

```powershell
uv run ruff check .
uv run pyright
uv run pytest tests
uv run poe verify
```

Les contributions doivent être ciblées, validées, et utiliser des fixtures
synthétiques. Les vulnérabilités, secrets ou données privées se signalent au
mainteneur en privé, jamais dans une issue.

Pour créer le dépôt public, partez d’un nouvel arbre Git, excluez les fichiers
runtime et artefacts listés dans `.gitignore`, scannez l’arbre et son historique
avec un outil de détection de secrets, puis révoquez toute clé déjà exposée.
Conservez les licences et notices des dépendances distribuées, activez Secret
Scanning/Push Protection, et publiez un historique court et cohérent.
