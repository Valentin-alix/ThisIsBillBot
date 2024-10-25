git subtree pull --prefix=IL2CppExtract https://github.com/Valentin-alix/IL2CppExtract.git main --squash
git subtree pull --prefix=protodec https://github.com/Valentin-alix/protodec.git master --squash

git submodule init
git submodule foreach '
  branch=$(git config -f $toplevel/.gitmodules submodule.$name.branch || echo main)
  git fetch origin $branch
  git checkout $branch || git checkout -b $branch origin/$branch
  git pull --ff-only
'
git submodule update --remote --merge