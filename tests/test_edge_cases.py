"""Extra adversarial checks found during the all-controls click audit."""
import ctypes
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import windows_launcher
from command_catalog import BY_ID, COMMANDS, build_argv, validate_file_target, validate_report_target
from temp_cleaner import scan_aged_files, remove_selected, _is_expected_user_temp_path


class DriveAndCommandEdgeTests(unittest.TestCase):
    def test_drive_enumeration_empty_is_not_a_fake_c_drive(self):
        kernel=Mock()
        kernel.GetLogicalDrives.return_value=0
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(kernel32=kernel), create=True):
            self.assertEqual(windows_launcher.available_drives(), [])

    def test_drive_enumeration_excludes_network_and_optical(self):
        kernel=Mock()
        # C: fixed, D: optical, E: removable, F: network.
        kernel.GetLogicalDrives.return_value=sum(1 << i for i in (2,3,4,5))
        kernel.GetDriveTypeW.side_effect=lambda path: {'C:\\':3,'D:\\':5,'E:\\':2,'F:\\':4}[path]
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(kernel32=kernel), create=True):
            self.assertEqual(windows_launcher.available_drives(), ['C:','E:'])

    def test_drive_discovery_error_is_not_a_fake_drive(self):
        kernel=Mock()
        kernel.GetLogicalDrives.side_effect=OSError('access denied')
        with patch.object(windows_launcher.os, 'name', 'nt'), \
             patch.object(windows_launcher.ctypes, 'windll', Mock(kernel32=kernel), create=True):
            self.assertEqual(windows_launcher.available_drives(), [])

    def test_non_windows_execution_rejected_even_for_gui(self):
        with patch.object(windows_launcher.os, 'name', 'posix'):
            with self.assertRaises(RuntimeError):
                windows_launcher.launch(BY_ID['boot.devices'])

    def test_nonexistent_sfc_path_never_launches(self):
        shell=Mock()
        with patch.object(windows_launcher.os,'name','nt'), \
             patch.object(windows_launcher.ctypes,'windll',Mock(shell32=shell),create=True), \
             patch.object(windows_launcher.Path,'is_file',return_value=False):
            with self.assertRaises(FileNotFoundError):
                windows_launcher.launch(BY_ID['sfc.file'],file_target=r'C:\Windows\System32\not-here.dll')
            shell.ShellExecuteW.assert_not_called()

    def test_power_reports_are_file_changing_operations(self):
        for key in ('power.battery','power.energy','power.sleepstudy'):
            with self.subTest(key=key):
                self.assertEqual(BY_ID[key].risk,'change')
                self.assertTrue(BY_ID[key].needs_report)

    def test_all_73_have_precise_kind_and_admin_classification(self):
        self.assertEqual(len(COMMANDS),73)
        for c in COMMANDS:
            with self.subTest(id=c.id):
                self.assertIn(c.kind,('native','powershell','slmgr','gui','shell'))
                self.assertIn(c.risk,('read','change','heavy'))
                self.assertFalse(c.needs_file and c.needs_report)
                self.assertTrue(c.description.strip() and c.notes.strip() and c.best_for.strip())

    def test_missing_user_pickers_are_rejected_instead_of_silent_run(self):
        for c in COMMANDS:
            if not (c.needs_file or c.needs_report): continue
            with self.subTest(id=c.id):
                with self.assertRaises(ValueError): build_argv(c)

    def test_unicode_spaced_report_path_is_preserved(self):
        target=r'C:\Users\Dimitris\Αναφορές\battery health test.html'
        self.assertEqual(validate_report_target(target),target)
        self.assertEqual(build_argv(BY_ID['power.battery'],report_target=target)[-1],target)

    def test_known_cmd_expansion_characters_rejected(self):
        for bad in ('%', '!', '^', '&', '|', '<', '>', '"', '\r', '\n'):
            with self.subTest(char=repr(bad)):
                with self.assertRaises(ValueError): validate_file_target('C:\\temp\\bad'+bad+'.dll')
                with self.assertRaises(ValueError): validate_report_target('C:\\temp\\bad'+bad+'.html')


class TempAbuseTests(unittest.TestCase):
    def setUp(self):
        # Exercise scan/deletion logic only inside disposable test directories.
        # Windows CI's TEMP location need not be %LOCALAPPDATA%\Temp.
        # The production root policy is tested independently above.
        validator = patch(
            'temp_cleaner._validate_temp_root',
            side_effect=lambda root: os.path.normcase(os.path.abspath(root)),
        )
        validator.start()
        self.addCleanup(validator.stop)

    def test_traversal_outside_temp_path_rejected(self):
        local=r'C:\Users\Tester\AppData\Local'
        self.assertFalse(_is_expected_user_temp_path(local+r'\Temp\..\Documents',local))

    def test_invalid_age_and_limit_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for d in (0,-1,366):
                with self.subTest(age=d), self.assertRaises(ValueError):scan_aged_files(tmp,d)
            for limit in (0,-1,3001):
                with self.subTest(limit=limit), self.assertRaises(ValueError):scan_aged_files(tmp,7,limit)

    def test_selected_file_that_becomes_new_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'target.tmp';p.write_text('same size')
            stamp=time.time()-20*86400;os.utime(p,(stamp,stamp))
            item=scan_aged_files(tmp,7).files[0]
            os.utime(p,None)
            self.assertEqual(remove_selected(tmp,[item],7),(0,0,1))
            self.assertTrue(p.exists())

    def test_old_directory_never_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested=Path(tmp)/'empty-old-directory';nested.mkdir()
            old=time.time()-40*86400;os.utime(nested,(old,old))
            self.assertEqual(scan_aged_files(tmp,7).eligible_files,0)
            self.assertTrue(nested.exists())

    def test_300_file_preview_limit_not_conflated_with_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=time.time()-30*86400
            for i in range(325):
                p=root/f'temp{i}.tmp';p.write_bytes(b'x');os.utime(p,(old,old))
            result=scan_aged_files(tmp,7)
            self.assertEqual(result.eligible_files,325)
            self.assertEqual(len(result.files),300)
            self.assertEqual(result.eligible_bytes,325)


if __name__=='__main__':unittest.main()