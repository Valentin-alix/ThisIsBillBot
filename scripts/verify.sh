uv run ruff format .
uv run ruff check . --fix
uv run pyright
uv run coverage run --source=src -m unittest discover -s tests && uv run coverage report -m --fail-under=90