## Requirements

### Proto

protoc-28.0 : https://github.com/protocolbuffers/protobuf/releases/download/v28.0/protoc-28.0-win64.zip (depending on your os)

#### Get protos (to do every maj) :

<!> TODO

`poetry run python ./scripts/generator/generate_proto_from_descriptor.py` # generate protos from descriptors

`poetry run python ./scripts/generator/generate_python_from_proto.py` # generate pythons from protos

### Datas

#### Patch CRCs to 0 :

Get https://github.com/nesrak1/AddressablesTools/releases

`cd C:\Users\valen\Documents\Workspace\UABEA_Example`

`Example.exe patchcrc C:\Users\valen\AppData\Local\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Data/catalog_1.0.json`

`Example.exe patchcrc C:\Users\valen\AppData\Local\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map/catalog_1.0.json`

It generate catalog_1.0.json.patched, you can then rename this to catalog_1.0.json

#### Get exported datas (to do very maj)

Get https://github.com/Valentin-alix/UABEA.git

`cd C:\Users\valen\Documents\Workspace\UABEA\UABEAvalonia\bin\Debug\net6.0`

`UABEAvalonia.exe batchexportbundle C:\Users\valen\AppData\Local\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Data`

`UABEAvalonia.exe batchexportbundle C:\Users\valen\AppData\Local\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map`

Generate python from datas :

`poetry run python scripts/generator/generate_python_from_datas.py`

## Mitm

- Launch redirect.py from https://github.com/Valentin-alix/Mitm-Http.git
- Create localhost proxy at port 8080
- `poetry run python main.py`
