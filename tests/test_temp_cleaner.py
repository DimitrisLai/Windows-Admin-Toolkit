import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from temp_cleaner import scan_aged_files, remove_selected, _is_expected_user_temp_path


class TempPathPolicyTests(unittest.TestCase):
    def test_only_user_appdata_temp_is_accepted(self):
        local = r'C:\Users\Tester\AppData\Local'
        good = (r'C:\Users\Tester\AppData\Local\Temp',
                r'C:\Users\Tester\AppData\Local\Temp\1')
        unsafe = (r'C:\Users\Tester\Documents',
                  r'C:\Users\Tester\AppData\Local\TempBackup',
                  r'C:\Windows\Temp',
                  r'D:\Temp',
                  r'C:\Users\Another\AppData\Local\Temp')
        for path in good:
            with self.subTest(path=path):
                self.assertTrue(_is_expected_user_temp_path(path, local))
        for path in unsafe:
            with self.subTest(path=path):
                self.assertFalse(_is_expected_user_temp_path(path, local))

    def test_missing_localappdata_is_rejected(self):
        self.assertFalse(_is_expected_user_temp_path(r'C:\Temp', None))


class TempCleanerTests(unittest.TestCase):
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

    def test_preview_does_not_delete_or_select_automatically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / 'old.temp'
            old.write_bytes(b'x' * 256)
            t = time.time() - 15 * 86400
            os.utime(old, (t, t))
            fresh = root / 'fresh.tmp'
            fresh.write_bytes(b'y' * 100)
            results = scan_aged_files(tmp, 7)
            self.assertEqual(results.eligible_files, 1)
            self.assertEqual(results.eligible_bytes, 256)
            self.assertTrue(old.is_file())
            self.assertTrue(fresh.is_file())
            self.assertEqual(results.files[0].path, str(old))

    def test_only_explicitly_selected_old_files_are_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / 'old.tmp'
            old.write_bytes(b'x' * 12)
            another = root / 'other.tmp'
            another.write_bytes(b'abc')
            t = time.time() - 10 * 86400
            os.utime(old, (t, t))
            os.utime(another, (t, t))
            results = scan_aged_files(tmp, 7)
            entry = next(c for c in results.files if c.path == str(old))
            count, size, skipped = remove_selected(tmp, [entry], 7)
            self.assertEqual((count, size, skipped), (1, 12, 0))
            self.assertFalse(old.exists())
            self.assertTrue(another.exists())

    def test_changed_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'keep.tmp'
            target.write_bytes(b'old data')
            t = time.time() - 20 * 86400
            os.utime(target, (t, t))
            entry = scan_aged_files(tmp, 7).files[0]
            target.write_bytes(b'changed contents')
            self.assertEqual(remove_selected(tmp, [entry], 7), (0, 0, 1))
            self.assertTrue(target.is_file())

    def test_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as external:
            target = Path(external) / 'important.txt'
            target.write_text('IMPORTANT')
            t = time.time() - 30 * 86400
            os.utime(target, (t, t))
            link = Path(tmp) / 'junction'
            try:
                link.symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Symlinks not supported in this test environment')
            self.assertEqual(scan_aged_files(tmp, 7).eligible_files, 0)
            self.assertEqual(target.read_text(), 'IMPORTANT')


if __name__ == '__main__':
    unittest.main()