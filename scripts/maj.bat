set UABEA_PATH_EXE="%USERPROFILE%\Documents\Workspace\UABEA\UABEAvalonia\bin\Debug\net6.0\UABEAvalonia.exe"

%UABEA_PATH_EXE% batchexportbundle %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map

%UABEA_PATH_EXE% batchexportbundle %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\aa\StandaloneWindows64

%UABEA_PATH_EXE% batchexportbundle %LOCALAPPDATA%\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Data

poetry run python scripts/generator/generate_proto_from_descriptor.py
poetry run python scripts/generator/generate_python_from_proto.py
poetry run python scripts/generator/generate_python_from_datas.py