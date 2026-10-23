# Windows Admin Toolkit v2.5.0 — Final Feature Release for 2026

**Version 2.5.0 · Created by Dimitris Laidis · MIT License**  
**Release date:** October 23, 2026 · **73 built-in commands / 11 categories**

## Project status — Feature-complete for 2026

**v2.5.0 is the final planned feature release for 2026.** No additional feature releases or scheduled updates are planned through **December 31, 2026**. The repository remains public and MIT-licensed, with issues and pull requests open. Important security, critical bug, compatibility or code-signing fixes may be published if necessary. Development may be reconsidered in 2027. This is **maintenance-only**, not an archived or abandoned repository.

## Downloads

- **Windows-Admin-Toolkit-v2.5.0-Windows.zip** — unsigned `WindowsAdminToolkit.exe`, quick-start instructions, MIT license, and user manual. Extract before running. **Python is not required for the EXE.**
- **Windows-Admin-Toolkit-v2.5.0-Source.zip** — complete tagged repository source, tests, launch scripts, documentation and assets.
- **Windows-Admin-Toolkit-v2.5.0-User-Manual.pdf** — 73-command printable reference.
- **SHA256SUMS.txt** — SHA-256 integrity hashes for the three assets.

## What's included

Four new read-only inspections — active Windows Firewall profiles, configured DNS server addresses, Microsoft Defender detection history and Windows Time synchronization state. The previous Expert Mode switch remains optional and suppresses only successful-launch information notices, not safety prompts, launch errors, UAC or command output.

## Verification and safety

At the v2.5 code-freeze audit, **67 automated Python unit tests, 1,385 simulated GUI checks and 13 TEMP cleaner GUI checks passed**. The Windows CI build generated an unsigned executable, and the PDF handbook was generated successfully. The maintainer has tested the application on Windows. These automated checks do **not** establish that all 73 commands, UAC scenarios, OS configurations or repair outcomes have been verified.

**Safety notice:** This toolkit can launch system-changing operations. Back up important data and read the warnings and native command outputs. Do **not** disable Defender, SmartScreen, or workplace security controls to run an unsigned build. SHA-256 checksums help detect changed downloads but do not replace publisher code signing.

See `V2_5_RELEASE_AUDIT.md`, `WINDOWS_TEST_PLAN.md`, and `SECURITY.md` in the source ZIP for further details.
