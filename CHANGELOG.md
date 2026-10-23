# Changelog

## [2.5.0] — 23 October 2026 (2026 year-end public beta)

**73 curated commands in 11 categories; final planned 2026 code milestone.**

- Added four **inspection-only** troubleshooting commands: active Windows Firewall profiles, configured DNS server addresses, Microsoft Defender detection history, and Windows Time synchronization status.
- All new commands have use cases, limitations, privacy cautions and Microsoft reference links; none modifies Windows settings.
- Retained the v2.4.5 Expert Mode toggle without hiding risk confirmations, UAC, errors or command-output windows.
- Updated the GUI version and changed the footer to derive its count from the live command catalog.
- Added documentation-to-catalog regression checks so the detailed command reference must cover every entry exactly once.
- Added a separate Linux/Xvfb GUI regression job to click through all 73 commands with mocked Windows launches, and upload its assertion CSV.
- Updated the printable PDF generator, user manual, full command reference and Windows pilot checklist for 73 commands.
- **Validation boundary:** automated command-building/mocked-launch tests and CI-built Windows EXE do not establish that actual repair commands work on production PCs. Retain the beta label and unsigned-binary warning.

## [2.4.5] — 23 October 2026

**Expert Mode quality-of-life update — Windows real-device execution remains unverified.**

- Added an always-visible **EXPERT: OFF / EXPERT: ON** header toggle. It is OFF at every startup and does not persist.
- When ON, suppresses only the redundant **Launch requested** information popup after Windows accepts a command launch; status-bar feedback remains visible.
- Kept risky-command confirmations, UAC, input-validation warnings, launch errors and separate output/management windows unchanged. This switch does **not** bypass safeguards or silently execute commands.
- Added focused mock-based tests for normal/expert successful launches, safety confirmation and cancellation, failed launches and non-Windows warnings, plus GUI toggle smoke assertions.
- Documented usage and limits. The previous version recorded in this repository is **1.2.0-beta.1**; the 2.4.5 label is the specifically requested milestone, not evidence of unpublished intervening releases.

## [1.2.0-beta.1] — 21 October 2026

**Public beta candidate — Windows execution still needs real-device validation.**

- Added **9 commands**, increasing the curated catalog from 60 to **69** in 11 existing categories: PnP problem devices, OEM driver packages, network adapters, configurable TCP connectivity, WinGet available upgrades, SleepStudy HTML report, effective Group Policy, WMI verification, and `whoami /all`.
- Added **Hostname/IP + TCP port input controls** in the scrollable middle panel, enabled only for `Test-NetConnection`, with strict validation (ASCII DNS/IPv4/IPv6, port 1–65535) to prevent script-injection input.
- Integrated SleepStudy with existing HTML report picker and output-file confirmation (does not try to run as a drive-specific operation).
- Updated displayed descriptions, best-use cases, privileges, safety/restart notes and source links; clarified WinGet lists (does not install), Modern Standby-only support and username/policy-output privacy.
- Added **11 new unit tests**, expanded GUI test coverage to all 69 commands; **55/55 unit tests, 1,313/1,313 GUI checks, 13/13 TEMP-cleaner GUI checks**, and smoke tests passed on Linux/Xvfb. Simulated Windows launcher checks are **not actual command execution**.
- Updated README, illustrated user manual, complete command reference, Windows pilot checklist, audit report, security guidance and Windows GitHub Actions CI/build workflow.

## [1.1.2] — 21 October 2026

- Full original 60-command beginner-style click-through audit: 44 unit tests, 1,025 Tkinter UI checks and 13 TEMP cleaner UI checks (all passed under headless Linux display with mocked Windows command launches).
- Fixed short-window middle-column clipping, disappearing TEMP deletion results and handling of missing local volumes.
- Corrected risk classification for battery-report output.

## [1.1.1]

- Tightened SFC path validation, TEMP root confinement, empty-search action locking and pointer-size ShellExecute success checks.

## [1.1.0]

- Expanded from 26 to 60 commands, adding RAM, TEMP cleanup, storage, drivers, power, monitoring and network diagnostics.

## [1.0.0]

- Initial three-column Python/Tkinter app with 26 curated Windows commands.
