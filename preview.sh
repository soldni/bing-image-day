#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python "${SCRIPT_DIR}/deploy.py" && python -m http.server 8000 --directory "${SCRIPT_DIR}/docs" --bind localhost
