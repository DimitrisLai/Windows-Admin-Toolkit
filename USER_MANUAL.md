# Windows Admin Toolkit — User Manual

**Version 2.5.0** · 73 built-in commands · MIT · Updated 23 October 2026

## 1. Before you start

Windows Admin Toolkit is a **reference and launcher**, not an automatic repair program. It explains what common Windows commands do and provides a safer way to copy or open them. It does not automatically find and fix all PC problems, nor does it interpret command output.

Requires Windows 10/11, Python 3.10+ with Tkinter (standard Python for Windows). The Python source needs no extra pip packages. A built EXE is optional and must be tested on Windows.

## 2. Install and launch

1. Extract the ZIP archive to a local folder.
2. Install Python from python.org if necessary, including Tcl/Tk.
3. Double-click `Start_Toolkit.pyw`.
4. If `.pyw` file associations do not work, double-click `Run_Windows_Admin_Toolkit.bat` to see startup errors, or run `py -3 app.py` in the extracted directory.
5. You should see the dark GUI with a list of commands at left, drive/target controls in the middle and explanations at right.

## 3. Explore the window

**Left — command browser:** use the Search field, category dropdown, scroll wheel or Ctrl+F to find a command. Select one line; its explanation appears at right. Double-clicking a command copies it to your clipboard; double-clicking does not execute it.

**Middle — drive and inputs:** choose `C:` by default if detected. When a command doesn't use drive letters, the drive picker is disabled deliberately. Refresh drives after inserting/removing disks. For `sfc /scanfile` select the target file. For `powercfg` reports select an existing folder and an HTML filename. For `Test-NetConnection`, enter a host/IP and TCP port. Host/port fields are locked for other commands. The column scrolls if your screen is short.

**Right — command details:** the preview is generated using selected values. Underneath you see What it does, Best for, whether a drive or admin privileges are needed, restarts, safety level and important limitations. Use the Microsoft reference link when provided.

**Bottom actions:** Copy Command copies the exact displayed command. Run Command (or Run as Admin) requests a Windows launch. A separate terminal/tool opens; this app cannot prove whether the command succeeded.

**Header — Expert Mode (v2.4.5):** Click **EXPERT: OFF** to switch to **EXPERT: ON**. Expert Mode suppresses the extra *Launch requested* information popup after Windows accepts a command, making repeated launches faster. You still see system-changing confirmations, validation warnings, error messages, Windows UAC prompts and the separate terminal/application that displays the actual output. The footer still states that the command was launched; that is not a claim that it completed. Toggle back to OFF at any time. It starts OFF whenever the toolkit opens.

## 4. Safety labels and confirmations

- Green: intended for inspection only. Even read-only tests may use network connections or generate disk/CPU load.
- Orange: writes a report, repairs files or changes some settings. A confirmation window appears.
- Red: potentially intensive or disruptive. Backup files and read the cautions before accepting.

If UAC appears, read the publisher/path and only approve an action you initiated. Cancellation should leave the system unchanged. Company policies can disallow elevation or utilities.

## 5. New diagnostic checks in v2.5.0

The **Networking** category now includes Active Windows Firewall profiles (read-only active profile defaults) and Configured DNS servers (read-only DNS configuration by adapter). Use these before changing firewall or DNS settings; displayed configuration is not a connectivity test.

**Logs & monitoring** now includes Microsoft Defender detection history (up to 20 detections available from Defender; results can include personal file paths) and Windows Time synchronization status (source and synchronization details; may require administrator access). Neither performs a scan, cleans malware or adjusts the clock. No detections does not mean a device is malware-free.

Expert Mode continues to suppress only the post-launch notification. Important warnings, administrative approval and error messages remain visible.

## 7. Common workflows

**Windows seems corrupted:** start with `DISM /CheckHealth` then `DISM /ScanHealth` or `sfc /verifyonly`. If a repair is actually needed, back up data first and use Microsoft repair instructions; `DISM /RestoreHealth` and `sfc /scannow` are changes, not harmless viewing.

**Slow PC or high RAM usage:** open Task Manager (`taskmgr`), Resource Monitor (`resmon.exe`), or use Top RAM Processes and physical RAM queries. Windows memory caching is normal: a RAM booster is not included.

**Low disk space:** run Disk Cleanup GUI or Storage Sense settings. For user TEMP, open the TEMP cleaner, preview older files, select only disposable files, review the warning and confirm. The operation permanently deletes selected files. Prefer Windows Storage Sense for broad system cleanup.

**Drive issues:** use `Get-PhysicalDisk`, physical-disk counters, CHKDSK without repair flags or `defrag /A`. A 'Healthy' flag does not guarantee a disk is safe; back up important information before CHKDSK repair. Never stress-test a potentially failing disk before saving data.

**Network problems:** check adapters, `ipconfig`, DNS cache, Wi-Fi interface, `netstat` and `Test-NetConnection` before resetting Winsock or IP. For Test-NetConnection use an approved destination (example `www.microsoft.com`, TCP 443) and read both DNS resolution and TCP test output. A failed remote port does not prove the PC has a fault.

**Driver problems:** open Device Manager, then `pnputil /enum-devices /problem`; inspect third-party installed driver-store packages using `/enum-drivers`. Listing packages doesn't update them.

**Battery drain or sleep problems:** run `powercfg /a`, `/requests`, `/lastwake`, then battery or energy report. SleepStudy works only for Modern Standby-capable devices and may not work on desktops.

**Workplace policy problems:** use `gpresult /r` or `whoami /all` and speak with your IT administrator rather than changing settings yourself.

## 7. Saving HTML reports

Battery Report, Energy Report and SleepStudy require the **Save report as…** selector. Choose an existing folder and `.html` name, then acknowledge the file-creation warning. If the report fails on the Windows computer, the terminal window normally explains why. A destination path containing spaces or non-English characters is supported as long as it does not contain disallowed shell metacharacters.

## 8. TEMP cleaner: precise scope

- Searches old **files** under the signed-in user's `%LOCALAPPDATA%\Temp`.
- Age options are 7, 14, 30, 60 or 90 days based on last modification time.
- Displays up to 300 oldest matching files; scan totals may be larger.
- Selects **zero** files by default; you must choose files before Delete becomes available.
- Confirms deletions; skips changed files, symlinks/junctions, files newer than the cutoff, in-use files and paths that escape the approved folder.
- **Permanently deletes** selected files; it does not use the Recycle Bin or provide an undo action.
- Doesn't remove directories or clean Downloads, browsers, Windows components, Recycle Bin or any arbitrary user-chosen TEMP directory.

**Never use this first on a business PC or to recover urgently needed space.** Windows Storage Sense/Disk Cleanup are safer system-maintained alternatives.

## 9. Troubleshooting

| Symptom | First action |
|---|---|
| App does not start | Launch `Run_Windows_Admin_Toolkit.bat` to see the Python error; check Python 3.10+ and Tkinter |
| No drive letters listed | Click Refresh drives; ensure a local volume is mounted; drive-specific commands remain locked until detected |
| Command not available | Windows edition, version, optional component or corporate policies may not provide it |
| Copy or Run greyed out | Choose required SFC file, report destination, valid host/port, or detected drive |
| UAC cancelled | Run was not approved. Do not turn off security settings just to proceed |
| Windows command window reports error | Read the Windows message and the Microsoft documentation linked in the UI |
| SleepStudy unsupported | Check `powercfg /a`; the computer may not support Modern Standby |
| WinGet missing | Update/install Windows Package Manager through supported Microsoft channels, or skip it |

## 10. What has not been validated

The Linux automated tests exercise 69 commands by simulated launch request only. They do **not** establish successful outcomes on Windows, UAC behavior, or that PyInstaller builds an EXE that works on every PC. See [`WINDOWS_TEST_PLAN.md`](WINDOWS_TEST_PLAN.md) before a public stable release.

## 10. Privacy, support and licensing

No tracking or sign-in. Some Windows utilities can use the network. Review outputs for user names, serials, SIDs, SSIDs, hostnames and enterprise details before sharing. Bug reports should omit secrets and identifying information. The project code is MIT licensed, without warranty.
