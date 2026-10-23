"""v2.5.0 catalog completeness and safety regressions (no OS commands run)."""
import unittest
from pathlib import Path
from command_catalog import COMMANDS, BY_ID, build_argv, display_command, categories


ROOT = Path(__file__).resolve().parents[1]
NEW = {
    'net.firewall_profiles',
    'net.dns_servers',
    'diag.defender_detections',
    'diag.time_sync',
}


class V25CatalogTests(unittest.TestCase):
    def test_final_catalog_has_unique_seventy_three_commands(self):
        self.assertEqual(len(COMMANDS), 73)
        self.assertEqual(len(BY_ID), 73)
        self.assertEqual(len(categories()), 11)
        self.assertTrue(NEW.issubset(BY_ID))

    def test_new_diagnostics_are_inspection_only(self):
        for key in NEW:
            with self.subTest(key=key):
                c = BY_ID[key]
                self.assertEqual(c.risk, 'read')
                self.assertFalse(c.uses_drive or c.needs_file or c.needs_report or c.needs_network)
                self.assertEqual(c.restart, 'No')
                self.assertTrue(c.doc_url.startswith('https://learn.microsoft.com/'))
                self.assertTrue(all((c.label, c.description, c.best_for, c.notes)))
                self.assertNotIn('Set-', str(c.args))
                self.assertNotIn('Remove-', str(c.args))

    def test_exact_firewall_and_dns_cmdlets(self):
        firewall = build_argv(BY_ID['net.firewall_profiles'])
        dns = build_argv(BY_ID['net.dns_servers'])
        self.assertEqual(firewall[:3], ['powershell.exe','-NoProfile','-Command'])
        self.assertIn('Get-NetFirewallProfile -PolicyStore ActiveStore', firewall[-1])
        self.assertIn('Get-DnsClientServerAddress', dns[-1])

    def test_defender_and_time_queries_only(self):
        defender = build_argv(BY_ID['diag.defender_detections'])
        clock = build_argv(BY_ID['diag.time_sync'])
        self.assertIn('Get-MpThreatDetection', defender[-1])
        self.assertIn('Select-Object -First 20', defender[-1])
        self.assertEqual(clock, ['w32tm.exe','/query','/status'])
        self.assertTrue(BY_ID['diag.time_sync'].admin)

    def test_preview_matches_expected_literal_launch(self):
        for key in NEW:
            with self.subTest(key=key):
                c = BY_ID[key]
                self.assertIn(build_argv(c)[0], display_command(c))
                self.assertFalse(any('{host}' in a or '{drive}' in a for a in build_argv(c)))

    def test_reference_exactly_covers_catalog(self):
        doc = (ROOT / 'COMMAND_REFERENCE.md').read_text(encoding='utf-8')
        self.assertEqual(doc.count('### `'), len(COMMANDS))
        for c in COMMANDS:
            with self.subTest(key=c.id):
                self.assertEqual(doc.count('### `' + c.label + '`'), 1)
        self.assertIn('**Version:** 2.5.0', doc)

    def test_release_documents_have_correct_version_and_count(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        manual = (ROOT / 'USER_MANUAL.md').read_text(encoding='utf-8')
        self.assertIn('v2.5.0', readme)
        self.assertIn('73 curated', readme)
        self.assertIn('**Version 2.5.0**', manual)


if __name__ == '__main__':
    unittest.main()
