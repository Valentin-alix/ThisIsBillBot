git submodule update --init --recursive

git submodule foreach --recursive '
  branch=$(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master)
  git fetch origin $branch
  git checkout $branch || git checkout -b $branch origin/$branch
  git pull --ff-only
'

git submodule update --remote --merge --recursive