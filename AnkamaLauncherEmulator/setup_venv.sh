#!/bin/bash

VENV_PATH=".venv"

if [ -f "$VENV_PATH/Scripts/activate" ]; then
    ACTIVATE_FILE="$VENV_PATH/Scripts/activate"
else
    ACTIVATE_FILE="$VENV_PATH/bin/activate"
fi

if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
    PATH_SEPARATOR=";"
else
    PATH_SEPARATOR=":"
fi

LINE="export PYTHONPATH=\".\""

if ! grep -Fxq "$LINE" "$ACTIVATE_FILE"; then
    echo "$LINE" >> "$ACTIVATE_FILE"
    echo "PYTHONPATH added to $ACTIVATE_FILE"
else
    echo "PYTHONPATH already in $ACTIVATE_FILE"
fi