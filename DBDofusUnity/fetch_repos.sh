git subtree pull --prefix=UABEA https://github.com/Valentin-alix/UABEA.git master --squash

git submodule init
git submodule foreach '
  branch=$(git config -f $toplevel/.gitmodules submodule.$name.branch || echo main)
  git fetch origin $branch
  git checkout $branch || git checkout -b $branch origin/$branch
  git pull --ff-only
'
git submodule update --remote --merge