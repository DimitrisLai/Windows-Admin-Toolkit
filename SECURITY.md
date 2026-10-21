# Security Policy and Reporting

**Status:** Public beta. The tool can initiate system modifications and must not be used as an unattended maintenance program.

## Supported version

- `v1.2.0-beta.1`: best-effort support and bug fixing, Windows pilot pending.
- Previous versions: superseded by the beta source; upgrade before reporting issues.

## Reporting a problem

For accidental data deletion, privilege bypass, unintended command execution, command injection, or other security concerns, **do not publish exploit details, personal system logs, passwords or recovery keys in an open GitHub Issue**. Use the repository's private security advisory/reporting feature if the maintainer enables it, or contact the maintainer through a private channel they publish. No private reporting address has been designated in this package.

## Boundaries

- Fixed command allowlist; there is no arbitrary user-typed shell command runner.
- File and report paths and the hostname/port controls are validated, including against command-injection syntax.
- Temporary cleanup is confined to the current user's expected local TEMP folder, previews and deletes explicitly selected files only.
- **Some commands send network traffic** (e.g. `Test-NetConnection`, WinGet and some DISM repairs) and tools can display personal system data. The app itself has no telemetry or sign-in.
- UAC elevation and OS policy remain under Windows control. No bypass of antivirus, elevation restrictions, SmartScreen or BitLocker.
- As with any desktop program, no race-free guarantee can be made in the face of concurrent malicious filesystem modifications.
