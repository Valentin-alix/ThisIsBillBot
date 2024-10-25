git subtree pull --prefix=D3Mapping https://github.com/Valentin-alix/D3Mapping.git main --squash
git subtree pull --prefix=DBDofusUnity https://github.com/Valentin-alix/DBDofusUnity.git main --squash

git submodule init
git submodule foreach '
  branch=$(git config -f $toplevel/.gitmodules submodule.$name.branch || echo main)
  git fetch origin $branch
  git checkout $branch || git checkout -b $branch origin/$branch
  git pull --ff-only
'
git submodule update --remote --merge