import unittest
from unittest.mock import Mock, patch
import windows_launcher
from command_catalog import BY_ID, COMMANDS


class LaunchTests(unittest.TestCase):
    def test_admin_launch_command_args_with_fake_windows_shell(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 33
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher, 'available_drives', return_value=['C:', 'D:']), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            windows_launcher.launch(BY_ID['disk.fix'], drive='D:')
        call = shell.ShellExecuteW.call_args.args
        self.assertEqual(call[1], 'runas')
        self.assertEqual(call[2], 'cmd.exe')
        self.assertIn('D: /f', call[3])
        self.assertNotIn('C: /f', call[3])

    def test_shell_execute_uses_pointer_sized_return_type(self):
        import ctypes
        shell = Mock()
        shell.ShellExecuteW.return_value = 33
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            windows_launcher.launch(BY_ID['sys.info'])
        self.assertIs(shell.ShellExecuteW.restype, ctypes.c_void_p)

    def test_gui_uses_open_without_elevation(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 40
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            windows_launcher.launch(BY_ID['diag.reliability'])
        call = shell.ShellExecuteW.call_args.args
        self.assertEqual(call[1:3], ('open', 'perfmon.exe'))


    def test_powershell_runs_direct_no_cmd_parsing(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 42
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            windows_launcher.launch(BY_ID['ram.modules'])
        call = shell.ShellExecuteW.call_args.args
        self.assertEqual(call[2], 'powershell.exe')
        self.assertIn('-NoExit', call[3])
        self.assertIn('Win32_PhysicalMemory', call[3])

    def test_storage_settings_shell_uri(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 42
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            windows_launcher.launch(BY_ID['temp.storagesense'])
        call = shell.ShellExecuteW.call_args.args
        self.assertEqual(call[2], 'ms-settings:storagepolicies')
        self.assertIsNone(call[3])

    def test_nonexistent_drive_rejected(self):
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher, 'available_drives', return_value=['C:']):
            with self.assertRaises(ValueError):
                windows_launcher.launch(BY_ID['disk.fix'], drive='D:')

    def test_every_catalog_entry_constructs_a_launch_request(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 33
        # A mocked end-to-end Windows launch test. Nothing is executed.
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher, 'available_drives', return_value=['C:', 'D:']), \
             patch.object(windows_launcher.Path, 'is_file', return_value=True), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            for command in COMMANDS:
                with self.subTest(command=command.id):
                    shell.ShellExecuteW.reset_mock()
                    windows_launcher.launch(command, drive='D:',
                        file_target=r'C:\Windows\System32\kernel32.dll',
                        report_target=r'C:\Users\Public\test-report.html')
                    args = shell.ShellExecuteW.call_args.args
                    self.assertEqual(args[1], 'runas' if command.admin else 'open')
                    self.assertTrue(args[2], 'No executable for ' + command.id)
                    if command.uses_drive:
                        self.assertIn('D', args[3])

    def test_zero_shell_execute_result_fails_cleanly(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = None
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            with self.assertRaises(OSError):
                windows_launcher.launch(BY_ID['net.winsock'])

    def test_windows_denial_does_not_report_success(self):
        shell = Mock()
        shell.ShellExecuteW.return_value = 5
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(shell32=shell), create=True):
            with self.assertRaises(OSError):
                windows_launcher.launch(BY_ID['net.winsock'])


if __name__ == '__main__':
    unittest.main()
