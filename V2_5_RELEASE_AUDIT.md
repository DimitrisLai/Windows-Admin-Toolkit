# Windows Admin Toolkit v2.5.0 — Year-End Release Audit

**Date:** 23 October 2026  
**Scope:** Public beta source milestone, **73 built-in commands across 11 categories**  
**Status:** Release candidate under automated verification; final CI evidence to be recorded after successful branch tests.

## What changed

- Added four fixed, documented **read-only** entries:
  - Active Windows Firewall profiles (`Get-NetFirewallProfile -PolicyStore ActiveStore`)
  - Configured DNS servers (`Get-DnsClientServerAddress`)
  - Defender detection history (`Get-MpThreatDetection`, no removal or modification)
  - Windows Time synchronization status (`w32tm /query /status`, no resync)
- Preserved safety confirmations, Windows UAC, errors and separate command result windows with Expert Mode ON.
- Updated the GUI version and made its command count derive from the catalog instead of stale hardcoded text.
- Updated command descriptions, printable handbook source, user manual, security policy and Windows test checklist.
- Added unit regression tests that fail when a command is omitted or duplicated in `COMMAND_REFERENCE.md`.
- Added an Ubuntu/Xvfb CI job with full GUI click-path checks for all 73 catalog commands and the TEMP cleaner. The job publishes a fresh assertion CSV as an artifact.

## Automated checks expected for v2.5.0

| Check | Acceptance condition | Scope |
|---|---|---|
| Python compilation | Pass | All core modules and tests on Windows CI |
| Python unit regressions | All pass | Catalog metadata, input validation, simulated Windows launch API, TEMP logic, Expert Mode and new commands |
| Exhaustive GUI test | All pass | 73 list selections, input pickers, copy/run/cancel/failure simulations, controls and resizing |
| TEMP cleaner GUI | All pass | Disposable TEMP fixtures only |
| Windows EXE packaging | Build and artifact upload succeed | CI-created unsigned EXE exists; this **does not** prove runtime command correctness |
| Printable PDF | Generate without catalog/reference mismatch | 73 entries and documentation refreshed |

CI workflow: [Windows tests, GUI regression and beta EXE build](.github/workflows/windows-ci.yml). The most recent workflow result is the source of truth until numerical outcomes are recorded below.

## Release limitations

**Real Windows repair-command execution remains unverified.** Unit tests mock `ShellExecuteW` and GUI tests mock launching. No user data, system files, network stack settings or actual Windows installation were intentionally modified during automated tests.

Windows 10/11 compatibility, system locale, PowerShell module availability, Defender policy, time-service state, actual privilege prompts, Windows launch argument behavior, signing/SmartScreen reputation and PyInstaller startup on another PC still need physical pilot testing. Treat the EXE as an **unsigned public beta** even if all CI jobs pass.

**Historical evidence:** [v1.2.0-beta.1 audit](AUDIT_REPORT.md) and [historical GUI assertion matrix](GUI_TEST_MATRIX.csv) describe older releases; do not cite their 69-command results as v2.5.0 test results.

## Year-end handover

1. Retain v2.5.0 source, CI artifacts, updated guide and changelog as the final 2026 milestone once the branch checks succeed.
2. Run the [real Windows pilot checklist](WINDOWS_TEST_PLAN.md) before treating the program as production-validated.
3. Keep this repository **public beta** until actual Windows execution, security and UX checks are documented. Do not disable Windows security controls merely to launch an unsigned EXE.
