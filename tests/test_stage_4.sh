#!/bin/bash
cd "$(dirname "$0")/.."
echo "exit" | uv run src/main.py --config config.xml --script startup_stage_4.txt