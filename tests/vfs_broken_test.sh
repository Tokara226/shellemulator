#!/bin/bash
cd "$(dirname "$0")/.."
echo "Попытка загрузить несуществующий файл"
echo "exit" | uv run src/main.py --vfs tests/not_exist.csv
echo "Попытка загрузить сломанный CSV"
echo "exit" | uv run src/main.py --vfs tests/vfs_broken.cs v