# Windows Admin Toolkit — Real Windows Pilot Checklist

**Applies to:** v2.5.0 (73 commands). The previous Linux simulations and Xvfb GUI tests **do not replace** these tests.

## Before testing

- [ ] Test on your own Windows 11 PC with an ordinary user account (preferably also Windows 10, if available).
- [ ] Extract the source ZIP to a normal local folder and note Windows build/edition (`winver`).
- [ ] Back up important files, avoid critical working hours and do not run a destructive repair on your production PC purely as a test.
- [ ] Test only on a PC for which you have administrator permission. Do not change policies to bypass restrictions.

## Essential interface tests

- [ ] Launch `Start_Toolkit.pyw`, close and restart it, minimize/maximize and resize to 1080×620.
- [ ] Toggle Expert Mode ON and OFF. Confirm only the redundant post-launch info message disappears; risk confirmations, UAC, output windows, and errors remain visible. Restart to verify it defaults OFF.
- [ ] Search by name, description, and nonsense string; zero results must disable Copy and Run.
- [ ] Select each of the 73 commands, read explanations and confirm intended drive/target locks.
- [ ] Switch from `C:` to another local drive (if available) and verify CHKDSK and defrag previews change appropriately.
- [ ] Click small copy icon and full Copy Command; compare text with the displayed command.
- [ ] Ctrl+F focuses Search; scroll left list, middle controls and right description.
- [ ] Cancel every file/report picker and every changing-command confirmation; no command should launch.
- [ ] Test UAC cancellation and approval for a benign read-only command such as `sfc /verifyonly`.
- [ ] Test the dropdown when the selected drive is removed or becomes unavailable.

## Safe execution smoke tests

Mark result for each: **Pass**, **Unsupported/not installed**, **Admin denied**, or **Incorrect behavior**. Read actual command output, not only the toolkit launch dialog.

| Test | Suggested command | Expected behavior |
|---|---|---|
| OS info | `systeminfo` | Prints OS/hardware summary |
| Account | `whoami /all` | Shows current token/groups/privileges; do not publicly share identifiers |
| Files | `sfc /verifyonly` | Verifies protected files; may require admin and take time |
| Image | `DISM /Online /Cleanup-Image /CheckHealth` | Reports component-store health flag |
| Storage | `Get-PhysicalDisk` | Lists disks, if supported by Windows storage provider |
| Network | `Get-NetAdapter` | Lists visible adapters |
| TCP host | `Test-NetConnection` to approved server/port 443 | Displays DNS/TCP results; network request is sent |
| Drivers | `pnputil /enum-devices /problem` | Shows devices with problems or an empty result |
| Driver packages | `pnputil /enum-drivers` | Lists third-party driver-store packages |
| Updates | `winget upgrade` | Lists available application updates; may prompt source agreement, does not install |
| Sleep | `powercfg /a` | Reports supported sleep states |
| Policy | `gpresult /r` | Shows applicable group-policy data (if accessible) |
| WMI | `winmgmt /verifyrepository` | Reports live WMI repository consistency; no repair occurs |
| Recent issues | `perfmon /rel` | Opens Reliability Monitor |
| Windows logs | `eventvwr.msc` | Opens Event Viewer |
| Firewall | `Get-NetFirewallProfile -PolicyStore ActiveStore` | Shows active firewall profile defaults without changes |
| DNS | `Get-DnsClientServerAddress` | Shows configured IPv4/IPv6 DNS resolver settings |
| Defender history | `Get-MpThreatDetection` | Shows historical detections if Defender is available; empty history is inconclusive |
| Windows Time | `w32tm /query /status` | Reports time service state/source, or a clear service/elevation error |

## Generated report tests

- [ ] Battery report: choose a fresh `.html` path, confirm, check file created and HTML opens (laptops preferred).
- [ ] Energy report: choose a fresh `.html` path, confirm, wait at least 60 seconds, inspect result if permission permits.
- [ ] SleepStudy: on a device with Modern Standby, choose a fresh `.html` path and verify HTML; on others, confirm unsupported status is explained.
- [ ] Report file picker cancel leaves action disabled. Paths containing spaces should work; trying a network share/unsafe path should be rejected.

## TEMP-cleaner tests

- [ ] Use only **disposable** files within your own `%LOCALAPPDATA%\Temp` and let test files age naturally or follow the manual test procedure in the previous pilot checklist.
- [ ] Preview without selecting files: Delete remains disabled; no cleanup occurs.
- [ ] Select a disposable file, cancel the warning and verify it remains.
- [ ] Confirm deletion of one disposable file and verify all other files remain.
- [ ] Confirm a file still in use is skipped, not forcibly removed.
- [ ] Confirm results display the count of deleted/skipped files after refresh.
- [ ] Never test deletion on Downloads, production data, work documents or a system folder.

## High-impact commands (test on a disposable Windows VM only)

- [ ] `chkdsk /f`, `chkdsk /r`: validate warnings and restart behavior on a disposable test volume.
- [ ] `netsh winsock reset` and `netsh int ip reset`: validate warnings/reboot/connection recovery in a VM where settings can be restored.
- [ ] `DISM /StartComponentCleanup`: run only in a disposable Windows installation; verify backup/rollback expectations.
- [ ] For these commands, pressing **No** must never launch the utility.

## Executable and public beta acceptance

- [ ] Build `dist\WindowsAdminToolkit.exe` with `Build_Windows_EXE.bat` on real Windows.
- [ ] Open on a second Windows PC with no Python, if possible, and verify all tabs and pickers.
- [ ] Compare copied commands and actual native command window output; confirm UAC on an admin-required read-only command.
- [ ] Check Microsoft Defender and SmartScreen behavior without disabling security protections; unsigned binaries may be blocked.
- [ ] Run `py -3 -m unittest discover -s tests -v` on Windows and record failures.
- [ ] Once Windows-specific bugs are fixed, tag a public **beta** release; promote to stable only after these tests and high-impact VM testing.

## Bug report template

```text
Windows version/build:
Python or EXE:
Toolkit version:
Selected command:
Drive / target selection (redact personal details):
What I clicked:
Expected outcome:
Actual message / screenshot (redacted):
Was UAC approved or canceled?:
```
