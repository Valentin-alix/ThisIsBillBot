## Presentation

This application is a bot MITM (Man in the Middle), he send network data to a server and receive them to gather datas

It's made in PyQt and use QFluentWidget

The bot can Fight, Farm, Harvest, Sell, Update price, Scrap price, Craft

## Guideline

- Always type hint the code, use built in type of python instead of importing from typing when it's possible, example :

  - BAD : List[int]
  - Good : list[int]

- Don't overcomment for nothing, use comment in code only when necessary

- Don't catch exception too large, example :

  - BAD : except Exception
  - GOOD : except ValueError

- Centralize IO Manager in controller folder

- Centralize interfaces, types, enum in interfaces folder

- Always use Component from QFluentWidget when it's possible

- Don't use ternary

- Please KEEP IT SIMPLE, don't over complexify things when it's not necessary and DRY (don't repeat yourself)

### Architecture

- In src/core folder you have all logic related to the bot, how he treat datas, how he send them etc..
  - Behaviors folder contains all the file who can directly interact with the server, for exemple ChatBehavior can send message to global channel
  - Frames folder contains all the listeners who listen for specific messages and update the states of the bot
  - States folder contains all the properties related to the bot
  - Logic folder contains primarly logic related to the game itself

Network datas are first received in proxy (GameProxy & ConnectionProxy) then they are send to event_manager which is gonna dispatch the messages received to the different frames & behavior who listen to it.

### Tests

- I use unittest, so use it aswell

## Commands & misc

`python -m cProfile -o tools/d3mapping_profiled D3Mapping/d3_mapping/main.py`

- frida -n Dofus.exe -l script_frida.js

### Mitm

- `poetry run python __main__.py`

![harvest](./docs/pres_harvest.gif)

![automatic_path](./docs/automatic_path.png)

![grid_state](./docs/grid_state.png)

![sniffer](./docs/sniffer.png)

### Profiling

`poetry run python -m cProfile -o benchmark.pstats __main__.py`
`gprof2dot -f pstats benchmark.pstats | dot -Tpng -o benchmark_output.png`

# pyarmor limite à 20 fichiers maxi

`poetry run pyarmor gen -O dist-obf **main**.py src D3Mapping DBDofusUnity D3Database --recursive`

`poetry run pyinstaller --add-data "D3Database/bundles":"D3Database/bundles" --add-data "D3Mapping/d3_mapping/resources":"d3_mapping/resources" --add-data "resources":"resources" --add-data ".venv/Lib/site-packages/wonderwords/assets:wonderwords/assets" **main**.py --noconfirm`
