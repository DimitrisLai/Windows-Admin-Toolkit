"""Curated, fixed allowlist of supported Windows maintenance commands.

Nothing in this module reads arbitrary commands from files or user input.
Only a vetted drive letter (and an optionally selected local file) can vary.
"""
from __future__ import annotations

from dataclasses import dataclass
import ntpath
import ipaddress
import os
import re
import subprocess
from typing import Literal

Risk = Literal['read', 'change', 'heavy']
Kind = Literal['native', 'powershell', 'slmgr', 'gui', 'shell']


@dataclass(frozen=True)
class Command:
    id: str
    category: str
    label: str
    args: tuple[str, ...]
    description: str
    best_for: str
    notes: str
    admin: bool = False
    uses_drive: bool = False
    needs_file: bool = False
    needs_report: bool = False
    needs_network: bool = False
    risk: Risk = 'read'
    restart: str = 'No'
    kind: Kind = 'native'
    doc_url: str = ''


SFC = 'https://support.microsoft.com/en-us/windows/using-system-file-checker-in-windows-365e0031-36b1-611a-1a6b-3cb056aa98d1'
DISM = 'https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image?view=windows-11'
CHKDSK = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk'
IPCONFIG = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig'
NETSH = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh'
SLMGR = 'https://learn.microsoft.com/en-us/windows-server/get-started/activation-slmgr-vbs-options'
DISK = 'https://learn.microsoft.com/en-us/powershell/module/storage/get-physicaldisk'
VOLUME = 'https://learn.microsoft.com/en-us/powershell/module/storage/get-volume'
POWERSHELL_CIM = 'https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance'
GETPROCESS = 'https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process'
CLEANMGR = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cleanmgr'
STORAGE_SENSE = 'https://support.microsoft.com/en-us/windows/manage-drive-space-with-storage-sense-654f6ada-7d1a-4e8d-8c28-2b5bba53a9d2'
STORAGE_COUNTER = 'https://learn.microsoft.com/en-us/powershell/module/storage/get-storagereliabilitycounter'
DEFRAG = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/defrag'
FSUTIL = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-dirty'
BITLOCKER = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/manage-bde-status'
POWERCFG = 'https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options'
WIN_EVENT = 'https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-5.1'
NETSTAT = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat'
WLAN = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan'
DISM_CLEANUP = 'https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/clean-up-the-winsxs-folder'
REAGENTC = 'https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/reagentc-command-line-options'
PNPUTIL = 'https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax'
GET_ADAPTER = 'https://learn.microsoft.com/en-us/powershell/module/netadapter/get-netadapter'
TEST_NET = 'https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection'
WINGET = 'https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade'
GPRESULT = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult'
WINMGMT = 'https://learn.microsoft.com/en-us/windows/win32/wmisdk/winmgmt'
WHOAMI = 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami'



COMMANDS: tuple[Command, ...] = (
    Command('sfc.scan', 'Windows files', 'sfc /scannow', ('sfc.exe','/scannow'),
            'Scans protected Windows system files and replaces corrupted versions where possible.',
            'Windows crashes, missing system files, or recurring system errors.',
            'DISM /RestoreHealth may be useful first if the component store is damaged. A scan can take time.',
            admin=True, risk='change', doc_url=SFC),
    Command('sfc.verify', 'Windows files', 'sfc /verifyonly', ('sfc.exe','/verifyonly'),
            'Scans protected Windows files for integrity problems without repairing them.',
            'Checking for system file problems before attempting repairs.',
            'This is a read-only integrity check; any problems reported require a separate repair.',
            admin=True, doc_url=SFC),
    Command('sfc.file', 'Windows files', 'sfc /scanfile=<file>', ('sfc.exe','/scanfile={file}'),
            'Scans and, when possible, repairs one specified protected Windows system file.',
            'Checking a particular Windows system DLL or other protected file.',
            'Choose an existing local file. This is intended for protected system files, not ordinary documents.',
            admin=True, needs_file=True, risk='change', doc_url=SFC),
    Command('dism.check', 'Windows image (DISM)', 'DISM /Online /Cleanup-Image /CheckHealth',
            ('dism.exe','/Online','/Cleanup-Image','/CheckHealth'),
            'Quickly reports whether the Windows component store was previously flagged as corrupted.',
            'A fast preliminary Windows image health check.',
            'Does not perform a new deep scan and does not repair the component store.',
            admin=True, doc_url=DISM),
    Command('dism.scan', 'Windows image (DISM)', 'DISM /Online /Cleanup-Image /ScanHealth',
            ('dism.exe','/Online','/Cleanup-Image','/ScanHealth'),
            'Performs a more thorough scan of the running Windows component store for corruption.',
            'Diagnosing Windows image health when the quick check is insufficient.',
            'This may take several minutes. It scans but does not repair the image.',
            admin=True, doc_url=DISM),
    Command('dism.restore', 'Windows image (DISM)', 'DISM /Online /Cleanup-Image /RestoreHealth',
            ('dism.exe','/Online','/Cleanup-Image','/RestoreHealth'),
            'Repairs corruption in the running Windows component store using available repair sources.',
            'Fixing a damaged component store, especially before running SFC.',
            'May use Windows Update to obtain repair files. Offline or restricted machines may need a /Source.',
            admin=True, risk='change', doc_url=DISM),
    Command('dism.analyze', 'Windows image (DISM)', 'DISM /Online /Cleanup-Image /AnalyzeComponentStore',
            ('dism.exe','/Online','/Cleanup-Image','/AnalyzeComponentStore'),
            'Analyzes Windows component store size and reports whether cleanup is recommended.',
            'Investigating component store disk usage without making changes.',
            'A cleanup recommendation is informational; this command does not delete files.',
            admin=True, doc_url=DISM),
    Command('disk.check', 'Disk & storage', 'chkdsk <Drive>', ('chkdsk.exe','{drive}'),
            'Checks file system status on the selected local volume without requesting repairs.',
            'A preliminary review of suspected file system errors.',
            'Read-only checks on active volumes may report transient discrepancies. Local volumes only.',
            admin=True, uses_drive=True, doc_url=CHKDSK),
    Command('disk.scan', 'Disk & storage', 'chkdsk <Drive> /scan', ('chkdsk.exe','{drive}','/scan'),
            'Runs an online NTFS scan of the selected local volume.',
            'Checking an NTFS drive with less disruption than an offline repair.',
            'NTFS only. Some problems may still require offline repair or a restart.',
            admin=True, uses_drive=True, doc_url=CHKDSK),
    Command('disk.fix', 'Disk & storage', 'chkdsk <Drive> /f', ('chkdsk.exe','{drive}','/f'),
            'Fixes file system errors on the selected local volume.',
            'Repairing confirmed file system problems.',
            'May ask to schedule a check at reboot when the volume is in use. Back up important files first.',
            admin=True, uses_drive=True, risk='change', restart='May be required', doc_url=CHKDSK),
    Command('disk.recover', 'Disk & storage', 'chkdsk <Drive> /f /r', ('chkdsk.exe','{drive}','/f','/r'),
            'Checks file system errors, scans for bad sectors and attempts to recover readable data.',
            'Investigating storage read errors or suspected bad sectors.',
            'Potentially very slow and intensive. Back up important data first; on a failing drive prioritize recovery.',
            admin=True, uses_drive=True, risk='heavy', restart='May be required', doc_url=CHKDSK),
    Command('disk.health', 'Disk & storage', 'Get-PhysicalDisk (health status)',
            ('Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,Size | Format-Table -AutoSize',),
            'Displays disk health and operational statuses reported by Windows storage providers.',
            'A modern first look at reported physical disk health.',
            'Replaces obsolete WMIC. Not a complete SMART diagnosis; reported Healthy is not proof a disk is fault-free.',
            kind='powershell', doc_url=DISK),
    Command('disk.volumes', 'Disk & storage', 'Get-Volume -DriveLetter <Drive>',
            ('Get-Volume -DriveLetter {drive_letter} | Format-List DriveLetter,FileSystem,FileSystemLabel,HealthStatus,Size,SizeRemaining',),
            'Shows Windows storage and file system information for the selected volume.',
            'Checking the volume file system, Windows health status, and free space.',
            'Some provider fields may be unavailable for particular volumes.',
            kind='powershell', uses_drive=True, doc_url=VOLUME),
    Command('memory', 'Hardware & diagnostics', 'mdsched.exe', ('mdsched.exe',),
            'Opens Windows Memory Diagnostic and offers to test RAM at the next reboot.',
            'Suspected RAM-related blue screens, instability, or random crashes.',
            'Opening this tool does not immediately restart the PC; Windows asks you to choose a testing time.',
            admin=True, risk='change', restart='User chooses', kind='gui'),
    Command('sys.info', 'Hardware & diagnostics', 'systeminfo', ('systeminfo.exe',),
            'Prints detailed information about Windows, hardware, patches, and boot time.',
            'Collecting useful system specifications for support and troubleshooting.',
            'Output can contain computer names and other system details; review before sharing.',
            doc_url='https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo'),
    Command('sys.fullinfo', 'Hardware & diagnostics', 'msinfo32', ('msinfo32.exe',),
            'Opens System Information with hardware resources, drivers, and OS details.',
            'Investigating a machine configuration through a graphical tool.',
            'Read-only viewer. Information may take a moment to load.', kind='gui'),
    Command('lic.expiration', 'Activation & licensing', 'slmgr /xpr', ('/xpr',),
            'Reports whether the current Windows activation is permanent or expires.',
            'Confirming activation expiration state.',
            'Uses Microsoft slmgr.vbs through cscript; does not activate Windows or change a license.',
            kind='slmgr', doc_url=SLMGR),
    Command('lic.details', 'Activation & licensing', 'slmgr /dlv', ('/dlv',),
            'Shows detailed Windows licensing and activation information.',
            'Diagnosing legitimate Windows licensing issues.',
            'Output includes licensing identifiers. Review before sharing publicly.', kind='slmgr', doc_url=SLMGR),
    Command('net.all', 'Networking', 'ipconfig /all', ('ipconfig.exe','/all'),
            'Displays network adapter addresses, DNS settings, DHCP details, and related configuration.',
            'Finding local network configuration and troubleshooting connection issues.',
            'Displays local networking identifiers; review before sharing.', doc_url=IPCONFIG),
    Command('net.flush', 'Networking', 'ipconfig /flushdns', ('ipconfig.exe','/flushdns'),
            'Clears the local DNS resolver cache.',
            'Troubleshooting stale or incorrect cached DNS results.',
            'Does not reset network adapters or change network configuration.',
            risk='change', doc_url=IPCONFIG),
    Command('net.register', 'Networking', 'ipconfig /registerdns', ('ipconfig.exe','/registerdns'),
            'Initiates DNS registration for eligible network adapter records.',
            'Troubleshooting DNS registration on appropriately configured networks.',
            'May be irrelevant on typical home devices; DNS registration can depend on domain/network policy.',
            admin=True, risk='change', doc_url=IPCONFIG),
    Command('net.winsock', 'Networking', 'netsh winsock reset', ('netsh.exe','winsock','reset'),
            'Resets the Winsock catalog to its default state.',
            'Investigating persistent networking issues that may involve Winsock providers.',
            'Changes networking configuration. Can affect third-party network components; reboot is usually necessary.',
            admin=True, risk='change', restart='Usually required', doc_url=NETSH),
    Command('net.ipreset', 'Networking', 'netsh int ip reset', ('netsh.exe','int','ip','reset'),
            'Resets TCP/IP settings to Windows defaults.',
            'Repairing serious network stack configuration issues.',
            'May remove custom network settings (including static configuration); record settings first. Reboot afterward.',
            admin=True, risk='heavy', restart='Usually required', doc_url=NETSH),
    Command('diag.reliability', 'Logs & monitoring', 'perfmon /rel', ('perfmon.exe','/rel'),
            'Opens Reliability Monitor, showing application and Windows failures over time.',
            'Finding which crashes or failures occurred around a particular date.',
            'A useful first stop for recurring crashes and application errors.', kind='gui'),
    Command('diag.events', 'Logs & monitoring', 'eventvwr.msc', ('eventvwr.msc',),
            'Opens Windows Event Viewer to inspect system, application, and security logs.',
            'Examining warnings and failures after a specific problem.',
            'Many events are routine; focus on events matching the actual time of the issue.', kind='gui'),
    Command('diag.taskmgr', 'Logs & monitoring', 'taskmgr', ('taskmgr.exe',),
            'Opens Task Manager to view running processes and resource usage.',
            'Investigating unusually high CPU, RAM, disk, or network use.',
            'Opening Task Manager is safe; avoid ending unknown processes.', kind='gui'),
    # RAM & performance (5)
    Command('ram.resmon', 'RAM & performance', 'resmon.exe', ('resmon.exe',),
            'Opens Resource Monitor to inspect per-process memory usage plus CPU, disk and networking activity.',
            'Finding applications consuming RAM and investigating resource pressure.',
            'Resource Monitor is an interactive viewer; high cached RAM alone does not mean memory is faulty.', kind='gui'),
    Command('ram.modules', 'RAM & performance', 'Installed RAM modules (PowerShell)',
            ('Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Manufacturer,@{Name=\'CapacityGB\';Expression={[math]::Round($_.Capacity/1GB,2)}},Speed,PartNumber | Format-Table -AutoSize',),
            'Lists memory module slots, manufacturers, module capacities in GiB, rated speeds, and part numbers as reported by firmware.',
            'Confirming installed RAM size and investigating module differences.',
            'Reported module details depend on BIOS/firmware; reported Speed is not a benchmark.', kind='powershell', doc_url=POWERSHELL_CIM),
    Command('ram.free', 'RAM & performance', 'Installed and free RAM (PowerShell)',
            ('Get-CimInstance Win32_OperatingSystem | Select-Object @{Name=\'TotalRAMGiB\';Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}},@{Name=\'FreeRAMGiB\';Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}} | Format-List',),
            'Reports total usable and currently free physical RAM in GiB using values that Windows exposes in KiB.',
            'Checking whether Windows currently has little free physical memory.',
            'Free physical memory changes constantly; Windows also intentionally uses memory for caching.', kind='powershell', doc_url=POWERSHELL_CIM),
    Command('ram.top', 'RAM & performance', 'Top 20 RAM processes (PowerShell)',
            ('Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 ProcessName,Id,@{Name=\'WorkingSetMiB\';Expression={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize',),
            'Lists the 20 processes with the largest working sets (resident physical memory) in MiB.',
            'Identifying applications currently occupying large amounts of physical RAM.',
            'Working set is not total allocated memory or proof of a leak; some protected processes may not expose details.', kind='powershell', doc_url=GETPROCESS),
    Command('ram.perfmon', 'RAM & performance', 'perfmon.exe', ('perfmon.exe',),
            'Opens Performance Monitor to review live counters and create performance data collection sets.',
            'Investigating intermittent resource bottlenecks with Windows performance counters.',
            'Viewing is safe, but users can configure data collection inside the tool.', kind='gui'),

    # Temporary files (7)
    Command('temp.cleanmgr', 'Temporary files', 'cleanmgr /d <Drive>', ('cleanmgr.exe','/d','{drive_letter}'),
            'Opens the Disk Cleanup interface for the selected drive; you choose what categories to remove.',
            'Reclaiming disk space using Microsoft’s built-in review-and-confirm cleanup UI.',
            'Review the selected categories carefully; some choices can delete Recycle Bin content or other data.',
            uses_drive=True, kind='gui', risk='change', doc_url=CLEANMGR),
    Command('temp.storagesense', 'Temporary files', 'Storage Sense settings', ('ms-settings:storagepolicies',),
            'Opens Windows Storage Sense settings to inspect automatic and manual space-cleanup options.',
            'Managing how Windows cleans temporary files and optionally the Recycle Bin or Downloads.',
            'Page availability varies by Windows version. Changes made inside Settings can delete files.', kind='shell', doc_url='https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings'),
    Command('temp.folder', 'Temporary files', 'Open current-user %TEMP% folder', ('explorer.exe','{temp_dir}'),
            'Opens the current user’s temporary directory in File Explorer without deleting anything.',
            'Inspecting which applications have left temporary files on the PC.',
            'Uses the current user TEMP path, not the drive dropdown; avoid deleting unknown or in-use files.', kind='gui'),
    Command('temp.size', 'Temporary files', 'Measure user TEMP folder (PowerShell)',
            ('Get-ChildItem -LiteralPath $env:TEMP -File -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum | Select-Object Count,@{Name=\'SizeGiB\';Expression={[math]::Round($_.Sum/1GB,3)}} | Format-List',),
            'Counts accessible files inside the current user’s TEMP folder and estimates their total size in GiB.',
            'Checking how much storage temporary files are occupying before cleanup.',
            'Read-only, but recursion can take time; inaccessible files and junction targets are not guaranteed to be counted.', kind='powershell', doc_url=STORAGE_SENSE),
    Command('temp.oldest', 'Temporary files', 'Oldest user TEMP files (PowerShell)',
            ('Get-ChildItem -LiteralPath $env:TEMP -File -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -First 20 FullName,Length,LastWriteTime | Format-Table -Wrap',),
            'Shows up to 20 accessible temporary files with the oldest modification dates, without deleting them.',
            'Investigating old temporary data prior to making cleanup decisions.',
            'Age is based on modification time, not whether a file is safe to delete; paths and file names may contain private data.', kind='powershell', doc_url=STORAGE_SENSE),
    Command('temp.store', 'Temporary files', 'wsreset.exe', ('wsreset.exe',),
            'Clears Microsoft Store’s local cache and may reopen Microsoft Store.',
            'Investigating Store loading or cache-related problems.',
            'This is specifically the Store cache; it does not clean ordinary TEMP files. Store may take time to reopen.', kind='gui', risk='change'),
    Command('temp.component', 'Temporary files', 'DISM /StartComponentCleanup',
            ('dism.exe','/Online','/Cleanup-Image','/StartComponentCleanup'),
            'Removes superseded component-store files from the running Windows installation to reduce their disk usage.',
            'Reducing Windows component-store size when DISM analysis shows cleanup can help.',
            'Unlike scheduled cleanup, manually running this can immediately remove superseded component versions and limit rollback of older updates. Never manually delete WinSxS.',
            admin=True, risk='heavy', doc_url=DISM_CLEANUP),

    # Storage and disk health (5)
    Command('disk.counters', 'Disk & storage', 'Disk reliability counters (PowerShell)',
            ('Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId,Temperature,Wear,ReadErrorsTotal,WriteErrorsTotal | Format-Table -AutoSize',),
            'Displays available temperature, wear and read/write error counters from compatible physical disks.',
            'Looking for reported SSD/HDD temperature, lifetime and media-error warning signals.',
            'A blank value can mean unsupported hardware or drivers, not zero; Windows storage providers vary. No complete SMART test.',
            kind='powershell', doc_url=STORAGE_COUNTER),
    Command('disk.analyze', 'Disk & storage', 'defrag <Drive> /A /V', ('defrag.exe','{drive}','/A','/V'),
            'Analyzes the selected volume’s optimization status and prints detailed information without optimizing it.',
            'Checking whether Windows considers a drive in need of optimization.',
            'Administrator permission may be needed. This is not a disk integrity or SMART test.',
            admin=True, uses_drive=True, doc_url=DEFRAG),
    Command('disk.optimize', 'Disk & storage', 'defrag <Drive> /O /V', ('defrag.exe','{drive}','/O','/V'),
            'Asks Windows to select the appropriate optimization for the volume’s media type.',
            'Optimizing an HDD or requesting supported SSD retrim/maintenance using Windows defaults.',
            'Can take time and generate disk activity. /O chooses appropriate behavior; do not assume it always performs traditional defragmentation.',
            admin=True, uses_drive=True, risk='change', doc_url=DEFRAG),
    Command('disk.dirty', 'Disk & storage', 'fsutil dirty query <Drive>', ('fsutil.exe','dirty','query','{drive}'),
            'Queries the volume dirty bit, which indicates Windows may need to check the file system.',
            'Investigating a volume that Windows flags for a check during startup.',
            'A dirty bit does not by itself diagnose the cause. Some volumes/filesystems are unsupported; admin may be required.',
            admin=True, uses_drive=True, doc_url=FSUTIL),
    Command('disk.bitlocker', 'Disk & storage', 'manage-bde -status <Drive>', ('manage-bde.exe','-status','{drive}'),
            'Shows BitLocker encryption, conversion and protection status for the selected volume.',
            'Verifying whether a volume is encrypted or protected before storage troubleshooting.',
            'Status output can reveal identifying volume details, but this command does not display BitLocker recovery passwords.',
            uses_drive=True, doc_url=BITLOCKER),

    # Startup / drivers (4)
    Command('boot.startup', 'Startup & drivers', 'Registered startup programs (PowerShell)',
            ('Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location,User | Format-Table -Wrap',),
            'Lists startup entries exposed by the Win32_StartupCommand WMI class.',
            'Finding common Run-key and Startup-folder programs that launch with Windows.',
            'Does not enumerate every startup mechanism, service, or scheduled task. Arguments may contain private information.',
            kind='powershell', doc_url=POWERSHELL_CIM),
    Command('boot.services', 'Startup & drivers', 'services.msc', ('services.msc',),
            'Opens the Windows Services management console for inspecting service status and startup settings.',
            'Finding a service that fails to start or consumes resources.',
            'Changing or disabling critical services inside this console can break Windows features.', kind='gui'),
    Command('boot.devices', 'Startup & drivers', 'devmgmt.msc', ('devmgmt.msc',),
            'Opens Device Manager to inspect connected devices and installed drivers.',
            'Diagnosing missing, disabled or malfunctioning hardware drivers.',
            'Uninstalling devices or drivers within Device Manager may disrupt hardware until repaired.', kind='gui'),
    Command('boot.dxdiag', 'Startup & drivers', 'dxdiag.exe', ('dxdiag.exe',),
            'Opens DirectX Diagnostic Tool for graphics, audio, drivers and DirectX information.',
            'Investigating graphics/game/audio incompatibilities or collecting device information.',
            'Reports may contain machine identifiers; review before sharing.', kind='gui'),

    # Network (4)
    Command('net.dnscache', 'Networking', 'ipconfig /displaydns', ('ipconfig.exe','/displaydns'),
            'Displays the Windows DNS Client resolver cache entries currently stored locally.',
            'Seeing whether recent DNS lookups or negative DNS cache entries exist.',
            'May reveal sites or services accessed by applications; DNS entries are not a reliable browser-history record.',
            doc_url=IPCONFIG),
    Command('net.wlan', 'Networking', 'netsh wlan show interfaces', ('netsh.exe','wlan','show','interfaces'),
            'Shows Wi-Fi interface details such as connection state, radio type and current signal level.',
            'Investigating wireless signal or connection issues on a PC with Wi-Fi.',
            'Requires Windows WLAN AutoConfig and compatible Wi-Fi hardware; no Wi-Fi interface means no useful data.', doc_url=WLAN),
    Command('net.wlanreport', 'Networking', 'netsh wlan show wlanreport', ('netsh.exe','wlan','show','wlanreport'),
            'Generates a local HTML report of recent Windows Wi-Fi connection events and failures.',
            'Diagnosing intermittent Wi-Fi disconnects and connection errors.',
            'Creates report files on disk (often under ProgramData); administrator access is recommended. Reports may contain SSIDs and device identifiers.',
            admin=True, risk='change', doc_url=WLAN),
    Command('net.netstat', 'Networking', 'netstat -ano', ('netstat.exe','-ano'),
            'Lists active TCP connections, listening TCP/UDP ports, numerical endpoints and owning process IDs.',
            'Investigating unexpected network listeners or finding which PID owns a connection.',
            'Snapshot only; PID identifies a process but does not establish whether traffic is malicious.', doc_url=NETSTAT),

    # Power and battery (5)
    Command('power.states', 'Power & battery', 'powercfg /a', ('powercfg.exe','/a'),
            'Reports sleep states available and unavailable on the current computer, with reasons.',
            'Checking whether Sleep, Hibernate or Modern Standby is supported.',
            'Capabilities depend on device firmware, drivers and current Windows configuration.', doc_url=POWERCFG),
    Command('power.requests', 'Power & battery', 'powercfg /requests', ('powercfg.exe','/requests'),
            'Lists currently reported processes, drivers and services requesting that Windows stay awake.',
            'Troubleshooting sleep or display-off problems.',
            'The output is a live snapshot; an empty list does not rule out all sleep problems. Admin may reveal more.',
            doc_url=POWERCFG),
    Command('power.wake', 'Power & battery', 'powercfg /lastwake', ('powercfg.exe','/lastwake'),
            'Displays the last wake source that Windows was able to record.',
            'Finding why a PC recently woke up unexpectedly.',
            'May show no useful source, depending on firmware, sleep state and Windows logging.', doc_url=POWERCFG),
    Command('power.battery', 'Power & battery', 'powercfg /batteryreport /output <HTML file>',
            ('powercfg.exe','/batteryreport','/output','{report}'),
            'Generates an HTML battery usage and capacity report at a file location you choose.',
            'Reviewing battery capacity trends on laptops or tablets.',
            'Most desktops without batteries have no meaningful battery history. This creates or overwrites the selected HTML file and may reveal device and usage information.',
            needs_report=True, risk='change', doc_url=POWERCFG),
    Command('power.energy', 'Power & battery', 'powercfg /energy /duration 60 /output <HTML file>',
            ('powercfg.exe','/energy','/duration','60','/output','{report}'),
            'Runs a 60-second Windows power-efficiency analysis and writes an HTML report to a selected path.',
            'Finding power-efficiency problems when idle and troubleshooting battery drain.',
            'Run while the system is otherwise idle. Requires admin, waits about 60 seconds and may flag benign warnings.',
            needs_report=True, admin=True, risk='change', doc_url=POWERCFG),

    # Events, updates, security, recovery (4)
    Command('diag.syserrors', 'Logs & monitoring', 'System error events: last 7 days (PowerShell)',
            ('Get-WinEvent -FilterHashtable @{LogName=\'System\';Level=2;StartTime=(Get-Date).AddDays(-7)} -MaxEvents 30 | Select-Object TimeCreated,Id,ProviderName,Message | Format-List',),
            'Shows up to 30 error-level events from the System log in the past seven days, newest first.',
            'Finding errors close to a Windows crash, hardware fault or unexpected restart.',
            'No matching events is not proof the PC is healthy. Reading some event logs may require elevation.',
            kind='powershell', doc_url=WIN_EVENT),
    Command('diag.hotfixes', 'Logs & monitoring', 'Recent hotfix records (PowerShell)',
            ('Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 15 HotFixID,InstalledOn,Description | Format-Table -AutoSize',),
            'Lists up to 15 Windows hotfix records in descending installed-date order.',
            'Checking recently recorded servicing changes while troubleshooting.',
            'Get-HotFix does not list every feature update, driver update or Microsoft Store update; some dates may be missing.',
            kind='powershell', doc_url='https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix'),
    Command('diag.recovery', 'Logs & monitoring', 'reagentc /info', ('reagentc.exe','/info'),
            'Shows whether Windows Recovery Environment is enabled and where its recovery image is configured.',
            'Checking recovery readiness before attempting advanced Windows repairs.',
            'Read-only command; some systems require administrator permissions to access all details.',
            admin=True, doc_url=REAGENTC),
    Command('diag.defender', 'Logs & monitoring', 'Microsoft Defender status (PowerShell)',
            ('Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated | Format-List',),
            'Displays current antivirus and real-time protection status and signature-update date when Defender is available.',
            'Checking whether Microsoft Defender protection and signature updates are active.',
            'Third-party antivirus products, security policy or Defender component availability can affect results.',
            kind='powershell', doc_url='https://learn.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=windowsserver2025-ps'),

    # Public beta: nine additional diagnostic/reference commands (read-only
    # except SleepStudy, which creates or overwrites a user-selected HTML file).
    Command('boot.pnp_problems', 'Startup & drivers', 'pnputil /enum-devices /problem',
            ('pnputil.exe','/enum-devices','/problem'),
            'Lists Plug and Play devices that currently report a device problem code.',
            'Investigating unrecognized hardware, disabled devices or drivers that did not start.',
            'Available on Windows 10 version 1903 and newer. A problem code identifies a device state, not necessarily the root cause. Does not repair devices.',
            admin=True, doc_url=PNPUTIL),
    Command('boot.pnp_drivers', 'Startup & drivers', 'pnputil /enum-drivers',
            ('pnputil.exe','/enum-drivers'),
            'Lists third-party driver packages stored in the Windows driver store, including published INF names.',
            'Checking OEM driver packages and troubleshooting driver-version conflicts.',
            'Shows driver-store packages, not a complete list of currently active device drivers. Does not install, remove or update drivers.',
            admin=True, doc_url=PNPUTIL),
    Command('net.adapters', 'Networking', 'Get-NetAdapter (PowerShell)',
            ('Get-NetAdapter | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress | Format-Table -AutoSize',),
            'Lists visible network adapters with their status, reported link speed and MAC address.',
            'Checking whether Windows sees a wired or wireless adapter and whether its link is up.',
            'Virtual adapters may be included; a connected link is not proof that internet access works. MAC addresses are identifying data.',
            kind='powershell', doc_url=GET_ADAPTER),
    Command('net.test_connection', 'Networking', 'Test-NetConnection <host> -Port <port>',
            ('Test-NetConnection -ComputerName {host} -Port {port} -InformationLevel Detailed | Format-List',),
            'Attempts a TCP connection to the specified host and port; shows DNS, routing and TCP test results.',
            'Testing if a specific website/server port (for example HTTPS 443) is reachable.',
            'Enter a trusted hostname or IP address and port (1–65535). A failed result may be caused by a firewall or remote-service policy, not necessarily by your PC. Makes outbound network traffic.',
            kind='powershell', needs_network=True, doc_url=TEST_NET),
    Command('diag.winget', 'Logs & monitoring', 'winget upgrade (list only)',
            ('winget.exe','upgrade'),
            'Lists installed applications for which WinGet identifies available updates; does not install them.',
            'Checking application update opportunities before updating anything.',
            'Requires Windows Package Manager (App Installer). Depending on source configuration, WinGet may access the network or request agreement acceptance. This is not Windows Update.',
            doc_url=WINGET),
    Command('power.sleepstudy', 'Power & battery', 'powercfg /sleepstudy /output <HTML file>',
            ('powercfg.exe','/sleepstudy','/output','{report}'),
            'Generates a report of Modern Standby sleep sessions, power usage and activity where supported.',
            'Investigating battery drain or poor Modern Standby behavior during sleep.',
            'Requires Modern Standby-capable hardware and administrator permissions. Creates or overwrites the chosen HTML report; unsupported systems may report an error.',
            admin=True, needs_report=True, risk='change', doc_url=POWERCFG),
    Command('diag.group_policy', 'Logs & monitoring', 'gpresult /r',
            ('gpresult.exe','/r'),
            'Shows summary information about applied Group Policy settings for the current user and computer when accessible.',
            'Troubleshooting organizational restrictions and unexpected policy-controlled settings.',
            'The current user context matters: elevation as a different administrator can show a different user. Some computer data may require elevation; personal PCs may have little policy information.',
            doc_url=GPRESULT),
    Command('diag.wmi_verify', 'Hardware & diagnostics', 'winmgmt /verifyrepository',
            ('winmgmt.exe','/verifyrepository'),
            'Checks the consistency of the live Windows Management Instrumentation (WMI) repository.',
            'Investigating suspected WMI repository corruption behind failing management queries.',
            'Verification does not repair or reset WMI. An inconsistent result needs careful diagnosis; do not automatically reset the repository.',
            admin=True, doc_url=WINMGMT),
    Command('diag.whoami', 'Hardware & diagnostics', 'whoami /all',
            ('whoami.exe','/all'),
            'Displays the security identifiers, groups and privileges in the current process access token.',
            'Understanding which account and privileges a command window actually has.',
            'Results can differ between standard and elevated launches. Output includes SIDs and security-group membership; review before sharing.',
            doc_url=WHOAMI),

)

BY_ID = {c.id: c for c in COMMANDS}


def validate_drive(drive: str) -> str:
    """A drive letter, never an arbitrary command fragment."""
    if not re.fullmatch(r'[A-Za-z]:', drive):
        raise ValueError('Drive must be a single letter followed by a colon, e.g. C:')
    return drive.upper()


def validate_file_target(path: str) -> str:
    """Only absolute local paths with no cmd.exe metacharacters are allowed."""
    if not isinstance(path, str) or not re.match(r'^[a-zA-Z]:\\', path):
        raise ValueError('Select an absolute local Windows file path (for example C:\\Windows\\System32\\file.dll).')
    if any(c in path for c in ('%', '!', '^', '&', '|', '<', '>', '"', '\r', '\n')):
        raise ValueError('The selected path has characters unsupported by the safe command launcher.')
    normalized = ntpath.normpath(path)
    if not re.match(r'^[A-Za-z]:\\', normalized) or normalized.endswith('\\'):
        raise ValueError('Select an individual file, not a directory.')
    return normalized


def validate_report_target(path: str) -> str:
    """Allow only local .html paths compatible with the Windows command launcher."""
    if not isinstance(path, str) or not re.match(r'^[A-Za-z]:\\', path):
        raise ValueError('Please select a local absolute HTML file path.')
    # The app invokes a fixed command line via cmd.exe; prohibit its expansion and control syntax.
    if any(c in path for c in ('%', '!', '^', '&', '|', '<', '>', '"', '\r', '\n')):
        raise ValueError('The selected report file path contains unsupported command characters.')
    normalized = ntpath.normpath(path)
    if not normalized.lower().endswith('.html') or ntpath.basename(normalized) in ('.', '..'):
        raise ValueError('The report filename must end in .html.')
    if len(normalized) > 240:
        raise ValueError('Choose a shorter report path for legacy Windows tools.')
    return normalized


def validate_network_host(host: str) -> str:
    """Allow only literal IP addresses or conservatively validated ASCII DNS names.

    Never embed arbitrary user input in a PowerShell -Command expression.
    """
    if not isinstance(host, str) or host != host.strip() or not host or len(host) > 253:
        raise ValueError('Enter a valid host name or IP address (without spaces).')
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass
    labels = host.split('.')
    if not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', x) for x in labels):
        raise ValueError('Enter an ASCII hostname or IP address; no URLs, scripts or spaces.')
    return host


def validate_network_port(port: str | int) -> int:
    if not isinstance(port, (str, int)) or not re.fullmatch(r'[0-9]{1,5}', str(port)):
        raise ValueError('Enter a TCP port from 1 to 65535.')
    number = int(port)
    if not 1 <= number <= 65535:
        raise ValueError('Enter a TCP port from 1 to 65535.')
    return number


def build_argv(command: Command, drive: str = 'C:', file_target: str | None = None, report_target: str | None = None, host_target: str = 'www.microsoft.com', port_target: str | int = '443') -> list[str]:
    if command.uses_drive:
        drive = validate_drive(drive)
    if command.needs_file:
        if not file_target:
            raise ValueError('Choose a system file before using this command.')
        file_target = validate_file_target(file_target)
    if command.needs_report:
        if not report_target:
            raise ValueError('Choose a location for the HTML report first.')
        report_target = validate_report_target(report_target)
    if command.needs_network:
        host_target = validate_network_host(host_target)
        port_target = str(validate_network_port(port_target))
    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or r'C:\Windows\Temp'
    rendered = [part.replace('{drive}', drive)
                    .replace('{drive_letter}', drive[:1])
                    .replace('{file}', file_target or '')
                    .replace('{report}', report_target or '')
                    .replace('{temp_dir}', temp_dir)
                    .replace('{host}', host_target)
                    .replace('{port}', str(port_target))
                for part in command.args]
    if command.kind == 'powershell':
        return ['powershell.exe', '-NoProfile', '-Command', rendered[0]]
    if command.kind == 'slmgr':
        return ['cscript.exe', '//nologo', ntpath.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'slmgr.vbs'), *rendered]
    return rendered


def display_command(command: Command, drive: str = 'C:', file_target: str | None = None, report_target: str | None = None, host_target: str = 'www.microsoft.com', port_target: str | int = '443') -> str:
    if command.needs_file and not file_target:
        return 'sfc /scanfile=<choose a file>'
    if command.needs_report and not report_target:
        return command.label
    argv = build_argv(command, drive, file_target, report_target, host_target, port_target)
    if command.kind == 'shell':
        return argv[0]
    if command.kind == 'gui':
        return subprocess.list2cmdline(argv)
    return subprocess.list2cmdline(argv)


def categories() -> list[str]:
    return list(dict.fromkeys(c.category for c in COMMANDS))
