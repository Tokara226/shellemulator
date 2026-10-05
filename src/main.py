import sys
import argparse
import xml.etree.ElementTree as ET
import getpass
import socket
import shlex
import json
import datetime
import os
import csv


class VirtualFileSystem:
    def __init__(self):
        '''Дерево хранится исключительно в памяти'''
        self.fs = {"/": {"type": "dir", "children": set()}}
        self.cwd = "/"

    def load(self, csv_path):
        if not csv_path or not os.path.exists(csv_path):
            print(f"Ошибка загрузки VFS: файл '{csv_path}' не найден.")
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Пропускаем заголовок
                for row in reader:
                    if len(row) < 2:
                        print("Ошибка загрузки VFS: неверный формат CSV (недостаточно столбцов).")
                        return False
                    path = row[0]
                    ftype = row[1]
                    content = row[2] if len(row) > 2 else ""
                    self.add_to_tree(path, ftype, content)
            return True
        except Exception as e:
            print(f"Ошибка загрузки VFS: неверный формат ({e}).")
            return False

    def add_to_tree(self, path, ftype, content):
        if not path.startswith("/"): path = "/" + path
        path = path.rstrip("/") if path != "/" else "/"
        self.fs[path] = {"type": ftype, "content": content}

        '''Cвязываем с родительской папкой'''
        if path != "/":
            parent = os.path.dirname(path)
            if parent not in self.fs:
                self.add_to_tree(parent, "dir", "")
            if "children" not in self.fs[parent]:
                self.fs[parent]["children"] = set()
            self.fs[parent]["children"].add(os.path.basename(path))

    def _resolve_path(self, path):
        if path.startswith("/"):
            target = path
        else:
            target = os.path.join(self.cwd, path)
        return os.path.normpath(target).replace("\\", "/")

    def ls(self, args):
        target = self.cwd
        if args:
            target = self._resolve_path(args[0])

        if target not in self.fs:
            print(f"ls: {args[0] if args else ''}: Нет такого файла или каталога")
            return False

        node = self.fs[target]
        if node["type"] == "file":
            print(os.path.basename(target))
        else:
            children = node.get("children", set())
            if children:
                print(" ".join(sorted(children)))
        return True

    def cd(self, args):
        if not args or args[0] == "~":
            self.cwd = "/"
            return True

        target = self._resolve_path(args[0])
        if target not in self.fs:
            print(f"cd: {args[0]}: Нет такого файла или каталога")
            return False
        if self.fs[target]["type"] != "dir":
            print(f"cd: {args[0]}: Не каталог")
            return False

        self.cwd = target
        return True


def load_configuration():
    parser = argparse.ArgumentParser(description="UNIX Shell Emulator")
    parser.add_argument('--config', type=str, help='Путь к конфигурационному файлу XML')
    parser.add_argument('--vfs', type=str, help='Путь к физическому расположению VFS')
    parser.add_argument('--log', type=str, help='Путь к лог-файлу JSON')
    parser.add_argument('--script', type=str, help='Путь к стартовому скрипту')

    args = parser.parse_args()

    config = {'vfs_path': None, 'log_path': None, 'script_path': None}

    if args.config:
        try:
            tree = ET.parse(args.config)
            root = tree.getroot()
            vfs_node, log_node, script_node = root.find('vfs_path'), root.find('log_path'), root.find('script_path')

            if vfs_node is not None:
                config['vfs_path'] = vfs_node.text
            if log_node is not None:
                config['log_path'] = log_node.text
            if script_node is not None:
                config['script_path'] = script_node.text
        except Exception as e:
            print(f"Ошибка чтения конфигурационного файла: {e}")
            sys.exit(1)

    if args.vfs: config['vfs_path'] = args.vfs
    if args.log: config['log_path'] = args.log
    if args.script: config['script_path'] = args.script

    return config


def get_prompt():
    username, hostname = getpass.getuser(), socket.gethostname()
    if hostname.endswith('.local'): hostname = hostname[:-6]
    return f"{username}@{hostname}:~$ "


def log_event(log_path, command, error_message=None):
    if not log_path: return
    event = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "command": command,
             "error": error_message}
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass
    logs.append(event)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)


def process_command(command_line, log_path, vfs):
    if not command_line.strip():
        return True

    try:
        args = shlex.split(command_line)
    except ValueError as e:
        error_msg = "Ошибка: обнаружена незакрытая кавычка."
        print(error_msg)
        log_event(log_path, command_line, error_message=error_msg)
        return False

    if not args:
        return True

    cmd, cmd_args = args[0], args[1:]

    if cmd == "exit":
        log_event(log_path, command_line)
        sys.exit(0)
    elif cmd == "ls":
        success = vfs.ls(cmd_args)
        log_event(log_path, command_line, error_message=None if success else "Ошибка выполнения ls")
        return success
    elif cmd == "cd":
        success = vfs.cd(cmd_args)
        log_event(log_path, command_line, error_message=None if success else "Ошибка выполнения cd")
        return success
    else:
        error_msg = f"{cmd}: команда не найдена"
        print(error_msg)
        log_event(log_path, command_line, error_message=error_msg)
        return False


def run_startup_script(script_path, log_path, prompt, vfs):
    if not script_path or not os.path.exists(script_path):
        return

    print("=== Стартовый скрипт ===")
    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            cmd = line.strip()
            if not cmd: continue

            print(f"{prompt}{cmd}")
            success = process_command(cmd, log_path, vfs)

            if not success:
                print(f"Скрипт остановлен из-за ошибки")
                break


def main():
    config = load_configuration()

    print(f"VFS Path:    {config.get('vfs_path')}")
    print(f"Log Path:    {config.get('log_path')}")
    print(f"Script Path: {config.get('script_path')}")

    vfs_path = config.get('vfs_path')
    vfs = VirtualFileSystem()

    if not vfs.load(vfs_path):
        sys.exit(1)

    prompt = get_prompt()
    log_path = config.get('log_path')
    script_path = config.get('script_path')

    run_startup_script(script_path, log_path, prompt, vfs)

    while True:
        try:
            cmd = input(prompt)
            process_command(cmd, log_path, vfs)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue
        except SystemExit:
            break


if __name__ == "__main__":
    main()