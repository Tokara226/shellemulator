import os
import socket
import sys
import shlex

def get_prompt() -> str:
    user = os.getlogin()
    host = socket.gethostname()
    return f"{user}@{host}:~$ "

def process_command(user_input: str) -> None:
    try:
        parts = shlex.split(user_input.strip())
    except ValueError:
        print("Ошибка")
        return

    if not parts:
        return

    command = parts[0]
    args = parts[1:]

    if command == "exit":
        sys.exit(0)
    elif command in ("ls", "cd"):
        print(f"{command} {' '.join(args)}" if args else command)
    else:
        print(f"{command}: команда не найдена")

def main() -> None:
    prompt = get_prompt()
    while True:
        try:
            user_input = input(prompt)
            process_command(user_input)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue

if __name__ == "__main__":
    main()