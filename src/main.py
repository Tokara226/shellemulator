import os
import socket
import sys
import shlex  # Подключаем модуль для умного парсинга командной строки

def get_prompt() -> str:
    """
    Формирует строку приглашения для эмулятора.
    """
    user = os.getlogin()
    host = socket.gethostname()
    return f"{user}@{host}:~$ "

def process_command(user_input: str) -> None:
    """
    Разбивает ввод на команду и аргументы, выполняет логику.
    """
    try:
        # shlex.split разбивает строку с учетом пробелов и кавычек
        parts = shlex.split(user_input.strip())
    except ValueError:
        # Если кавычка не закрыта, shlex выкинет ValueError
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
        print(f"{command}: неизвестная команда")

def main() -> None:
    """
    Запускает интерактивный цикл REPL приложения.
    """
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