## Requirements

### Proto

protoc-28.0 : https://github.com/protocolbuffers/protobuf/releases/download/v28.0/protoc-28.0-win64.zip (depending on
your os)

### Datas

#### Patch CRCs to 0 (No idea what this is doing & why we do it):

Get https://github.com/nesrak1/AddressablesTools/releases

`cd %USERPROFILE%\Documents\Workspace\UABEA_Example`

`Example.exe patchcrc %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Data/catalog_1.0.json`

`Example.exe patchcrc %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map/catalog_1.0.json`

It generates catalog_1.0.json.patched, you can then rename this to catalog_1.0.json

#### Get exported datas

Get https://github.com/Valentin-alix/UABEA.git

First launch : `poetry run python src/on_init.py`

To do every maj : `poetry run python src/on_maj.py`