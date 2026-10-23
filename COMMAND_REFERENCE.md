# Windows Admin Toolkit — Complete Command Reference

**Version:** 2.5.0 · **Date:** 23 October 2026 · **License:** MIT

This reference describes all 73 commands defined in `command_catalog.py` for v2.5.0. It is not a promise that every utility exists on every version of Windows.

## Safety key

- **Inspection / low risk**: intended to inspect or list information (some may create network traffic).
- **Changes system or writes report**: may modify a setting, repair files, open an action-oriented GUI, or create/overwrite a file. The app requests confirmation.
- **Intensive / potentially disruptive**: may take a long time or reset major system settings. The app displays a stronger confirmation.

The **Run** button only confirms a Windows launch request, **not completion or success**. Read the separate terminal result.

For volume-specific commands the UI passes the currently selected drive, initially `C:` where detected; the drive selector is locked otherwise. PowerShell physical-disk checks do not use drive letters.

## Windows files (3)

### `sfc /scannow`

- **What it does:** Scans protected Windows system files and replaces corrupted versions where possible.
- **Best for:** Windows crashes, missing system files, or recurring system errors.
- **Notes / limits:** DISM /RestoreHealth may be useful first if the component store is damaged. A scan can take time.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `sfc.exe /scannow`
- **Reference:** [Microsoft documentation](https://support.microsoft.com/en-us/windows/using-system-file-checker-in-windows-365e0031-36b1-611a-1a6b-3cb056aa98d1)

### `sfc /verifyonly`

- **What it does:** Scans protected Windows files for integrity problems without repairing them.
- **Best for:** Checking for system file problems before attempting repairs.
- **Notes / limits:** This is a read-only integrity check; any problems reported require a separate repair.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `sfc.exe /verifyonly`
- **Reference:** [Microsoft documentation](https://support.microsoft.com/en-us/windows/using-system-file-checker-in-windows-365e0031-36b1-611a-1a6b-3cb056aa98d1)

### `sfc /scanfile=<file>`

- **What it does:** Scans and, when possible, repairs one specified protected Windows system file.
- **Best for:** Checking a particular Windows system DLL or other protected file.
- **Notes / limits:** Choose an existing local file. This is intended for protected system files, not ordinary documents.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** SFC file picker
- **Command example:** `sfc.exe /scanfile=C:\Windows\System32\kernel32.dll`
- **Reference:** [Microsoft documentation](https://support.microsoft.com/en-us/windows/using-system-file-checker-in-windows-365e0031-36b1-611a-1a6b-3cb056aa98d1)

## Windows image (DISM) (4)

### `DISM /Online /Cleanup-Image /CheckHealth`

- **What it does:** Quickly reports whether the Windows component store was previously flagged as corrupted.
- **Best for:** A fast preliminary Windows image health check.
- **Notes / limits:** Does not perform a new deep scan and does not repair the component store.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dism.exe /Online /Cleanup-Image /CheckHealth`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image?view=windows-11)

### `DISM /Online /Cleanup-Image /ScanHealth`

- **What it does:** Performs a more thorough scan of the running Windows component store for corruption.
- **Best for:** Diagnosing Windows image health when the quick check is insufficient.
- **Notes / limits:** This may take several minutes. It scans but does not repair the image.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dism.exe /Online /Cleanup-Image /ScanHealth`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image?view=windows-11)

### `DISM /Online /Cleanup-Image /RestoreHealth`

- **What it does:** Repairs corruption in the running Windows component store using available repair sources.
- **Best for:** Fixing a damaged component store, especially before running SFC.
- **Notes / limits:** May use Windows Update to obtain repair files. Offline or restricted machines may need a /Source.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dism.exe /Online /Cleanup-Image /RestoreHealth`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image?view=windows-11)

### `DISM /Online /Cleanup-Image /AnalyzeComponentStore`

- **What it does:** Analyzes Windows component store size and reports whether cleanup is recommended.
- **Best for:** Investigating component store disk usage without making changes.
- **Notes / limits:** A cleanup recommendation is informational; this command does not delete files.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dism.exe /Online /Cleanup-Image /AnalyzeComponentStore`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image?view=windows-11)

## Disk & storage (11)

### `chkdsk <Drive>`

- **What it does:** Checks file system status on the selected local volume without requesting repairs.
- **Best for:** A preliminary review of suspected file system errors.
- **Notes / limits:** Read-only checks on active volumes may report transient discrepancies. Local volumes only.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `chkdsk.exe C:`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk)

### `chkdsk <Drive> /scan`

- **What it does:** Runs an online NTFS scan of the selected local volume.
- **Best for:** Checking an NTFS drive with less disruption than an offline repair.
- **Notes / limits:** NTFS only. Some problems may still require offline repair or a restart.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `chkdsk.exe C: /scan`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk)

### `chkdsk <Drive> /f`

- **What it does:** Fixes file system errors on the selected local volume.
- **Best for:** Repairing confirmed file system problems.
- **Notes / limits:** May ask to schedule a check at reboot when the volume is in use. Back up important files first.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** May be required
- **Special input:** None
- **Command example:** `chkdsk.exe C: /f`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk)

### `chkdsk <Drive> /f /r`

- **What it does:** Checks file system errors, scans for bad sectors and attempts to recover readable data.
- **Best for:** Investigating storage read errors or suspected bad sectors.
- **Notes / limits:** Potentially very slow and intensive. Back up important data first; on a failing drive prioritize recovery.
- **Safety:** Intensive / potentially disruptive
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** May be required
- **Special input:** None
- **Command example:** `chkdsk.exe C: /f /r`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk)

### `Get-PhysicalDisk (health status)`

- **What it does:** Displays disk health and operational statuses reported by Windows storage providers.
- **Best for:** A modern first look at reported physical disk health.
- **Notes / limits:** Replaces obsolete WMIC. Not a complete SMART diagnosis; reported Healthy is not proof a disk is fault-free.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,Size | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/storage/get-physicaldisk)

### `Get-Volume -DriveLetter <Drive>`

- **What it does:** Shows Windows storage and file system information for the selected volume.
- **Best for:** Checking the volume file system, Windows health status, and free space.
- **Notes / limits:** Some provider fields may be unavailable for particular volumes.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-Volume -DriveLetter C | Format-List DriveLetter,FileSystem,FileSystemLabel,HealthStatus,Size,SizeRemaining"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/storage/get-volume)

### `Disk reliability counters (PowerShell)`

- **What it does:** Displays available temperature, wear and read/write error counters from compatible physical disks.
- **Best for:** Looking for reported SSD/HDD temperature, lifetime and media-error warning signals.
- **Notes / limits:** A blank value can mean unsupported hardware or drivers, not zero; Windows storage providers vary. No complete SMART test.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId,Temperature,Wear,ReadErrorsTotal,WriteErrorsTotal | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/storage/get-storagereliabilitycounter)

### `defrag <Drive> /A /V`

- **What it does:** Analyzes the selected volume’s optimization status and prints detailed information without optimizing it.
- **Best for:** Checking whether Windows considers a drive in need of optimization.
- **Notes / limits:** Administrator permission may be needed. This is not a disk integrity or SMART test.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `defrag.exe C: /A /V`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/defrag)

### `defrag <Drive> /O /V`

- **What it does:** Asks Windows to select the appropriate optimization for the volume’s media type.
- **Best for:** Optimizing an HDD or requesting supported SSD retrim/maintenance using Windows defaults.
- **Notes / limits:** Can take time and generate disk activity. /O chooses appropriate behavior; do not assume it always performs traditional defragmentation.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `defrag.exe C: /O /V`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/defrag)

### `fsutil dirty query <Drive>`

- **What it does:** Queries the volume dirty bit, which indicates Windows may need to check the file system.
- **Best for:** Investigating a volume that Windows flags for a check during startup.
- **Notes / limits:** A dirty bit does not by itself diagnose the cause. Some volumes/filesystems are unsupported; admin may be required.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `fsutil.exe dirty query C:`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-dirty)

### `manage-bde -status <Drive>`

- **What it does:** Shows BitLocker encryption, conversion and protection status for the selected volume.
- **Best for:** Verifying whether a volume is encrypted or protected before storage troubleshooting.
- **Notes / limits:** Status output can reveal identifying volume details, but this command does not display BitLocker recovery passwords.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `manage-bde.exe -status C:`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/manage-bde-status)

## Hardware & diagnostics (5)

### `mdsched.exe`

- **What it does:** Opens Windows Memory Diagnostic and offers to test RAM at the next reboot.
- **Best for:** Suspected RAM-related blue screens, instability, or random crashes.
- **Notes / limits:** Opening this tool does not immediately restart the PC; Windows asks you to choose a testing time.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** User chooses
- **Special input:** None
- **Command example:** `mdsched.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `systeminfo`

- **What it does:** Prints detailed information about Windows, hardware, patches, and boot time.
- **Best for:** Collecting useful system specifications for support and troubleshooting.
- **Notes / limits:** Output can contain computer names and other system details; review before sharing.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `systeminfo.exe`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo)

### `msinfo32`

- **What it does:** Opens System Information with hardware resources, drivers, and OS details.
- **Best for:** Investigating a machine configuration through a graphical tool.
- **Notes / limits:** Read-only viewer. Information may take a moment to load.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `msinfo32.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `winmgmt /verifyrepository`

- **What it does:** Checks the consistency of the live Windows Management Instrumentation (WMI) repository.
- **Best for:** Investigating suspected WMI repository corruption behind failing management queries.
- **Notes / limits:** Verification does not repair or reset WMI. An inconsistent result needs careful diagnosis; do not automatically reset the repository.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `winmgmt.exe /verifyrepository`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/wmisdk/winmgmt)

### `whoami /all`

- **What it does:** Displays the security identifiers, groups and privileges in the current process access token.
- **Best for:** Understanding which account and privileges a command window actually has.
- **Notes / limits:** Results can differ between standard and elevated launches. Output includes SIDs and security-group membership; review before sharing.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `whoami.exe /all`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami)

## Activation & licensing (2)

### `slmgr /xpr`

- **What it does:** Reports whether the current Windows activation is permanent or expires.
- **Best for:** Confirming activation expiration state.
- **Notes / limits:** Uses Microsoft slmgr.vbs through cscript; does not activate Windows or change a license.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `cscript.exe //nologo C:\Windows\System32\slmgr.vbs /xpr`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/get-started/activation-slmgr-vbs-options)

### `slmgr /dlv`

- **What it does:** Shows detailed Windows licensing and activation information.
- **Best for:** Diagnosing legitimate Windows licensing issues.
- **Notes / limits:** Output includes licensing identifiers. Review before sharing publicly.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `cscript.exe //nologo C:\Windows\System32\slmgr.vbs /dlv`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/get-started/activation-slmgr-vbs-options)

## Networking (13)

### `ipconfig /all`

- **What it does:** Displays network adapter addresses, DNS settings, DHCP details, and related configuration.
- **Best for:** Finding local network configuration and troubleshooting connection issues.
- **Notes / limits:** Displays local networking identifiers; review before sharing.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `ipconfig.exe /all`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)

### `ipconfig /flushdns`

- **What it does:** Clears the local DNS resolver cache.
- **Best for:** Troubleshooting stale or incorrect cached DNS results.
- **Notes / limits:** Does not reset network adapters or change network configuration.
- **Safety:** Changes settings or writes files
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `ipconfig.exe /flushdns`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)

### `ipconfig /registerdns`

- **What it does:** Initiates DNS registration for eligible network adapter records.
- **Best for:** Troubleshooting DNS registration on appropriately configured networks.
- **Notes / limits:** May be irrelevant on typical home devices; DNS registration can depend on domain/network policy.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `ipconfig.exe /registerdns`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)

### `netsh winsock reset`

- **What it does:** Resets the Winsock catalog to its default state.
- **Best for:** Investigating persistent networking issues that may involve Winsock providers.
- **Notes / limits:** Changes networking configuration. Can affect third-party network components; reboot is usually necessary.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** Usually required
- **Special input:** None
- **Command example:** `netsh.exe winsock reset`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh)

### `netsh int ip reset`

- **What it does:** Resets TCP/IP settings to Windows defaults.
- **Best for:** Repairing serious network stack configuration issues.
- **Notes / limits:** May remove custom network settings (including static configuration); record settings first. Reboot afterward.
- **Safety:** Intensive / potentially disruptive
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** Usually required
- **Special input:** None
- **Command example:** `netsh.exe int ip reset`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh)

### `ipconfig /displaydns`

- **What it does:** Displays the Windows DNS Client resolver cache entries currently stored locally.
- **Best for:** Seeing whether recent DNS lookups or negative DNS cache entries exist.
- **Notes / limits:** May reveal sites or services accessed by applications; DNS entries are not a reliable browser-history record.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `ipconfig.exe /displaydns`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)

### `netsh wlan show interfaces`

- **What it does:** Shows Wi-Fi interface details such as connection state, radio type and current signal level.
- **Best for:** Investigating wireless signal or connection issues on a PC with Wi-Fi.
- **Notes / limits:** Requires Windows WLAN AutoConfig and compatible Wi-Fi hardware; no Wi-Fi interface means no useful data.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `netsh.exe wlan show interfaces`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan)

### `netsh wlan show wlanreport`

- **What it does:** Generates a local HTML report of recent Windows Wi-Fi connection events and failures.
- **Best for:** Diagnosing intermittent Wi-Fi disconnects and connection errors.
- **Notes / limits:** Creates report files on disk (often under ProgramData); administrator access is recommended. Reports may contain SSIDs and device identifiers.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `netsh.exe wlan show wlanreport`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan)

### `netstat -ano`

- **What it does:** Lists active TCP connections, listening TCP/UDP ports, numerical endpoints and owning process IDs.
- **Best for:** Investigating unexpected network listeners or finding which PID owns a connection.
- **Notes / limits:** Snapshot only; PID identifies a process but does not establish whether traffic is malicious.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `netstat.exe -ano`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat)

### `Get-NetAdapter (PowerShell)`

- **What it does:** Lists visible network adapters with their status, reported link speed and MAC address.
- **Best for:** Checking whether Windows sees a wired or wireless adapter and whether its link is up.
- **Notes / limits:** Virtual adapters may be included; a connected link is not proof that internet access works. MAC addresses are identifying data.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-NetAdapter | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/netadapter/get-netadapter)

### `Test-NetConnection <host> -Port <port>`

- **What it does:** Attempts a TCP connection to the specified host and port; shows DNS, routing and TCP test results.
- **Best for:** Testing if a specific website/server port (for example HTTPS 443) is reachable.
- **Notes / limits:** Enter a trusted hostname or IP address and port (1–65535). A failed result may be caused by a firewall or remote-service policy, not necessarily by your PC. Makes outbound network traffic.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** DNS/IP host and TCP port
- **Command example:** `powershell.exe -NoProfile -Command "Test-NetConnection -ComputerName www.microsoft.com -Port 443 -InformationLevel Detailed | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection)

### `Active Windows Firewall profiles (PowerShell)`

- **What it does:** Displays active Domain, Private and Public Windows Firewall profile settings without changing rules.
- **Best for:** Investigating whether Windows Firewall is enabled and how inbound and outbound traffic are handled.
- **Notes / limits:** Shows configured profile defaults, not a guarantee that a specific connection is allowed. Corporate policy or third-party firewalls can change effective behavior.
- **Safety:** Inspection / low risk
- **Administrator:** No · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-NetFirewallProfile -PolicyStore ActiveStore | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallprofile?view=win10-ps)

### `Configured DNS servers (PowerShell)`

- **What it does:** Shows DNS server addresses configured on Windows network interfaces for IPv4 and IPv6.
- **Best for:** Diagnosing incorrect DNS resolvers, name-resolution failures or unexpected network settings.
- **Notes / limits:** May list disconnected adapters and private network addresses. This checks configuration, not whether DNS resolution is working.
- **Safety:** Inspection / low risk
- **Administrator:** No · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-DnsClientServerAddress | Select-Object InterfaceAlias,AddressFamily,ServerAddresses | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/dnsclient/get-dnsclientserveraddress)

## Logs & monitoring (11)

### `perfmon /rel`

- **What it does:** Opens Reliability Monitor, showing application and Windows failures over time.
- **Best for:** Finding which crashes or failures occurred around a particular date.
- **Notes / limits:** A useful first stop for recurring crashes and application errors.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `perfmon.exe /rel`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `eventvwr.msc`

- **What it does:** Opens Windows Event Viewer to inspect system, application, and security logs.
- **Best for:** Examining warnings and failures after a specific problem.
- **Notes / limits:** Many events are routine; focus on events matching the actual time of the issue.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `eventvwr.msc`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `taskmgr`

- **What it does:** Opens Task Manager to view running processes and resource usage.
- **Best for:** Investigating unusually high CPU, RAM, disk, or network use.
- **Notes / limits:** Opening Task Manager is safe; avoid ending unknown processes.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `taskmgr.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `System error events: last 7 days (PowerShell)`

- **What it does:** Shows up to 30 error-level events from the System log in the past seven days, newest first.
- **Best for:** Finding errors close to a Windows crash, hardware fault or unexpected restart.
- **Notes / limits:** No matching events is not proof the PC is healthy. Reading some event logs may require elevation.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-WinEvent -FilterHashtable @{LogName='System';Level=2;StartTime=(Get-Date).AddDays(-7)} -MaxEvents 30 | Select-Object TimeCreated,Id,ProviderName,Message | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-5.1)

### `Recent hotfix records (PowerShell)`

- **What it does:** Lists up to 15 Windows hotfix records in descending installed-date order.
- **Best for:** Checking recently recorded servicing changes while troubleshooting.
- **Notes / limits:** Get-HotFix does not list every feature update, driver update or Microsoft Store update; some dates may be missing.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 15 HotFixID,InstalledOn,Description | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix)

### `reagentc /info`

- **What it does:** Shows whether Windows Recovery Environment is enabled and where its recovery image is configured.
- **Best for:** Checking recovery readiness before attempting advanced Windows repairs.
- **Notes / limits:** Read-only command; some systems require administrator permissions to access all details.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `reagentc.exe /info`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/reagentc-command-line-options)

### `Microsoft Defender status (PowerShell)`

- **What it does:** Displays current antivirus and real-time protection status and signature-update date when Defender is available.
- **Best for:** Checking whether Microsoft Defender protection and signature updates are active.
- **Notes / limits:** Third-party antivirus products, security policy or Defender component availability can affect results.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=windowsserver2025-ps)

### `winget upgrade (list only)`

- **What it does:** Lists installed applications for which WinGet identifies available updates; does not install them.
- **Best for:** Checking application update opportunities before updating anything.
- **Notes / limits:** Requires Windows Package Manager (App Installer). Depending on source configuration, WinGet may access the network or request agreement acceptance. This is not Windows Update.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `winget.exe upgrade`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade)

### `gpresult /r`

- **What it does:** Shows summary information about applied Group Policy settings for the current user and computer when accessible.
- **Best for:** Troubleshooting organizational restrictions and unexpected policy-controlled settings.
- **Notes / limits:** The current user context matters: elevation as a different administrator can show a different user. Some computer data may require elevation; personal PCs may have little policy information.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `gpresult.exe /r`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult)

### `Microsoft Defender detection history (PowerShell)`

- **What it does:** Lists up to 20 recent active or historical threat-detection records available to Microsoft Defender Antivirus.
- **Best for:** Reviewing detections after investigating suspicious files or an unexpected antivirus warning.
- **Notes / limits:** Defender must be available and permitted by policy. History can be incomplete; an empty list does not prove the device is malware-free. Resources may include sensitive local paths.
- **Safety:** Inspection / low risk
- **Administrator:** No · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-MpThreatDetection | Sort-Object InitialDetectionTime -Descending | Select-Object -First 20 InitialDetectionTime,ThreatID,ActionSuccess,Resources | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/defender/get-mpthreatdetection?view=windowsserver2022-ps)

### `Windows Time synchronization status`

- **What it does:** Shows the local Windows Time service synchronization state, source and last recorded successful synchronization.
- **Best for:** Investigating wrong system time, authentication failures or clock-related errors.
- **Notes / limits:** The Windows Time service must be available; local administrator rights can be required. This query does not resynchronize or change time settings.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `w32tm.exe /query /status`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/networking/windows-time-service/windows-time-service-tools-and-settings)

## RAM & performance (5)

### `resmon.exe`

- **What it does:** Opens Resource Monitor to inspect per-process memory usage plus CPU, disk and networking activity.
- **Best for:** Finding applications consuming RAM and investigating resource pressure.
- **Notes / limits:** Resource Monitor is an interactive viewer; high cached RAM alone does not mean memory is faulty.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `resmon.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `Installed RAM modules (PowerShell)`

- **What it does:** Lists memory module slots, manufacturers, module capacities in GiB, rated speeds, and part numbers as reported by firmware.
- **Best for:** Confirming installed RAM size and investigating module differences.
- **Notes / limits:** Reported module details depend on BIOS/firmware; reported Speed is not a benchmark.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Manufacturer,@{Name='CapacityGB';Expression={[math]::Round($_.Capacity/1GB,2)}},Speed,PartNumber | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance)

### `Installed and free RAM (PowerShell)`

- **What it does:** Reports total usable and currently free physical RAM in GiB using values that Windows exposes in KiB.
- **Best for:** Checking whether Windows currently has little free physical memory.
- **Notes / limits:** Free physical memory changes constantly; Windows also intentionally uses memory for caching.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-CimInstance Win32_OperatingSystem | Select-Object @{Name='TotalRAMGiB';Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}},@{Name='FreeRAMGiB';Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}} | Format-List"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance)

### `Top 20 RAM processes (PowerShell)`

- **What it does:** Lists the 20 processes with the largest working sets (resident physical memory) in MiB.
- **Best for:** Identifying applications currently occupying large amounts of physical RAM.
- **Notes / limits:** Working set is not total allocated memory or proof of a leak; some protected processes may not expose details.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 ProcessName,Id,@{Name='WorkingSetMiB';Expression={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process)

### `perfmon.exe`

- **What it does:** Opens Performance Monitor to review live counters and create performance data collection sets.
- **Best for:** Investigating intermittent resource bottlenecks with Windows performance counters.
- **Notes / limits:** Viewing is safe, but users can configure data collection inside the tool.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `perfmon.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

## Temporary files (7)

### `cleanmgr /d <Drive>`

- **What it does:** Opens the Disk Cleanup interface for the selected drive; you choose what categories to remove.
- **Best for:** Reclaiming disk space using Microsoft’s built-in review-and-confirm cleanup UI.
- **Notes / limits:** Review the selected categories carefully; some choices can delete Recycle Bin content or other data.
- **Safety:** Changes settings or writes files
- **Administrator:** Not required by the launcher · **Drive picker:** Required · **Restart:** No
- **Special input:** None
- **Command example:** `cleanmgr.exe /d C`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cleanmgr)

### `Storage Sense settings`

- **What it does:** Opens Windows Storage Sense settings to inspect automatic and manual space-cleanup options.
- **Best for:** Managing how Windows cleans temporary files and optionally the Recycle Bin or Downloads.
- **Notes / limits:** Page availability varies by Windows version. Changes made inside Settings can delete files.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `ms-settings:storagepolicies`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings)

### `Open current-user %TEMP% folder`

- **What it does:** Opens the current user’s temporary directory in File Explorer without deleting anything.
- **Best for:** Inspecting which applications have left temporary files on the PC.
- **Notes / limits:** Uses the current user TEMP path, not the drive dropdown; avoid deleting unknown or in-use files.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `explorer.exe C:\Windows\Temp`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `Measure user TEMP folder (PowerShell)`

- **What it does:** Counts accessible files inside the current user’s TEMP folder and estimates their total size in GiB.
- **Best for:** Checking how much storage temporary files are occupying before cleanup.
- **Notes / limits:** Read-only, but recursion can take time; inaccessible files and junction targets are not guaranteed to be counted.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-ChildItem -LiteralPath $env:TEMP -File -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum | Select-Object Count,@{Name='SizeGiB';Expression={[math]::Round($_.Sum/1GB,3)}} | Format-List"`
- **Reference:** [Microsoft documentation](https://support.microsoft.com/en-us/windows/manage-drive-space-with-storage-sense-654f6ada-7d1a-4e8d-8c28-2b5bba53a9d2)

### `Oldest user TEMP files (PowerShell)`

- **What it does:** Shows up to 20 accessible temporary files with the oldest modification dates, without deleting them.
- **Best for:** Investigating old temporary data prior to making cleanup decisions.
- **Notes / limits:** Age is based on modification time, not whether a file is safe to delete; paths and file names may contain private data.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-ChildItem -LiteralPath $env:TEMP -File -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -First 20 FullName,Length,LastWriteTime | Format-Table -Wrap"`
- **Reference:** [Microsoft documentation](https://support.microsoft.com/en-us/windows/manage-drive-space-with-storage-sense-654f6ada-7d1a-4e8d-8c28-2b5bba53a9d2)

### `wsreset.exe`

- **What it does:** Clears Microsoft Store’s local cache and may reopen Microsoft Store.
- **Best for:** Investigating Store loading or cache-related problems.
- **Notes / limits:** This is specifically the Store cache; it does not clean ordinary TEMP files. Store may take time to reopen.
- **Safety:** Changes settings or writes files
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `wsreset.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `DISM /StartComponentCleanup`

- **What it does:** Removes superseded component-store files from the running Windows installation to reduce their disk usage.
- **Best for:** Reducing Windows component-store size when DISM analysis shows cleanup can help.
- **Notes / limits:** Unlike scheduled cleanup, manually running this can immediately remove superseded component versions and limit rollback of older updates. Never manually delete WinSxS.
- **Safety:** Intensive / potentially disruptive
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dism.exe /Online /Cleanup-Image /StartComponentCleanup`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/clean-up-the-winsxs-folder)

## Startup & drivers (6)

### `Registered startup programs (PowerShell)`

- **What it does:** Lists startup entries exposed by the Win32_StartupCommand WMI class.
- **Best for:** Finding common Run-key and Startup-folder programs that launch with Windows.
- **Notes / limits:** Does not enumerate every startup mechanism, service, or scheduled task. Arguments may contain private information.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powershell.exe -NoProfile -Command "Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location,User | Format-Table -Wrap"`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance)

### `services.msc`

- **What it does:** Opens the Windows Services management console for inspecting service status and startup settings.
- **Best for:** Finding a service that fails to start or consumes resources.
- **Notes / limits:** Changing or disabling critical services inside this console can break Windows features.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `services.msc`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `devmgmt.msc`

- **What it does:** Opens Device Manager to inspect connected devices and installed drivers.
- **Best for:** Diagnosing missing, disabled or malfunctioning hardware drivers.
- **Notes / limits:** Uninstalling devices or drivers within Device Manager may disrupt hardware until repaired.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `devmgmt.msc`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `dxdiag.exe`

- **What it does:** Opens DirectX Diagnostic Tool for graphics, audio, drivers and DirectX information.
- **Best for:** Investigating graphics/game/audio incompatibilities or collecting device information.
- **Notes / limits:** Reports may contain machine identifiers; review before sharing.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `dxdiag.exe`
- **Reference:** Built-in Windows tool; behavior also depends on installed components.

### `pnputil /enum-devices /problem`

- **What it does:** Lists Plug and Play devices that currently report a device problem code.
- **Best for:** Investigating unrecognized hardware, disabled devices or drivers that did not start.
- **Notes / limits:** Available on Windows 10 version 1903 and newer. A problem code identifies a device state, not necessarily the root cause. Does not repair devices.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `pnputil.exe /enum-devices /problem`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax)

### `pnputil /enum-drivers`

- **What it does:** Lists third-party driver packages stored in the Windows driver store, including published INF names.
- **Best for:** Checking OEM driver packages and troubleshooting driver-version conflicts.
- **Notes / limits:** Shows driver-store packages, not a complete list of currently active device drivers. Does not install, remove or update drivers.
- **Safety:** Inspection / low risk
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `pnputil.exe /enum-drivers`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax)

## Power & battery (6)

### `powercfg /a`

- **What it does:** Reports sleep states available and unavailable on the current computer, with reasons.
- **Best for:** Checking whether Sleep, Hibernate or Modern Standby is supported.
- **Notes / limits:** Capabilities depend on device firmware, drivers and current Windows configuration.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powercfg.exe /a`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

### `powercfg /requests`

- **What it does:** Lists currently reported processes, drivers and services requesting that Windows stay awake.
- **Best for:** Troubleshooting sleep or display-off problems.
- **Notes / limits:** The output is a live snapshot; an empty list does not rule out all sleep problems. Admin may reveal more.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powercfg.exe /requests`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

### `powercfg /lastwake`

- **What it does:** Displays the last wake source that Windows was able to record.
- **Best for:** Finding why a PC recently woke up unexpectedly.
- **Notes / limits:** May show no useful source, depending on firmware, sleep state and Windows logging.
- **Safety:** Inspection / low risk
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** None
- **Command example:** `powercfg.exe /lastwake`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

### `powercfg /batteryreport /output <HTML file>`

- **What it does:** Generates an HTML battery usage and capacity report at a file location you choose.
- **Best for:** Reviewing battery capacity trends on laptops or tablets.
- **Notes / limits:** Most desktops without batteries have no meaningful battery history. This creates or overwrites the selected HTML file and may reveal device and usage information.
- **Safety:** Changes settings or writes files
- **Administrator:** Not required by the launcher · **Drive picker:** Locked · **Restart:** No
- **Special input:** HTML report destination
- **Command example:** `powercfg.exe /batteryreport /output C:\Users\Public\report.html`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

### `powercfg /energy /duration 60 /output <HTML file>`

- **What it does:** Runs a 60-second Windows power-efficiency analysis and writes an HTML report to a selected path.
- **Best for:** Finding power-efficiency problems when idle and troubleshooting battery drain.
- **Notes / limits:** Run while the system is otherwise idle. Requires admin, waits about 60 seconds and may flag benign warnings.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** HTML report destination
- **Command example:** `powercfg.exe /energy /duration 60 /output C:\Users\Public\report.html`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

### `powercfg /sleepstudy /output <HTML file>`

- **What it does:** Generates a report of Modern Standby sleep sessions, power usage and activity where supported.
- **Best for:** Investigating battery drain or poor Modern Standby behavior during sleep.
- **Notes / limits:** Requires Modern Standby-capable hardware and administrator permissions. Creates or overwrites the chosen HTML report; unsupported systems may report an error.
- **Safety:** Changes settings or writes files
- **Administrator:** Yes · **Drive picker:** Locked · **Restart:** No
- **Special input:** HTML report destination
- **Command example:** `powercfg.exe /sleepstudy /output C:\Users\Public\report.html`
- **Reference:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)

## Known platform restrictions

- PnPUtil `/enum-devices /problem` needs Windows 10 1903 or newer.
- WinGet may not be installed and may contact remote package sources or request source agreement. Listing does not install updates.
- SleepStudy requires Modern Standby hardware; PowerShell modules and device-specific counters may be missing.
- Disk and networking repair tools may need elevation, restart, backups and a maintenance window.
- `Test-NetConnection` sends network traffic to the user-selected host/port; it does not change system configuration.
- The firewall and DNS PowerShell modules may be unavailable or restricted on some systems; Defender detection history may be incomplete, and Windows Time service may not be running.
- Windows 10 reached end of general support in October 2025, but the toolkit can still launch its existing built-in utilities on supported configurations.

## Accuracy and testing

Descriptions and syntaxes were checked against Microsoft command documentation, and commands were tested through the toolkit's command builder and mocked Windows launch requests. Actual execution on Windows machines is still outstanding. See [`AUDIT_REPORT.md`](AUDIT_REPORT.md) and [`WINDOWS_TEST_PLAN.md`](WINDOWS_TEST_PLAN.md).
