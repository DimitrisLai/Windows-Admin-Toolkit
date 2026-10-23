"""Regression tests for the v2.4.5 Expert Mode launch-notice switch.

These test the real command dispatch method with mocked Windows launches;
they do not execute commands or require a graphical desktop.
"""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import AdminToolkit
from command_catalog import BY_ID


def fake_window(*, expert=False, command_id='sys.info'):
    return SimpleNamespace(
        current=BY_ID[command_id],
        drives=['C:'],
        drive_var=SimpleNamespace(get=lambda: 'C:'),
        host_var=SimpleNamespace(get=lambda: 'www.microsoft.com'),
        port_var=SimpleNamespace(get=lambda: '443'),
        expert_var=SimpleNamespace(get=lambda: expert),
        selected_file=None,
        selected_report=None,
        status_var=Mock(),
        _validate_network_before_action=lambda command: True,
    )


class ExpertModeTests(unittest.TestCase):
    def test_normal_mode_still_shows_post_launch_notice(self):
        window = fake_window(expert=False)
        with patch('app.os.name', 'nt'), patch('app.launch') as launch, \
             patch('app.messagebox.showinfo') as info:
            AdminToolkit._run(window)
        launch.assert_called_once()
        info.assert_called_once()
        self.assertEqual(info.call_args.args[0], 'Launch requested')
        self.assertIn('Command launched', window.status_var.set.call_args.args[0])

    def test_expert_mode_hides_only_successful_launch_notice(self):
        window = fake_window(expert=True)
        with patch('app.os.name', 'nt'), patch('app.launch') as launch, \
             patch('app.messagebox.showinfo') as info:
            AdminToolkit._run(window)
        launch.assert_called_once()
        info.assert_not_called()
        self.assertIn('Command launched', window.status_var.set.call_args.args[0])

    def test_expert_mode_preserves_danger_confirmation_and_cancellation(self):
        window = fake_window(expert=True, command_id='net.winsock')
        self.assertNotEqual(window.current.risk, 'read')
        with patch('app.os.name', 'nt'), \
             patch('app.messagebox.askyesno', return_value=False) as confirm, \
             patch('app.launch') as launch, patch('app.messagebox.showinfo') as info:
            AdminToolkit._run(window)
        confirm.assert_called_once()
        launch.assert_not_called()
        info.assert_not_called()

        with patch('app.os.name', 'nt'), \
             patch('app.messagebox.askyesno', return_value=True) as confirm, \
             patch('app.launch') as launch, patch('app.messagebox.showinfo') as info:
            AdminToolkit._run(window)
        confirm.assert_called_once()
        launch.assert_called_once()
        info.assert_not_called()

    def test_failed_launch_still_shows_error_in_both_modes(self):
        for expert in (False, True):
            with self.subTest(expert=expert):
                window = fake_window(expert=expert)
                with patch('app.os.name', 'nt'), \
                     patch('app.launch', side_effect=OSError('UAC declined')), \
                     patch('app.messagebox.showinfo') as info, \
                     patch('app.messagebox.showerror') as error:
                    AdminToolkit._run(window)
                info.assert_not_called()
                error.assert_called_once()
                self.assertEqual(error.call_args.args[0], 'Command not launched')
                self.assertEqual(window.status_var.set.call_args.args[0], 'Launch failed or canceled')

    def test_non_windows_notice_remains_visible_in_expert_mode(self):
        window = fake_window(expert=True)
        with patch('app.os.name', 'posix'), patch('app.launch') as launch, \
             patch('app.messagebox.showinfo') as info:
            AdminToolkit._run(window)
        launch.assert_not_called()
        info.assert_called_once()
        self.assertEqual(info.call_args.args[0], 'Windows required')


if __name__ == '__main__':
    unittest.main()
