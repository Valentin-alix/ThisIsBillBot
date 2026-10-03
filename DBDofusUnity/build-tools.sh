#!/usr/bin/env bash
# run with Git Bash on Windows; requires .NET 10 and Visual Studio C++ tools (v145).
set -euo pipefail

case "$(uname -s)" in
    MINGW*|MSYS*) ;;
    *) echo "This script requires Git Bash on Windows." >&2; exit 1 ;;
esac

cd "$(dirname "${BASH_SOURCE[0]}")/.."
command -v dotnet >/dev/null
vswhere='/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
msbuild=$("$vswhere" -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find 'MSBuild\**\Bin\MSBuild.exe' | tr -d '\r' | head -n 1)
[[ -n "$msbuild" ]] || { echo "Install Visual Studio with C++ build tools." >&2; exit 1; }

dependency_commit=bc15122ddd4cec81977fa99167c513df260a9410
dependencies=(
    Libs/AssetsTools.NET.dll
    Libs/AssetsTools.NET.Cpp2IL.dll
    Libs/AssetsTools.NET.MonoCecil.dll
    Libs/AssetsTools.NET.Texture.dll
    TexToolWrap/PVRTexLib/Windows_x86_32/PVRTexLib.dll
    TexToolWrap/PVRTexLib/Windows_x86_64/PVRTexLib.dll
    TexToolWrap/crunch/win32/crnlib.dll
    TexToolWrap/crunch/win64/crnlib.dll
    TexToolWrap/ispc/win32/ispc_texcomp.dll
    TexToolWrap/ispc/win64/ispc_texcomp.dll
)
for dependency in "${dependencies[@]}"; do
    path="DBDofusUnity/UABEA/$dependency"
    if [[ ! -s "$path" ]] || git lfs pointer --check --file="$path" >/dev/null 2>&1; then
        mkdir -p "$(dirname "$path")"
        git show "$dependency_commit:$path" | GIT_LFS_SKIP_SMUDGE=0 git lfs smudge > "$path.tmp"
        if git lfs pointer --check --file="$path.tmp" >/dev/null 2>&1; then
            rm -f "$path.tmp"
            echo "Failed to download $path" >&2
            exit 1
        fi
        mv "$path.tmp" "$path"
    fi
done

MSYS_NO_PATHCONV=1 "$msbuild" DBDofusUnity/UABEA/UABEAvalonia.sln \
    /restore /p:Configuration=Debug /p:UseSharedCompilation=false /m:1 /nr:false /verbosity:minimal
dotnet build DBDofusUnity/Il2CppInspectorRedux/Il2CppInspector.CLI/Il2CppInspector.CLI.csproj \
    --configuration Debug -p:UseSharedCompilation=false --verbosity minimal
dotnet build DBDofusUnity/protodec/src/protodec/protodec.csproj \
    --configuration Debug -p:UseSharedCompilation=false --verbosity minimal

for executable in \
    DBDofusUnity/UABEA/UABEAvalonia/bin/Debug/net6.0/UABEAvalonia.exe \
    DBDofusUnity/Il2CppInspectorRedux/Il2CppInspector.CLI/bin/Debug/net10.0/win-x64/Il2CppInspector.exe \
    DBDofusUnity/protodec/bin/protodec/Debug/net10.0/protodec.exe; do
    [[ -s "$executable" ]] || { echo "Missing build output: $executable" >&2; exit 1; }
done
echo 'UABEA, Il2CppInspector and protodec built successfully.'
