import unittest
from command_catalog import (
    COMMANDS, BY_ID, build_argv, display_command,
    validate_drive, validate_file_target, validate_report_target, categories,
)
from windows_launcher import available_drives


class CommandCatalogTests(unittest.TestCase):
    def test_unique_ids(self):
        self.assertEqual(len(COMMANDS), len(BY_ID))
        self.assertEqual(len(COMMANDS), 73)
        self.assertTrue(all(c.description and c.best_for and c.notes for c in COMMANDS))
        self.assertTrue(all(c.risk in ('read', 'change', 'heavy') for c in COMMANDS))

    def test_drive_substitution(self):
        cmd = BY_ID['disk.recover']
        self.assertEqual(build_argv(cmd, 'd:'), ['chkdsk.exe', 'D:', '/f', '/r'])
        self.assertIn('D:', display_command(cmd, 'd:'))
        self.assertEqual(build_argv(BY_ID['disk.volumes'], 'e:')[-1].split()[2], 'E')

    def test_invalid_drive_rejected(self):
        for text in ('C: & del /s', 'C:/', 'CC:', '', '1:', 'C:\\'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    validate_drive(text)

    def test_drive_ignored_for_non_drive_commands(self):
        self.assertEqual(build_argv(BY_ID['sfc.scan'], 'INVALID'), ['sfc.exe', '/scannow'])

    def test_sfc_file_requires_target(self):
        with self.assertRaises(ValueError):
            build_argv(BY_ID['sfc.file'])
        self.assertEqual(build_argv(BY_ID['sfc.file'], file_target=r'C:\Windows\System32\abc.dll'),
                         ['sfc.exe', r'/scanfile=C:\Windows\System32\abc.dll'])

    def test_file_path_injection_rejected(self):
        for path in [r'C:\foo&whoami.txt', r'C:\foo%COMSPEC%.dll',
                     r'C:\foo!dll', r'C:\foo|cmd.dll', r'\\server\a.dll',
                     r'foo.dll', r'C:\foo"bar.dll']:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    validate_file_target(path)

    def test_no_obsolete_wmic(self):
        self.assertFalse(any('wmic' in c.label.lower() for c in COMMANDS))
        self.assertEqual(build_argv(BY_ID['disk.health'])[0], 'powershell.exe')

    def test_static_command_has_no_shell(self):
        for cmd in COMMANDS:
            if cmd.needs_file or cmd.needs_report:
                continue
            args = build_argv(cmd, 'C:')
            self.assertTrue(args[0].lower().endswith(('.exe', '.msc')) or args[0].startswith('ms-settings:'))
            self.assertNotIn('wmic.exe', args)

    def test_categories(self):
        self.assertIn('Disk & storage', categories())
        self.assertIn('Windows files', categories())

    def test_expansion_is_complete(self):
        groups = {'RAM & performance': 5, 'Temporary files': 7, 'Startup & drivers': 4, 'Power & battery': 5}
        for category, minimum in groups.items():
            with self.subTest(category=category):
                self.assertGreaterEqual(sum(1 for c in COMMANDS if c.category == category), minimum)
        self.assertEqual(len({c.id for c in COMMANDS}), 73)
        self.assertTrue(all(c.doc_url.startswith('https://') for c in COMMANDS if c.doc_url))

    def test_drive_rules_every_entry(self):
        for c in COMMANDS:
            with self.subTest(id=c.id):
                self.assertEqual(c.uses_drive, '{drive}' in str(c.args) or '{drive_letter}' in str(c.args))
                if c.needs_report:
                    self.assertTrue('{report}' in str(c.args))
                    continue
                if c.needs_file:
                    continue
                argv = build_argv(c, 'D:')
                self.assertTrue(argv and isinstance(argv[0], str))
                if c.uses_drive:
                    self.assertTrue('D:' in ' '.join(argv) or 'D' in argv or '-DriveLetter D' in ' '.join(argv))
                self.assertFalse(any('{drive}' in x or '{report}' in x for x in argv))

    def test_report_save_paths(self):
        target = r'C:\Users\Public\battery report.html'
        self.assertEqual(validate_report_target(target), target)
        self.assertEqual(build_argv(BY_ID['power.battery'], report_target=target),
                         ['powercfg.exe', '/batteryreport', '/output', target])
        self.assertIn('/duration 60', display_command(BY_ID['power.energy'], report_target=target))
        for path in (r'C:\foo&bar.html', r'C:\foo%USER%.html', r'\\server\share\report.html',
                     'report.html', r'C:\notes.txt'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_report_target(path)
        with self.assertRaises(ValueError):
            build_argv(BY_ID['power.battery'])

    def test_uri_settings_and_temp_folder(self):
        self.assertEqual(build_argv(BY_ID['temp.storagesense']), ['ms-settings:storagepolicies'])
        self.assertEqual(BY_ID['temp.storagesense'].kind, 'shell')
        self.assertFalse(BY_ID['temp.folder'].uses_drive)
        self.assertEqual(build_argv(BY_ID['temp.cleanmgr'], 'E:'), ['cleanmgr.exe', '/d', 'E'])
        self.assertEqual(build_argv(BY_ID['disk.optimize'], 'D:'), ['defrag.exe', 'D:', '/O', '/V'])

    def test_nonwindows_fallback_drive(self):
        self.assertTrue(available_drives())


if __name__ == '__main__':
    unittest.main()
