"""Regression tests for the nine original v1.2.0 beta additions."""
import unittest
from unittest.mock import Mock, patch
from command_catalog import (
    BY_ID, COMMANDS, build_argv, display_command,
    validate_network_host, validate_network_port,
)
import windows_launcher


class NewCommandsTests(unittest.TestCase):
    NINE = {
        'boot.pnp_problems', 'boot.pnp_drivers', 'net.adapters', 'net.test_connection',
        'diag.winget', 'power.sleepstudy', 'diag.group_policy', 'diag.wmi_verify', 'diag.whoami',
    }

    def test_beta_nine_retained_in_current_catalog(self):
        self.assertEqual(len(COMMANDS), 73)
        self.assertEqual(len({c.id for c in COMMANDS}), 69)
        self.assertTrue(self.NINE.issubset(BY_ID))

    def test_each_new_entry_has_credible_english_documentation(self):
        for key in self.NINE:
            with self.subTest(id=key):
                c = BY_ID[key]
                self.assertTrue(c.doc_url.startswith('https://learn.microsoft.com/'))
                for v in (c.label, c.description, c.best_for, c.notes):
                    self.assertGreater(len(v), 15 if v is not c.label else 5)
                self.assertFalse(c.uses_drive)

    def test_known_cli_commands_have_expected_arguments(self):
        self.assertEqual(build_argv(BY_ID['boot.pnp_problems']), ['pnputil.exe','/enum-devices','/problem'])
        self.assertEqual(build_argv(BY_ID['boot.pnp_drivers']), ['pnputil.exe','/enum-drivers'])
        self.assertEqual(build_argv(BY_ID['diag.winget']), ['winget.exe','upgrade'])
        self.assertEqual(build_argv(BY_ID['diag.group_policy']), ['gpresult.exe','/r'])
        self.assertEqual(build_argv(BY_ID['diag.wmi_verify']), ['winmgmt.exe','/verifyrepository'])
        self.assertEqual(build_argv(BY_ID['diag.whoami']), ['whoami.exe','/all'])

    def test_powershell_cmdlets_target_correct_purpose(self):
        self.assertIn('Get-NetAdapter', build_argv(BY_ID['net.adapters'])[-1])
        a=build_argv(BY_ID['net.test_connection'], host_target='router.local', port_target='8443')
        self.assertEqual(a[0], 'powershell.exe')
        self.assertIn('-ComputerName router.local -Port 8443', a[-1])
        self.assertIn('router.local', display_command(BY_ID['net.test_connection'],host_target='router.local'))

    def test_network_host_validation_good(self):
        for value in ('server', 'server.example.com', '192.0.2.1', '2001:db8::1', 'a-b.example'):
            with self.subTest(value=value):
                self.assertTrue(validate_network_host(value))

    def test_network_host_validation_bad_and_injection(self):
        for value in ('', ' host', 'host ', 'https://example.com', 'x; calc',
                      "x' -Command evil", 'x$(whoami)', 'x|cat', 'x`calc', 'x&calc',
                      'a..b', '-evil', 'evil\nnew', 'user@host', 'a'*254):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_network_host(value)

    def test_network_port_valid_invalid(self):
        for v in ('1','443','65535',8443):
            self.assertTrue(1 <= validate_network_port(v) <= 65535)
        for v in ('0','65536','80;whoami','-1','1.2','',None, '999999'):
            with self.subTest(port=v), self.assertRaises(ValueError):
                validate_network_port(v)

    def test_invalid_host_or_port_rejected_before_launch(self):
        shell = Mock()
        with patch.object(windows_launcher.os,'name','nt'), \
             patch.object(windows_launcher.ctypes,'windll',Mock(shell32=shell),create=True):
            with self.assertRaises(ValueError):
                windows_launcher.launch(BY_ID['net.test_connection'],host_target='test;evil')
            with self.assertRaises(ValueError):
                windows_launcher.launch(BY_ID['net.test_connection'],port_target='70000')
            shell.ShellExecuteW.assert_not_called()

    def test_sleepstudy_requires_html_destination_and_confirmation(self):
        c=BY_ID['power.sleepstudy']
        self.assertTrue(c.needs_report and c.admin and c.risk=='change')
        with self.assertRaises(ValueError): build_argv(c)
        a=build_argv(c,report_target=r'C:\Users\Public\Sleep Report.html')
        self.assertEqual(a, ['powercfg.exe','/sleepstudy','/output',r'C:\Users\Public\Sleep Report.html'])

    def test_other_eight_are_inspections(self):
        for key in self.NINE - {'power.sleepstudy'}:
            self.assertEqual(BY_ID[key].risk,'read')

    def test_no_new_commands_write_arbitrary_script(self):
        for key in self.NINE:
            c=BY_ID[key]
            argv=build_argv(c,report_target=r'C:\Public\test.html')
            self.assertFalse(any('Invoke-Expression' in a or 'Start-Process' in a for a in argv))


if __name__=='__main__':
    unittest.main()
