"""Windows-only launcher. Uses a fixed command catalog, not a shell input box."""
from __future__ import annotations
import ctypes
import os
import ntpath
import string
import subprocess
from pathlib import Path

from command_catalog import Command, build_argv, validate_drive


def available_drives() -> list[str]:
    if os.name != 'nt':
        return ['C:']
    try:
        kernel = ctypes.windll.kernel32
        kernel.GetLogicalDrives.restype = ctypes.c_uint32
        kernel.GetDriveTypeW.argtypes = [ctypes.c_wchar_p]
        kernel.GetDriveTypeW.restype = ctypes.c_uint
        mask = kernel.GetLogicalDrives()
        found = []
        for i, letter in enumerate(string.ascii_uppercase):
            if (mask & (1 << i)) and kernel.GetDriveTypeW(f'{letter}:\\') in (2, 3):
                found.append(f'{letter}:')
        return found
    except Exception:
        # On Windows never fabricate C: if drive discovery fails. The UI
        # must disable volume-specific commands until discovery succeeds.
        return []


def is_admin() -> bool:
    if os.name != 'nt':
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def launch(command: Command, drive: str = 'C:', file_target: str | None = None, report_target: str | None = None, host_target: str = 'www.microsoft.com', port_target: str | int = '443') -> None:
    if os.name != 'nt':
        raise RuntimeError('Running system commands is only supported on Windows.')
    if command.uses_drive and validate_drive(drive) not in available_drives():
        raise ValueError('Selected drive is no longer present. Refresh the drive list.')
    argv = build_argv(command, drive, file_target, report_target, host_target, port_target)
    if command.needs_file and not Path(file_target).is_file():
        raise FileNotFoundError('The selected file no longer exists.')

    # The .msc management consoles are files opened through Microsoft MMC.
    if command.kind == 'gui' and argv[0].lower().endswith('.msc'):
        exe, params = 'mmc.exe', subprocess.list2cmdline([ntpath.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', argv[0])])
    elif command.kind == 'shell':
        # Shell URI: launch through the registered Windows protocol handler.
        exe, params = argv[0], None
    elif command.kind == 'gui':
        exe, params = argv[0], subprocess.list2cmdline(argv[1:])
    elif command.kind == 'powershell':
        # PowerShell expressions must not be sent through cmd.exe: its parser
        # interprets pipe and quote syntax differently from PowerShell.
        exe = argv[0]
        params = subprocess.list2cmdline(['-NoExit', *argv[1:]])
    else:
        # Whitelisted args only. Selected drive is regex-validated; selected
        # local file path is checked for cmd.exe metacharacters before use.
        exe = 'cmd.exe'
        params = '/k ' + subprocess.list2cmdline(argv)

    verb = 'runas' if command.admin else 'open'
    # ShellExecuteW returns an HINSTANCE-sized result, not a 32-bit int.
    # Set the return type explicitly so the result is interpreted correctly
    # on both 32-bit and 64-bit Windows.
    shell_execute = ctypes.windll.shell32.ShellExecuteW
    shell_execute.restype = ctypes.c_void_p
    result = shell_execute(None, verb, exe, params, None, 1)
    if not result or result <= 32:
        raise OSError(f'Windows declined to open the command (ShellExecute code {result}).')
