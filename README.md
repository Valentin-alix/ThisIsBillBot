## Requirements

### Proto

protoc-28.0 : https://github.com/protocolbuffers/protobuf/releases/download/v28.0/protoc-28.0-win64.zip (depending on
your os)

- Get BepinexUnityIL2CPP : https://builds.bepinex.dev/projects/bepinex_be/725/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.725%2Be1974e2.zip
- Extract content to Dofus folder
- Run game from .exe to generate configuration files

- Get https://github.com/Valentin-alix/DofusUnity.Plugins.BepInEx
- Generate solution then copy and paste ProtocolDumper.dll to Dofus/Bepinex/plugins folder

### Datas

#### Patch CRCs to 0 :

Get https://github.com/nesrak1/AddressablesTools/releases

`cd %USERPROFILE%\Documents\Workspace\UABEA_Example`

`Example.exe patchcrc %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Data/catalog_1.0.json`

`Example.exe patchcrc %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map/catalog_1.0.json`

It generates catalog_1.0.json.patched, you can then rename this to catalog_1.0.json

#### Get exported datas

Get https://github.com/Valentin-alix/UABEA.git

### To Do Every Maj

You can run the game from launcher to get proto descriptors

Then launch maj.bat to update data & code :
`./scripts/maj.bat`

## Mitm

- Launch redirect.py from https://github.com/Valentin-alix/Mitm-Http.git
- Create localhost proxy at port 8080
- `poetry run python main.py`
