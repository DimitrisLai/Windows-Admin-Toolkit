# Windows Admin Toolkit v2.5.0 — Year-End Release Audit

**Date:** 23 October 2026  
**Scope:** Public beta source milestone, **73 built-in commands across 11 categories**  
**Status:** Automated branch checks passed on 23 October 2026. **Windows real-device execution not yet validated.**

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

## Automated checks completed for v2.5.0

| Check | Verified result | Scope |
|---|---|---|
| Python compilation | **PASS** | All core modules and tests in Windows CI |
| Python unit regressions | **67/67 PASS** | Catalog metadata, input validation, simulated Windows launch API, TEMP logic, Expert Mode and four new commands |
| Exhaustive GUI test | **1,385/1,385 PASS** | 73 list selections, input pickers, copy/run/cancel/failure simulations, controls, scrolling and resizing |
| TEMP cleaner GUI | **13/13 PASS** | Disposable TEMP fixtures only |
| Windows EXE packaging | **PASS** | Windows GitHub Actions built and uploaded an unsigned EXE; this **does not** establish that the program works on all real Windows PCs |
| Printable PDF | **Reference parity PASS; PDF publication checked separately after merge** | Catalog has 73 entries, and the printable PDF build enforces exact reference parity |

**Evidence:** [v2.5.0 Windows + GUI CI run](https://github.com/DimitrisLai/Windows-Admin-Toolkit/actions/runs/39991865045) for branch commit `5516b5aaf97d712ba92cb2ca8cbd280c0eaaeded`. The GUI job uploads a current `WindowsAdminToolkit-v2.5.0-gui-test-matrix` CSV artifact; the tracked `GUI_TEST_MATRIX.csv` remains historical.

## Release limitations

**Real Windows repair-command execution remains unverified.** Unit tests mock `ShellExecuteW` and GUI tests mock launching. No user data, system files, network stack settings or actual Windows installation were intentionally modified during automated tests.

Windows 10/11 compatibility, system locale, PowerShell module availability, Defender policy, time-service state, actual privilege prompts, Windows launch argument behavior, signing/SmartScreen reputation and PyInstaller startup on another PC still need physical pilot testing. Treat the EXE as an **unsigned public beta** even if all CI jobs pass.

**Historical evidence:** [v1.2.0-beta.1 audit](AUDIT_REPORT.md) and [historical GUI assertion matrix](GUI_TEST_MATRIX.csv) describe older releases; do not cite their 69-command results as v2.5.0 test results.

## Year-end handover

1. Retain v2.5.0 source, CI artifacts, updated guide and changelog as the final 2026 milestone after the successful automated branch tests.
2. Run the [real Windows pilot checklist](WINDOWS_TEST_PLAN.md) before treating the program as production-validated.
3. Keep this repository **public beta** until actual Windows execution, security and UX checks are documented. Do not disable Windows security controls merely to launch an unsigned EXE.
