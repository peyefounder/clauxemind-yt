#!/usr/bin/env bash
# CLAUXEMIND-YT — Launcher script
# Makes it easy to start from anywhere

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${SCRIPT_DIR}/venv/bin/python3"

# Check if venv exists, if not create it
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    echo "Setting up CLAUXEMIND-YT..."
    python3 -m venv "${SCRIPT_DIR}/venv" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to create venv. Using system python3."
        PYTHON="python3"
    fi
fi

# Run the Python script
exec ${PYTHON} "${SCRIPT_DIR}/clauxemind-yt.py" "$@"
