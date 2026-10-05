import sys
import argparse
import xml.etree.ElementTree as ET
import getpass
import socket
import shlex
import json
import datetime
import os


def load_configuration():
    parser = argparse.ArgumentParser(description="UNIX Shell Emulator")
    parser.add_argument('--config', type=str, help='Путь к конфигурационному файлу XML')
    parser.add_argument('--vfs', type=str, help='Путь к физическому расположению VFS')
    parser.add_argument('--log', type=str, help='Путь к лог-файлу JSON')
    parser.add_argument('--script', type=str, help='Путь к стартовому скрипту')

    args = parser.parse_args()

    config = {
        'vfs_path': None,
        'log_path': None,
        'script_path': None
    }

    if args.config:
        try:
            tree = ET.parse(args.config)
            root = tree.getroot()

            vfs_node = root.find('vfs_path')
            log_node = root.find('log_path')
            script_node = root.find('script_path')

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
    username = getpass.getuser()
    hostname = socket.gethostname()

    if hostname.endswith('.local'):
        hostname = hostname[:-6]

    return f"{username}@{hostname}:~$ "


def log_event(log_path, command, error_message=None):
    if not log_path:
        return

    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "command": command,
        "error": error_message
    }

    logs = []
    '''Если файл уже существует'''
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            '''Если файл пустой или сломанный, начнем с чистого листа'''
            pass

    logs.append(event)

    '''Записываем обновленный массив'''
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)


def process_command(command_line, log_path):
    if not command_line.strip():
        return

    try:
        args = shlex.split(command_line)
    except ValueError as e:
        error_msg = "Ошибка: обнаружена незакрытая кавычка."
        print(error_msg)
        log_event(log_path, command_line, error_message=error_msg)
        return

    if not args:
        return

    cmd = args[0]

    if cmd == "exit":
        log_event(log_path, command_line)
        sys.exit(0)
    elif cmd in ["ls", "cd"]:
        print(" ".join(args))
        log_event(log_path, command_line)
    else:
        error_msg = f"{cmd}: команда не найдена"
        print(error_msg)
        log_event(log_path, command_line, error_message=error_msg)


def main():
    config = load_configuration()

    print(f"VFS Path:    {config.get('vfs_path')}")
    print(f"Log Path:    {config.get('log_path')}")
    print(f"Script Path: {config.get('script_path')}")

    prompt = get_prompt()
    log_path = config.get('log_path')

    while True:
        try:
            cmd = input(prompt)
            process_command(cmd, log_path)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue
        except SystemExit:
            break


if __name__ == "__main__":
    main()