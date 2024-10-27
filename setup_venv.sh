#!/bin/bash

VENV_PATH=$(poetry env info -p)

ACTIVATE_FILE="$VENV_PATH/Scripts/activate"

LINE='export PYTHONPATH=".;./D3Mapping;./D3Database;./DBDofusUnity"'

# add only once
if ! grep -Fxq "$LINE" "$ACTIVATE_FILE"; then
    echo "$LINE" >> "$ACTIVATE_FILE"
    echo "✅ PYTHONPATH ajouté dans $ACTIVATE_FILE"
else
    echo "ℹ️ PYTHONPATH déjà présent dans $ACTIVATE_FILE"
fi
