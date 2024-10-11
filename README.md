## Mitm

Config proxy :
- Get https://github.com/Valentin-alix/Mitm-Http.git : 
- Create localhost proxy at port 8080
- `nohup poetry run python main.py &`

Mitm :
- `poetry run python __main__.py`

![harvest](./docs/pres_harvest.gif)


![automatic_path](./docs/automatic_path.png)

![grid_state](./docs/grid_state.png)

![sniffer](./docs/sniffer.png)

Autres :

Profiling :
`gprof2dot -f pstats benchmark.pstats | dot -Tpng -o benchmark_output.png`

TODO :
- Avec le sniffer, capturer ses temps de réaction dans une session de farming et de fight pour les reproduire dans les temps d'attente (avec écart type etc...)

PyInstaller -> pyinstaller --add-data "D3Database":"D3Database" --add-data "resources":"resources" __main__.py --noconfirm