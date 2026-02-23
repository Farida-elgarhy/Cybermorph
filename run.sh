#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
    cd "$SCRIPT_DIR"
    "$SCRIPT_DIR/venv/bin/pip" install -r requirements.txt
    "$SCRIPT_DIR/venv/bin/pip" install -e .
fi

source "$SCRIPT_DIR/venv/bin/activate"
cybermorph-auto "$@"
CYBERMORPH_EXIT_CODE=$?
deactivate
exit $CYBERMORPH_EXIT_CODE