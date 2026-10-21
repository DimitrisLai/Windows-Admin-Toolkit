"""Conservative user TEMP inspector and *selected-file-only* cleanup.

Never deletes directories, follows reparse points, or selects files automatically.
Not a replacement for Windows Storage Sense / Disk Cleanup.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import heapq
import ntpath
import os
from pathlib import Path
import queue
import stat
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk


MAX_DISPLAY = 300
REPARSE_POINT = 0x400


@dataclass(frozen=True)
class TempFile:
    path: str
    size: int
    mtime_ns: int
    inode: int


@dataclass(frozen=True)
class ScanResult:
    files: tuple[TempFile, ...]
    eligible_files: int
    eligible_bytes: int
    skipped: int


def user_temp_root() -> str:
    return os.environ.get('TEMP') or os.environ.get('TMP') or tempfile.gettempdir()


def _is_reparse(path: str) -> bool:
    try:
        info = os.lstat(path)
        return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & REPARSE_POINT)
    except OSError:
        return True


def _is_expected_user_temp_path(root: str, local_app_data: str | None) -> bool:
    """Accept only the current user's LocalAppData/Temp tree on Windows.

    A process can have a custom TEMP environment variable. The cleaner must
    not interpret such a path as permission to delete files in unrelated
    folders (for example, Documents, Program Files, or another user profile).
    A per-session subfolder beneath Temp is permitted.
    """
    if not local_app_data:
        return False
    root = ntpath.normcase(ntpath.normpath(root))
    local_app_data = ntpath.normcase(ntpath.normpath(local_app_data))
    expected = ntpath.join(local_app_data, 'temp')
    try:
        return ntpath.commonpath([root, expected]) == expected
    except ValueError:
        return False


def _validate_temp_root(root: str) -> str:
    if not root or not os.path.isdir(root) or _is_reparse(root):
        raise ValueError('The current-user TEMP directory is missing or is a link/junction.')
    real = os.path.normcase(os.path.abspath(root))
    if real in (os.path.normcase(os.path.abspath(os.path.sep)),
                os.path.normcase(os.path.abspath(os.path.expanduser('~')))):
        raise ValueError('Refusing to use a filesystem root or entire user profile as TEMP.')
    if os.name == 'nt':
        if not _is_expected_user_temp_path(real, os.environ.get('LOCALAPPDATA')):
            raise ValueError('For safety, this cleaner only supports the current-user %LOCALAPPDATA%\\Temp folder (or its subfolders). Use Windows Disk Cleanup / Storage Sense for other locations.')
        drive, tail = os.path.splitdrive(real)
        if not drive or tail in ('', '\\'):
            raise ValueError('Refusing to use a drive root for cleanup.')
        windows_dir = os.path.normcase(os.path.abspath(os.environ.get('SystemRoot', r'C:\Windows')))
        if (real == windows_dir or real == os.path.dirname(windows_dir) or
            os.path.commonpath([real, windows_dir]) == windows_dir):
            raise ValueError('Refusing to clean a Windows system directory.')
    return real


def _safe_child(root: str, path: str) -> bool:
    try:
        candidate = os.path.normcase(os.path.abspath(path))
        if os.path.commonpath([root, candidate]) != root or candidate == root:
            return False
        current = os.path.dirname(candidate)
        while current != root:
            if _is_reparse(current):
                return False
            parent = os.path.dirname(current)
            if parent == current:
                return False
            current = parent
        return not _is_reparse(candidate)
    except (ValueError, OSError):
        return False


def scan_aged_files(root: str, min_age_days: int = 7, limit: int = MAX_DISPLAY) -> ScanResult:
    root = _validate_temp_root(root)
    if min_age_days < 1 or min_age_days > 365 or limit < 1 or limit > 3000:
        raise ValueError('Specify an age between 1 and 365 days and a valid result limit.')
    cutoff = time.time_ns() - min_age_days * 86400 * 1_000_000_000
    count = size = skipped = 0
    # Bounded priority queue: keeps the oldest limit files, while counting all eligible files.
    oldest: list[tuple[int, int, TempFile]] = []
    counter = 0
    for folder, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [d for d in directories if not _is_reparse(os.path.join(folder, d))]
        if not _safe_child(root, folder) and folder != root:
            directories[:] = []
            continue
        for filename in filenames:
            path = os.path.join(folder, filename)
            if _is_reparse(path):
                skipped += 1
                continue
            try:
                st = os.stat(path, follow_symlinks=False)
                if not stat.S_ISREG(st.st_mode) or st.st_mtime_ns > cutoff:
                    continue
                candidate = TempFile(path, st.st_size, st.st_mtime_ns, st.st_ino)
                count += 1
                size += st.st_size
                counter += 1
                item = (-st.st_mtime_ns, counter, candidate)
                if len(oldest) < limit:
                    heapq.heappush(oldest, item)
                elif item[0] > oldest[0][0]:
                    heapq.heapreplace(oldest, item)
            except OSError:
                skipped += 1
    files = tuple(x[2] for x in sorted(oldest, key=lambda x: (-x[0], x[1])))
    return ScanResult(files, count, size, skipped)


def remove_selected(root: str, files: list[TempFile], min_age_days: int = 7) -> tuple[int, int, int]:
    """Return (deleted_count, deleted_bytes, skipped_count); never delete folders."""
    root = _validate_temp_root(root)
    if min_age_days < 1 or min_age_days > 365:
        raise ValueError('Invalid minimum age for deleting temporary files.')
    cutoff = time.time_ns() - min_age_days * 86400 * 1_000_000_000
    deleted = deleted_bytes = skipped = 0
    for item in files:
        if not _safe_child(root, item.path):
            skipped += 1
            continue
        try:
            before = os.stat(item.path, follow_symlinks=False)
            if (not stat.S_ISREG(before.st_mode) or before.st_mtime_ns > cutoff or
                before.st_mtime_ns != item.mtime_ns or before.st_size != item.size or
                before.st_ino != item.inode):
                skipped += 1
                continue
            os.unlink(item.path)
            deleted += 1
            deleted_bytes += item.size
        except OSError:
            skipped += 1
    return deleted, deleted_bytes, skipped


def _size_label(size: int) -> str:
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        if size < 1024 or unit == 'TiB':
            return f'{size:,.0f} {unit}' if unit == 'B' else f'{size:,.1f} {unit}'
        size /= 1024
    return ''


class TempCleanerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('User TEMP — scan & review')
        self.geometry('960x620')
        self.minsize(760, 480)
        self.configure(bg='#121e2d')
        self.transient(parent)
        self.events: queue.Queue = queue.Queue()
        self.scan_data: ScanResult | None = None
        self.file_rows: dict[str, TempFile] = {}
        self.age_var = tk.StringVar(value='7')
        self.summary_var = tk.StringVar(value='Reviewing the current user TEMP folder only. No files are selected automatically.')
        self._busy = False
        self._last_cleanup_notice = ''
        self._build()
        self.after(200, self.scan)

    def _build(self):
        bg, fg, muted = '#121e2d', '#ecf2fc', '#a5b6cc'
        title = tk.Frame(self, bg=bg)
        title.pack(fill='x', padx=23, pady=(22, 6))
        tk.Label(title, text='Temporary files — careful cleanup', bg=bg, fg=fg,
                 font=('Segoe UI', 17, 'bold')).pack(anchor='w')
        tk.Label(title, text='Only the signed-in user’s TEMP directory. Never Downloads, Recycle Bin or Windows system caches.',
                 bg=bg, fg=muted, font=('Segoe UI', 10)).pack(anchor='w', pady=(7, 0))
        top = tk.Frame(self, bg=bg)
        top.pack(fill='x', padx=23, pady=15)
        tk.Label(top, text='Show files last modified at least', bg=bg, fg=fg).pack(side='left')
        self.age_box = ttk.Combobox(top, textvariable=self.age_var, state='readonly', width=5,
                                     values=['7', '14', '30', '60', '90'])
        self.age_box.pack(side='left', padx=8)
        tk.Label(top, text='days ago', bg=bg, fg=fg).pack(side='left')
        self.scan_btn = tk.Button(top, text='Scan / refresh', command=self.scan,
                                  bg='#1b2a40', fg=fg, padx=16, pady=7, relief='flat')
        self.scan_btn.pack(side='right')
        tk.Label(self, textvariable=self.summary_var, bg=bg, fg='#6ea2ff',
                 wraplength=880, justify='left', anchor='w').pack(fill='x', padx=23, pady=(0, 12))
        table_frame = tk.Frame(self, bg=bg)
        table_frame.pack(fill='both', expand=True, padx=23)
        columns = ('date', 'size', 'path')
        style = ttk.Style(self)
        style.configure('Temp.Dark.Treeview', background='#192638', foreground='#ecf2fc',
                        fieldbackground='#192638', rowheight=26, borderwidth=0)
        style.map('Temp.Dark.Treeview', background=[('selected', '#2563d9')],
                  foreground=[('selected', '#ffffff')])
        style.configure('Temp.Dark.Treeview.Heading', background='#1b2a40',
                        foreground='#ecf2fc', relief='flat')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings',
                                  selectmode='extended', style='Temp.Dark.Treeview')
        for col, name, width in (('date', 'Last modified', 145), ('size', 'Size', 95), ('path', 'File path', 640)):
            self.table.heading(col, text=name)
            self.table.column(col, width=width, minwidth=80, anchor='w')
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        tk.Label(self, text='Select individual files using Ctrl/Shift. Deleting permanently removes only the selected, unchanged files.',
                 bg=bg, fg='#ffcd7b', anchor='w').pack(fill='x', padx=23, pady=(14, 0))
        bottom = tk.Frame(self, bg=bg)
        bottom.pack(fill='x', padx=23, pady=(14, 20))
        self.delete_btn = tk.Button(bottom, text='Delete selected files…', command=self.delete_selected,
                                    bg='#913f48', fg='white', relief='flat', padx=20, pady=10, state='disabled')
        self.delete_btn.pack(side='right')
        self.table.bind('<<TreeviewSelect>>', lambda _event: self._update_delete_state())
        tk.Button(bottom, text='Close', command=self.destroy, bg='#1b2a40', fg=fg,
                  relief='flat', padx=20, pady=10).pack(side='right', padx=(0, 10))

    def _update_delete_state(self):
        self.delete_btn.configure(state='normal' if not self._busy and self.table.selection() else 'disabled')

    def _work(self, action: str, func):
        self._busy = True
        self.scan_btn.configure(state='disabled')
        self.age_box.configure(state='disabled')
        self._update_delete_state()
        self.summary_var.set('Scanning safely…' if action == 'scan' else 'Deleting selected old TEMP files…')
        def worker():
            try:
                self.events.put((action, func(), None))
            except Exception as exc:
                self.events.put((action, None, str(exc)))
        threading.Thread(target=worker, daemon=True).start()
        self.after(150, self._poll)

    def scan(self):
        if self._busy:
            return
        days = int(self.age_var.get())
        self._work('scan', lambda: scan_aged_files(user_temp_root(), days))

    def _poll(self):
        if not self.winfo_exists():
            return
        try:
            action, payload, error = self.events.get_nowait()
        except queue.Empty:
            self.after(150, self._poll)
            return
        self._busy = False
        self.scan_btn.configure(state='normal')
        self.age_box.configure(state='readonly')
        if error:
            self.summary_var.set('Operation failed: ' + error)
            messagebox.showerror('TEMP operation failed', error, parent=self)
        elif action == 'scan':
            self.scan_data = payload
            self.file_rows.clear()
            self.table.delete(*self.table.get_children())
            for i, item in enumerate(payload.files):
                row_id = str(i)
                self.file_rows[row_id] = item
                self.table.insert('', 'end', iid=row_id, values=(
                    datetime.fromtimestamp(item.mtime_ns / 1e9).strftime('%Y-%m-%d %H:%M'),
                    _size_label(item.size), item.path))
            self.summary_var.set(
                (self._last_cleanup_notice + '  |  ' if self._last_cleanup_notice else '') +
                f'Found {payload.eligible_files:,} files at least {self.age_var.get()} days old '
                f'(~{_size_label(payload.eligible_bytes)}). '
                f'Displaying the oldest {len(payload.files)}. No files are selected.')
        else:
            count, bytes_removed, skipped = payload
            self._last_cleanup_notice = (f'Deleted {count} selected files ({_size_label(bytes_removed)}); '
                                         f'skipped {skipped} changed, locked, or unsafe files.')
            self.summary_var.set(self._last_cleanup_notice + ' Refreshing…')
            self.scan()
        self._update_delete_state()

    def delete_selected(self):
        if self._busy:
            return
        chosen = [self.file_rows[i] for i in self.table.selection() if i in self.file_rows]
        if not chosen:
            return
        if not messagebox.askyesno('Permanently delete selected TEMP files?',
                                   f'Delete ONLY these {len(chosen)} selected files (total {_size_label(sum(f.size for f in chosen))})?\n\n'
                                   'They were last modified at least the chosen number of days ago. '
                                   'Files that have changed or are locked will be skipped.\n\n'
                                   'This deletion cannot be undone.', parent=self, icon='warning'):
            return
        days = int(self.age_var.get())
        self._work('delete', lambda: remove_selected(user_temp_root(), chosen, days))


def open_temp_cleaner(parent):
    if os.name != 'nt':
        messagebox.showinfo('Windows required', 'The TEMP cleaner is available only on Windows 10/11.', parent=parent)
        return
    TempCleanerWindow(parent)
