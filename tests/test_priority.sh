#!/bin/bash
cd "$(dirname "$0")/.."
echo "exit" | uv run src/main.py --config config.xml --vfs OVERRIDDEN_VFS.tar