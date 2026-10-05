#!/bin/bash
cd "$(dirname "$0")/.."
echo "exit" | uv run src/main.py --vfs cli_vfs.tar --log cli_log.json --script cli_script.txt