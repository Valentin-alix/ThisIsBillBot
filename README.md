`python -m cProfile -o tools/d3mapping_profiled D3Mapping/d3_mapping/main.py`

- Regarder comment se log à ankama
  -> pour pouvoir spécifier un HWID custom

* Multi farming -> si pas d'arme de chasse alors aller champs d'incarnam et bouftou d'incarnam
  -> dès que on peux craft l'arme, alors aller la craft à l'atelier forgeron

-> Automatiquement craft chasseur, et ne pas farmer des zones supérieur au niveau chasseur

- frida -n Dofus.exe -l script_frida.js

# TODO On reco, si dans donjon alors faire dongon behavior

## Mitm

- `poetry run python __main__.py`

![harvest](./docs/pres_harvest.gif)

![automatic_path](./docs/automatic_path.png)

![grid_state](./docs/grid_state.png)

![sniffer](./docs/sniffer.png)

Autres :

Profiling :
`poetry run python -m cProfile -o benchmark.pstats __main__.py`
`gprof2dot -f pstats benchmark.pstats | dot -Tpng -o benchmark_output.png`

Nouveau procédé :

Avec proxy mobile (pour pas se faire ban ip car l'ip se reset souvent en mobile)

4 comptes doivent etre créer par jour par ip pour max 8 compte par email

Depuis création du compte (toujours sacri eau):

- Monter lvl 15 au sein d'incarnam en combattant (auto monter charactéristique)
- Une fois lvl 15 go farmer à astrub ressource récoltable
- Une fois full pods mettre dans banque
- Toutes les 2 heures mettre en vente le contenu de la banque trier par prix moyen estimé et auto recolté les kamas en banque

Mule kamas (lvl 51) => si character id == MULE KAMAS alors executer behavior mule kamas

A voir plus tard mais à terme créer un perso lvl 50 pour centraliser les kamas pour la revente (un perso jetable)
et au bout de plus de 400 000 kamas sur les autres perso, donner le surplus à ce perso

TODO :

- Guild rank id pas tjrs update
- Fix un max de invalid transition
- Avec le sniffer, capturer ses temps de réaction dans une session de farming et de fight pour les reproduire dans les temps d'attente (avec écart type etc...)
- Faire bdd pour enregistrer a quel point des ressources partent vite et leur prix

# pyarmor limite à 20 fichiers maxi

`poetry run pyarmor gen -O dist-obf **main**.py src D3Mapping DBDofusUnity D3Database --recursive`

`poetry run pyinstaller --add-data "D3Database/bundles":"D3Database/bundles" --add-data "D3Mapping/d3_mapping/resources":"d3_mapping/resources" --add-data "resources":"resources" --add-data ".venv/Lib/site-packages/wonderwords/assets:wonderwords/assets" **main**.py --noconfirm`

<!-- "yolo.ezrealeu2+1747935431.2478561@outlook.fr": {
        "playtime_start": "08:00",
        "playtime_end": "23:00"
    } -->
