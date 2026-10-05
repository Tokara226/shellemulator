#!/bin/bash
cd "$(dirname "$0")/.."
echo -e "ls\nexit" | uv run src/main.py --vfs tests/vfs_flat.csv