#!/bin/bash
cd "$(dirname "$0")"
uv run src/main.py --config config.xml --script cli_script.txt