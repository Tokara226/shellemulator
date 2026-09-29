import unittest
import io
from unittest.mock import patch
from src.main import process_command


class TestEmulator(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_simple_command(self):
        process_command("ls")
        self.assertEqual(self.mock_stdout.getvalue().strip(), "ls")

    def test_command_with_args(self):
        process_command("cd UnityProjects")
        self.assertEqual(self.mock_stdout.getvalue().strip(), "cd UnityProjects")

    def test_command_with_quotes(self):
        process_command('ls "Active Ragdoll.cs"')
        self.assertEqual(self.mock_stdout.getvalue().strip(), "ls Active Ragdoll.cs")

    def test_unclosed_quote_error(self):
        process_command('cd "Grounded')
        self.assertEqual(self.mock_stdout.getvalue().strip(), "Ошибка")

    def test_unknown_command(self):
        process_command("git status")
        self.assertEqual(self.mock_stdout.getvalue().strip(), "git: команда не найдена")

    def test_empty_input(self):
        process_command("   ")
        self.assertEqual(self.mock_stdout.getvalue().strip(), "")


if __name__ == '__main__':
    unittest.main()