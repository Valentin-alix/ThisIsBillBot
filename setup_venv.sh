#!/bin/bash

VENV_PATH=".venv"

# détecte automatiquement le fichier d'activation selon le système
if [ -f "$VENV_PATH/Scripts/activate" ]; then
    ACTIVATE_FILE="$VENV_PATH/Scripts/activate"
elif [ -f "$VENV_PATH/bin/activate" ]; then
    ACTIVATE_FILE="$VENV_PATH/bin/activate"
else
    echo "❌ Fichier d'activation introuvable dans $VENV_PATH"
    exit 1
fi

# utilise le séparateur correct selon le système
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
    PATH_SEPARATOR=";"
else
    PATH_SEPARATOR=":"
fi

LINE="export PYTHONPATH=\".${PATH_SEPARATOR}./D3Mapping${PATH_SEPARATOR}./D3Database${PATH_SEPARATOR}./DBDofusUnity\""

# ajoute seulement si absent
if ! grep -Fxq "$LINE" "$ACTIVATE_FILE"; then
    echo "$LINE" >> "$ACTIVATE_FILE"
    echo "✅ PYTHONPATH ajouté dans $ACTIVATE_FILE"
else
    echo "ℹ️ PYTHONPATH déjà présent dans $ACTIVATE_FILE"
fi
