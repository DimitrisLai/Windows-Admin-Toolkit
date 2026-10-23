"""Windows Admin Toolkit — a curated maintenance command reference and launcher.

Run with: python app.py
Windows 10/11, Python 3.10+, standard library Tkinter only.
"""
from __future__ import annotations
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from pathlib import Path

from command_catalog import COMMANDS, BY_ID, Command, categories, display_command, validate_file_target, validate_report_target, validate_network_host, validate_network_port
from windows_launcher import available_drives, is_admin, launch
from temp_cleaner import open_temp_cleaner

# Dark Fluent-inspired palette; drawn with platform-neutral Tkinter widgets.
BG = '#0d1623'
TOP = '#141f2e'
PANEL = '#121e2d'
CARD = '#192638'
INPUT = '#1b2a40'
BORDER = '#2a3a53'
TEXT = '#ecf2fc'
MUTED = '#a5b6cc'
ACCENT = '#2563d9'
HOVER = '#213451'
BLUE = '#6ea2ff'
GREEN = '#4de0ac'
ORANGE = '#ffcd7b'
RED = '#ff9193'
FONT = 'Segoe UI' if sys.platform == 'win32' else 'DejaVu Sans'
MONO = 'Cascadia Code' if sys.platform == 'win32' else 'DejaVu Sans Mono'
APP_VERSION = '2.4.5'


def label(parent, text, *, size=10, color=TEXT, weight='normal', **kw):
    return tk.Label(parent, text=text, font=(FONT, size, weight),
                    bg=parent.cget('bg'), fg=color, **kw)


def button(parent, text, command, *, primary=False, width=None, disabled=False):
    b = tk.Button(parent, text=text, command=command, font=(FONT, 10, 'bold'),
                  bg=ACCENT if primary else INPUT, fg=TEXT,
                  activebackground='#3477ee' if primary else HOVER,
                  activeforeground=TEXT, relief='flat', bd=0, padx=17, pady=11,
                  cursor='hand2', highlightthickness=0,
                  disabledforeground='#6a788b')
    if width:
        b.config(width=width)
    if disabled:
        b.config(state='disabled')
    return b


class SlimScrollbar(tk.Canvas):
    """Small dark scrollbar that remains dark across Windows/Tk themes."""
    def __init__(self, master, *, orient='vertical', command=None):
        self.vertical = orient == 'vertical'
        super().__init__(master, bg=PANEL, highlightthickness=0, bd=0,
                         width=11 if self.vertical else 1,
                         height=11 if not self.vertical else 1,
                         cursor='hand2')
        self.command = command
        self.first, self.last = 0.0, 1.0
        self.bind('<Configure>', lambda _: self._paint())
        self.bind('<Button-1>', self._click)
        self.bind('<B1-Motion>', self._click)

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self._paint()

    def _paint(self):
        self.delete('all')
        length = self.winfo_height() if self.vertical else self.winfo_width()
        if length < 2 or self.last - self.first >= .999:
            return
        thickness = self.winfo_width() if self.vertical else self.winfo_height()
        start = max(0, self.first * length)
        end = min(length, max(start + 22, self.last * length))
        if self.vertical:
            self.create_rectangle(2, start, thickness - 2, end, fill='#4f6582', outline='')
        else:
            self.create_rectangle(start, 2, end, thickness - 2, fill='#4f6582', outline='')

    def _click(self, event):
        if self.command is None:
            return
        length = self.winfo_height() if self.vertical else self.winfo_width()
        pointer = event.y if self.vertical else event.x
        thumb_fraction = self.last - self.first
        fraction = max(0.0, min(1.0 - thumb_fraction,
                                pointer / max(1, length) - thumb_fraction / 2))
        self.command('moveto', str(fraction))


class ScrollableDetails(tk.Frame):
    """Scrollable detail content, footer remains fixed."""
    def __init__(self, master):
        super().__init__(master, bg=PANEL)
        self.canvas = tk.Canvas(self, bg=PANEL, highlightthickness=0, bd=0)
        self.scrollbar = SlimScrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.body = tk.Frame(self.canvas, bg=PANEL)
        self.body_id = self.canvas.create_window((0, 0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', self._content_resize)
        self.canvas.bind('<Configure>', self._canvas_resize)

    def _content_resize(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _canvas_resize(self, event):
        self.canvas.itemconfigure(self.body_id, width=event.width)

    def reset(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


class AdminToolkit(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'Windows Admin Toolkit v{APP_VERSION}')
        self.configure(bg=BG)
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        width = max(1080, min(1460, screen_w - 70))
        height = max(620, min(865, screen_h - 70))
        self.geometry(f'{width}x{height}+{max(0, (screen_w-width)//2)}+{max(0, (screen_h-height)//2)}')
        self.minsize(1080, 620)
        self._set_app_icon()

        self.drive_var = tk.StringVar(value='C:')
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value='All categories')
        self.status_var = tk.StringVar(value='Ready')
        # Expert Mode is intentionally OFF at every app start; it never removes safety checks.
        self.expert_var = tk.BooleanVar(value=False)
        self.host_var = tk.StringVar(value='www.microsoft.com')
        self.port_var = tk.StringVar(value='443')
        self.selected_file: str | None = None
        self.selected_report: str | None = None
        self.current: Command = BY_ID['disk.recover']
        self.visible_commands: list[Command] = []
        self.drives: list[str] = []
        self._style_ttk()
        self._create_layout()
        self._refresh_drives()
        self._populate_commands(select_id=self.current.id)
        self.search_var.trace_add('write', lambda *_: self._populate_commands())
        self.host_var.trace_add('write', lambda *_: self._render_detail())
        self.port_var.trace_add('write', lambda *_: self._render_detail())
        self.bind('<Control-f>', self._focus_search)
        self.bind('<Control-F>', self._focus_search)
        self.bind_all('<MouseWheel>', self._wheel, add='+')
        self.bind_all('<Button-4>', self._wheel, add='+')
        self.bind_all('<Button-5>', self._wheel, add='+')

    def _on_expert_toggle(self):
        enabled = self.expert_var.get()
        self.expert_toggle.config(
            text='EXPERT: ON' if enabled else 'EXPERT: OFF',
            bg=ACCENT if enabled else INPUT,
            fg=TEXT if enabled else MUTED,
            selectcolor=ACCENT if enabled else INPUT)
        self.status_var.set(
            'Expert Mode ON — launch notices hidden' if enabled
            else 'Expert Mode OFF — launch notices visible')

    def _set_app_icon(self):
        try:
            icon = Path(__file__).resolve().parent / 'assets' / 'toolkit.ico'
            if icon.is_file() and os.name == 'nt':
                self.iconbitmap(str(icon))
        except Exception:
            pass

    def _style_ttk(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('Dark.TCombobox', foreground=TEXT, fieldbackground=INPUT,
                    background=INPUT, selectbackground=ACCENT, selectforeground=TEXT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    arrowcolor=TEXT, padding=(8, 8))
        s.map('Dark.TCombobox', fieldbackground=[('readonly', INPUT), ('disabled', TOP)],
              foreground=[('disabled', '#76849a'), ('readonly', TEXT)],
              background=[('active', INPUT), ('readonly', INPUT)])
        s.configure('Dark.Vertical.TScrollbar', background=INPUT,
                    troughcolor=PANEL, bordercolor=PANEL, arrowcolor=MUTED)
        s.configure('Dark.Horizontal.TScrollbar', background=INPUT,
                    troughcolor=PANEL, bordercolor=PANEL, arrowcolor=MUTED)
        self.option_add('*TCombobox*Listbox.background', INPUT)
        self.option_add('*TCombobox*Listbox.foreground', TEXT)
        self.option_add('*TCombobox*Listbox.selectBackground', ACCENT)

    def _create_layout(self):
        header = tk.Frame(self, bg=TOP, height=69, highlightthickness=1,
                          highlightbackground=BORDER)
        header.pack(side='top', fill='x')
        header.pack_propagate(False)
        logo = tk.Label(header, text='  ❯_', font=(MONO, 17, 'bold'), fg='white',
                        bg=ACCENT, padx=5, pady=2)
        logo.pack(side='left', padx=(22, 15), pady=14)
        label(header, 'Windows Admin Toolkit', size=15, weight='bold').pack(side='left')
        label(header, '  •  Safe command reference for Windows 10 / 11',
              size=9, color=MUTED).pack(side='left', padx=(14, 0))
        self.admin_text = label(header, 'ADMIN MODE' if is_admin() else 'STANDARD MODE',
                                size=9, color=GREEN if is_admin() else MUTED,
                                weight='bold')
        self.admin_text.pack(side='right', padx=(10, 23))
        # A visible, keyboard-accessible switch for experienced users. This
        # controls only the redundant post-launch information dialog.
        self.expert_toggle = tk.Checkbutton(
            header, text='EXPERT: OFF', variable=self.expert_var,
            indicatoron=False, command=self._on_expert_toggle,
            font=(FONT, 9, 'bold'), bg=INPUT, fg=MUTED,
            selectcolor=INPUT, activebackground=HOVER, activeforeground=TEXT,
            relief='flat', bd=0, padx=12, pady=8, cursor='hand2',
            highlightthickness=1, highlightbackground=BORDER,
            takefocus=True)
        self.expert_toggle.pack(side='right', padx=(0, 6))


        layout = tk.Frame(self, bg=BG)
        layout.pack(fill='both', expand=True, padx=15, pady=(15, 5))
        self.left = tk.Frame(layout, bg=PANEL, width=355, highlightbackground=BORDER, highlightthickness=1)
        self.left.pack(side='left', fill='y', padx=(0, 12))
        self.left.pack_propagate(False)
        self.mid = tk.Frame(layout, bg=PANEL, width=187, highlightbackground=BORDER, highlightthickness=1)
        self.mid.pack(side='left', fill='y', padx=(0, 12))
        self.mid.pack_propagate(False)
        self.right = tk.Frame(layout, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.right.pack(side='left', fill='both', expand=True)
        self._create_left()
        self._create_middle()
        self._create_right()

        foot = tk.Frame(self, bg=BG, height=32)
        foot.pack(side='bottom', fill='x', padx=22)
        label(foot, '69 curated tools  •  No arbitrary command entry',
              size=9, color=MUTED).pack(side='left')
        self.status = label(foot, '', size=9, color=MUTED)
        self.status.pack(side='right')
        self.status_var.trace_add('write', lambda *_: self.status.config(text=self.status_var.get()))

    def _create_left(self):
        wrapper = tk.Frame(self.left, bg=PANEL)
        wrapper.pack(fill='x', padx=16, pady=(19, 0))
        label(wrapper, 'Commands', size=17, weight='bold').pack(anchor='w')
        label(wrapper, 'Browse, search and select a command', size=9, color=MUTED).pack(anchor='w', pady=(3, 12))
        search_frame = tk.Frame(wrapper, bg=INPUT, highlightbackground=BORDER, highlightthickness=1)
        search_frame.pack(fill='x')
        tk.Label(search_frame, text='⌕', font=(FONT, 17), fg=MUTED, bg=INPUT).pack(side='left', padx=(10, 4))
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     bg=INPUT, fg=TEXT, insertbackground=TEXT,
                                     font=(FONT, 10), relief='flat', highlightthickness=0,
                                     bd=0)
        self.search_entry.pack(side='left', fill='both', expand=True, padx=(0, 9), pady=12)
        self.search_entry.insert(0, '')
        self.category_box = ttk.Combobox(wrapper, textvariable=self.category_var,
                                          values=['All categories', *categories()],
                                          state='readonly', style='Dark.TCombobox', font=(FONT, 9))
        self.category_box.pack(fill='x', pady=(10, 10))
        self.category_box.bind('<<ComboboxSelected>>', lambda _: self._populate_commands())
        self.count_label = label(wrapper, '', size=9, color=MUTED)
        self.count_label.pack(anchor='w', pady=(0, 8))

        list_frame = tk.Frame(self.left, bg=PANEL)
        list_frame.pack(fill='both', expand=True, padx=(9, 3), pady=(0, 12))
        self.command_list = tk.Listbox(list_frame, bg=PANEL, fg=TEXT,
                                       selectbackground=ACCENT, selectforeground=TEXT,
                                       activestyle='none', borderwidth=0, relief='flat',
                                       highlightthickness=0, font=(FONT, 10),
                                       exportselection=False, selectmode='browse',
                                       height=20, takefocus=True)
        vs = SlimScrollbar(list_frame, orient='vertical', command=self.command_list.yview)
        hs = SlimScrollbar(list_frame, orient='horizontal', command=self.command_list.xview)
        self.command_list.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.command_list.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        self.command_list.bind('<<ListboxSelect>>', self._choose_command)
        self.command_list.bind('<Double-Button-1>', lambda _: self._copy_command())

    def _create_middle(self):
        # The middle panel has more controls than fit vertically on smaller
        # displays. Keep ALL of them reachable, instead of clipping the report
        # picker and safety information below the bottom edge of the window.
        self.middle_canvas = tk.Canvas(self.mid, bg=PANEL, highlightthickness=0, bd=0)
        middle_scrollbar = SlimScrollbar(self.mid, orient='vertical',
                                         command=self.middle_canvas.yview)
        self.middle_canvas.configure(yscrollcommand=middle_scrollbar.set)
        middle_scrollbar.pack(side='right', fill='y')
        self.middle_canvas.pack(side='left', fill='both', expand=True)
        block = tk.Frame(self.middle_canvas, bg=PANEL)
        self.middle_body_id = self.middle_canvas.create_window((0, 0), window=block,
                                                                anchor='nw')
        block.bind('<Configure>', lambda e: self.middle_canvas.configure(
            scrollregion=self.middle_canvas.bbox('all')))
        self.middle_canvas.bind('<Configure>', lambda e: self.middle_canvas.itemconfigure(
            self.middle_body_id, width=e.width))
        inner = tk.Frame(block, bg=PANEL)
        inner.pack(fill='x', padx=(12, 8), pady=(20, 15))
        block = inner
        label(block, 'Drive', size=12, weight='bold').pack(anchor='w')
        self.drive_box = ttk.Combobox(block, textvariable=self.drive_var,
                                      values=['C:'], state='readonly',
                                      style='Dark.TCombobox', font=(FONT, 11))
        self.drive_box.pack(fill='x', pady=(9, 0))
        self.drive_box.bind('<<ComboboxSelected>>', lambda _: self._render_detail())
        self.drive_hint = label(block, 'Select a drive for commands that need one.',
                                 size=9, color=MUTED, wraplength=148, justify='left')
        self.drive_hint.pack(anchor='w', pady=(15, 13))
        self.refresh_button = button(block, '↻  Refresh drives', self._refresh_drives)
        self.refresh_button.pack(anchor='w')
        self.temp_button = button(block, '✧  Temp file cleaner', self._open_cleaner)
        self.temp_button.pack(fill='x', pady=(15, 0))

        tk.Frame(block, bg=BORDER, height=1).pack(fill='x', pady=(17, 12))
        self.file_caption = label(block, 'System file', size=11, weight='bold')
        self.file_caption.pack(anchor='w')
        self.file_button = button(block, 'Choose file…', self._choose_file)
        self.file_button.pack(fill='x', pady=(9, 0))
        self.file_hint = label(block, 'Only needed for SFC /scanfile.',
                                color=MUTED, size=9, wraplength=146, justify='left')
        self.file_hint.pack(anchor='w', pady=(10, 0))

        tk.Frame(block, bg=BORDER, height=1).pack(fill='x', pady=(17, 12))
        label(block, 'HTML report', size=11, weight='bold').pack(anchor='w')
        self.report_button = button(block, 'Save report as…', self._choose_report)
        self.report_button.pack(fill='x', pady=(9, 0))
        self.report_hint = label(block, 'Only used for battery and energy reports.',
                                 color=MUTED, size=9, wraplength=146, justify='left')
        self.report_hint.pack(anchor='w', pady=(9, 0))
        tk.Frame(block, bg=BORDER, height=1).pack(fill='x', pady=(17, 12))
        label(block, 'Network test target', size=11, weight='bold').pack(anchor='w')
        label(block, 'Hostname or IP', size=9, color=MUTED).pack(anchor='w', pady=(10, 4))
        self.host_entry = tk.Entry(block, textvariable=self.host_var, bg=INPUT, fg=TEXT,
                                   insertbackground=TEXT, relief='flat', font=(FONT, 9),
                                   highlightthickness=1, highlightbackground=BORDER)
        self.host_entry.pack(fill='x', ipady=7)
        label(block, 'TCP port (1–65535)', size=9, color=MUTED).pack(anchor='w', pady=(9, 4))
        self.port_entry = tk.Entry(block, textvariable=self.port_var, bg=INPUT, fg=TEXT,
                                   insertbackground=TEXT, relief='flat', font=(FONT, 9),
                                   highlightthickness=1, highlightbackground=BORDER)
        self.port_entry.pack(fill='x', ipady=7)
        self.network_hint = label(block, 'Only used for Test-NetConnection.', size=9,
                                  color=MUTED, wraplength=145, justify='left')
        self.network_hint.pack(anchor='w', pady=(8, 0))
        tk.Frame(block, bg=BORDER, height=1).pack(fill='x', pady=(17, 12))
        label(block, 'Safety', size=11, weight='bold').pack(anchor='w')
        label(block, 'System-changing commands ask for confirmation. Windows UAC handles elevation.',
              size=9, color=MUTED, justify='left', wraplength=145).pack(anchor='w', pady=(8, 12))

    def _create_right(self):
        self.heading = tk.Frame(self.right, bg=PANEL)
        self.heading.pack(side='top', fill='x', padx=25, pady=(22, 13))
        label(self.heading, 'Command details', size=18, weight='bold').pack(side='left')
        self.category_label = label(self.heading, '', size=9, color=MUTED)
        self.category_label.pack(side='right', pady=(6, 0))
        self.detail_scroll = ScrollableDetails(self.right)
        self.detail_scroll.pack(fill='both', expand=True, padx=(20, 7))
        controls = tk.Frame(self.right, bg=PANEL)
        controls.pack(side='bottom', fill='x', padx=24, pady=(11, 19))
        tk.Frame(controls, bg=BORDER, height=1).pack(fill='x', pady=(0, 12))
        self.run_button = button(controls, '🛡  Run as Admin', self._run, primary=True)
        self.run_button.pack(side='right', padx=(9, 0))
        self.copy_button = button(controls, '▣  Copy Command', self._copy_command)
        self.copy_button.pack(side='right')

    def _populate_commands(self, select_id: str | None = None):
        query = self.search_var.get().strip().lower()
        category = self.category_var.get()
        previous = select_id or self.current.id
        self.visible_commands = [c for c in COMMANDS
                                 if (category == 'All categories' or c.category == category)
                                 and (not query or query in (c.label + ' ' + c.category + ' ' +
                                                             c.description + ' ' + c.best_for).lower())]
        self.command_list.delete(0, tk.END)
        for c in self.visible_commands:
            self.command_list.insert(tk.END, '  ' + c.label)
        self.count_label.config(text=f'{len(self.visible_commands)} of {len(COMMANDS)} commands')
        if self.visible_commands:
            index = next((i for i, c in enumerate(self.visible_commands) if c.id == previous), 0)
            self.command_list.selection_set(index)
            self.command_list.activate(index)
            self.command_list.see(index)
            self._choose_command()
        else:
            self.detail_scroll.reset()
            label(self.detail_scroll.body, 'No commands match your search.',
                  size=12, color=MUTED).pack(anchor='w', padx=20, pady=30)
            self.run_button.config(state='disabled')
            self.copy_button.config(state='disabled')
            self.drive_box.configure(state='disabled')
            self.file_button.configure(state='disabled')
            self.report_button.configure(state='disabled')

    def _choose_command(self, _event=None):
        sel = self.command_list.curselection()
        if not sel:
            return
        selected = self.visible_commands[sel[0]]
        if selected.id != self.current.id:
            self.selected_file = None
            self.selected_report = None
        self.current = selected
        self._render_detail()

    def _refresh_drives(self):
        old = self.drive_var.get()
        self.drives = available_drives()
        self.drive_box['values'] = self.drives
        # C: is the preferred default even when not alphabetically first.
        self.drive_var.set(old if old in self.drives else 'C:' if 'C:' in self.drives else
                           self.drives[0] if self.drives else '')
        if hasattr(self, 'detail_scroll'):
            if self.visible_commands:
                self._render_detail()
            self.status_var.set(f'Drives refreshed: {", ".join(self.drives)}')

    def _wheel(self, event):
        # Delegate scrolling to the pane beneath the pointer, even when over
        # child labels (Tk's ordinary Canvas wheel binding misses these).
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        parent = widget
        while parent is not None:
            if parent == self.detail_scroll:
                step = -1 if (getattr(event, 'num', 0) == 4 or event.delta > 0) else 1
                self.detail_scroll.canvas.yview_scroll(step * 3, 'units')
                return 'break'
            if parent == self.mid:
                step = -1 if (getattr(event, 'num', 0) == 4 or event.delta > 0) else 1
                self.middle_canvas.yview_scroll(step * 3, 'units')
                return 'break'
            if parent == self.left:
                if widget != self.command_list:
                    step = -1 if (getattr(event, 'num', 0) == 4 or event.delta > 0) else 1
                    self.command_list.yview_scroll(step * 3, 'units')
                    return 'break'
                return
            parent = getattr(parent, 'master', None)

    def _choose_file(self):
        filename = filedialog.askopenfilename(title='Select a protected Windows system file',
                                               filetypes=[('System files', '*.dll *.sys *.exe *.ocx'),
                                                          ('All files', '*.*')])
        if filename:
            try:
                # Rendered by cmd.exe; reject command metacharacters before
                # the selection reaches the preview or the clipboard.
                self.selected_file = validate_file_target(filename)
            except ValueError as exc:
                self.selected_file = None
                messagebox.showerror('Unsupported file path', str(exc), parent=self)
            self._render_detail()

    def _choose_report(self):
        c = self.current
        if not c.needs_report:
            return
        stem = {'power.battery':'battery-report', 'power.energy':'energy-report',
                'power.sleepstudy':'sleepstudy-report'}.get(c.id,'report')
        filename = filedialog.asksaveasfilename(
            title='Choose HTML report destination', defaultextension='.html',
            initialfile=stem + '.html', filetypes=[('HTML reports', '*.html')])
        if filename:
            try:
                self.selected_report = validate_report_target(filename)
                if not Path(filename).parent.is_dir():
                    raise ValueError('Select an existing destination folder.')
            except ValueError as exc:
                self.selected_report = None
                messagebox.showerror('Invalid report destination', str(exc))
            self._render_detail()

    def _open_cleaner(self):
        open_temp_cleaner(self)

    def _focus_search(self, _event=None):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
        return 'break'

    def _info_section(self, parent, symbol, heading, body, *, body_color=TEXT):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill='x', padx=(4, 17), pady=(4, 16))
        icon = tk.Label(row, text=symbol, font=(FONT, 16, 'bold'), bg=PANEL, fg=BLUE,
                        width=3, anchor='nw')
        icon.pack(side='left', anchor='n')
        text_frame = tk.Frame(row, bg=PANEL)
        text_frame.pack(side='left', fill='x', expand=True)
        label(text_frame, heading, size=11, weight='bold').pack(anchor='w', pady=(0, 7))
        body_label = label(text_frame, body, size=10, color=body_color, justify='left',
                           anchor='w', wraplength=590)
        body_label.pack(anchor='w', fill='x')
        # Dynamically wrap with the actual panel size.
        text_frame.bind('<Configure>', lambda e, widget=body_label: widget.configure(
            wraplength=max(185, e.width - 15)), add='+')

    def _render_detail(self):
        if not hasattr(self, 'detail_scroll'):
            return
        c = self.current
        self.category_label.config(text=c.category)
        drive_ready = not c.uses_drive or (bool(self.drives) and self.drive_var.get() in self.drives)
        self.drive_box.configure(state='readonly' if c.uses_drive and drive_ready else 'disabled')
        self.drive_hint.config(text=('Required for this command. Only detected local drives are listed.'
                                     if drive_ready else 'No available local drives detected. Refresh drives.')
                                    if c.uses_drive else 'Locked: this command does not use a drive letter.')
        self.file_button.configure(state='normal' if c.needs_file else 'disabled')
        self.file_hint.config(text=(Path(self.selected_file).name if self.selected_file else
                                    'Choose a local protected Windows file to scan.')
                                   if c.needs_file else 'Only used by the SFC single-file check.')
        self.report_button.configure(state='normal' if c.needs_report else 'disabled')
        self.report_hint.config(text=(Path(self.selected_report).name if self.selected_report else
                                      'Choose a destination for the HTML report.')
                                    if c.needs_report else 'Only used by battery, energy and sleep reports.')
        self.host_entry.configure(state='normal' if c.needs_network else 'disabled')
        self.port_entry.configure(state='normal' if c.needs_network else 'disabled')
        network_valid = True
        if c.needs_network:
            try:
                validate_network_host(self.host_var.get())
                validate_network_port(self.port_var.get())
                self.network_hint.configure(text='Target validated; makes a TCP connection attempt.', fg=GREEN)
            except ValueError as exc:
                network_valid = False
                self.network_hint.configure(text=str(exc), fg=ORANGE)
        else:
            self.network_hint.configure(text='Only used for Test-NetConnection.', fg=MUTED)
        self.detail_scroll.reset()
        body = self.detail_scroll.body
        preview = (c.label if (c.uses_drive and not drive_ready) or not network_valid else
                   display_command(c, self.drive_var.get(), self.selected_file, self.selected_report,
                                   self.host_var.get(), self.port_var.get()))

        preview_box = tk.Frame(body, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        preview_box.pack(fill='x', padx=(6, 16), pady=(5, 21))
        label(preview_box, 'COMMAND', size=9, color=MUTED, weight='bold').pack(anchor='w', padx=19, pady=(15, 7))
        preview_row = tk.Frame(preview_box, bg=CARD)
        preview_row.pack(fill='x', padx=18, pady=(0, 17))
        preview_text = tk.Text(preview_row, font=(MONO, 12, 'bold'), bg=CARD,
                               fg='#dce8ff', wrap='word', borderwidth=0,
                               highlightthickness=0, width=20, height=2,
                               padx=0, pady=0, cursor='arrow')
        preview_text.insert('1.0', preview)
        preview_text.config(state='disabled')
        preview_text.pack(side='left', fill='x', expand=True)
        button(preview_row, '▣', self._copy_command).pack(side='right', padx=(8, 0))

        self._info_section(body, '▤', 'What it does', c.description)
        self._info_section(body, '◎', 'Best for', c.best_for)
        self._info_section(body, '▱', 'Drive selector',
                           f"{'Required — ' + self.drive_var.get() if c.uses_drive else 'Not applicable — locked.'}")
        self._info_section(body, '♢', 'Administrator rights',
                           'Required — Windows User Account Control (UAC) will request elevation.'
                           if c.admin else 'Not required for opening or running this command.')
        self._info_section(body, '↻', 'Restart', c.restart)
        color = GREEN if c.risk == 'read' else ORANGE if c.risk == 'change' else RED
        risk_name = {'read': 'Inspection / low risk', 'change': 'Changes settings, creates files or performs cleanup',
                     'heavy': 'Potentially disruptive or intensive'}[c.risk]
        self._info_section(body, '!', 'Safety level', risk_name, body_color=color)
        self._info_section(body, 'ⓘ', 'Important notes', c.notes, body_color=MUTED)

        tip = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tip.pack(fill='x', padx=(7, 16), pady=(0, 16))
        label(tip, 'ADDITIONAL INFORMATION', size=10, weight='bold', color=BLUE).pack(anchor='w', padx=19, pady=(13, 5))
        for note in self._tips(c):
            line = tk.Frame(tip, bg=CARD)
            line.pack(fill='x', padx=20, pady=5)
            tk.Label(line, text='•', font=(FONT, 12, 'bold'), bg=CARD, fg=BLUE).pack(side='left', padx=(0, 8))
            note_label = tk.Label(line, text=note, font=(FONT, 9), fg=TEXT,
                                   bg=CARD, anchor='w', justify='left', wraplength=565)
            note_label.pack(side='left', fill='x', expand=True)
            line.bind('<Configure>', lambda e, w=note_label: w.configure(wraplength=max(190, e.width-38)), add='+')
        tk.Frame(tip, bg=CARD, height=8).pack()
        if c.doc_url:
            link = tk.Label(body, text='↗  View official Microsoft documentation',
                            fg=BLUE, bg=PANEL, cursor='hand2', font=(FONT, 10, 'underline'))
            link.pack(anchor='w', padx=14, pady=(0, 14))
            link.bind('<Button-1>', lambda _e, url=c.doc_url: webbrowser.open(url))

        valid_file = (not c.needs_file or bool(self.selected_file)) and (not c.needs_report or bool(self.selected_report)) and drive_ready and network_valid
        self.copy_button.config(state='normal' if valid_file else 'disabled')
        self.run_button.config(state='normal' if valid_file else 'disabled',
                               text='🛡  Run as Admin' if c.admin else '▶  Run Command')

    def _tips(self, c: Command) -> list[str]:
        if c.category == 'Windows files':
            return ['Run DISM /RestoreHealth first if component-store corruption is suspected.',
                    'SFC repairs protected Windows files, not personal documents.']
        if c.category == 'Windows image (DISM)':
            return ['DISM /Online targets the currently running Windows installation.',
                    'Run SFC /scannow afterward if you need to repair protected system files.']
        if c.category == 'Disk & storage':
            return ['CHKDSK /f fixes logical errors; /r also scans for bad sectors.',
                    'Physical disk health status is not a replacement for verified backups.']
        if c.category == 'RAM & performance':
            return ['Windows manages cached RAM automatically; do not use fake RAM boosters.',
                    'For RAM hardware errors use Windows Memory Diagnostic in Hardware & diagnostics.']
        if c.category == 'Temporary files':
            return ['Preview old TEMP files with the Temp file cleaner button; nothing is preselected.',
                    'Use Storage Sense or Disk Cleanup for system-wide cleanup.']
        if c.category == 'Power & battery':
            return ['Choose an HTML report destination for /batteryreport or /energy.',
                    'Battery reports can be empty or unavailable on desktops.']
        if c.id == 'net.test_connection':
            return ['Check the hostname and TCP port before executing the command.',
                    'A failed TCP test may mean that the remote port is blocked, not that Windows is broken.']
        if c.category == 'Networking':
            return ['Try read-only network diagnostics before resetting the network stack.',
                    'Network reset operations can require a reboot or reconfiguration.']
        return ['These are built-in Windows tools; some need administrator permission.',
                'Review the description and safety notes before running commands.']

    def _validate_network_before_action(self, c: Command) -> bool:
        if not c.needs_network:
            return True
        try:
            validate_network_host(self.host_var.get())
            validate_network_port(self.port_var.get())
        except ValueError as exc:
            messagebox.showwarning('Invalid network target', str(exc), parent=self)
            return False
        return True

    def _copy_command(self):
        c = self.current
        if not self._validate_network_before_action(c):
            return
        if c.uses_drive and self.drive_var.get() not in self.drives:
            messagebox.showwarning('Drive unavailable', 'Refresh drives and select an available local volume.')
            return
        if (c.needs_file and not self.selected_file) or (c.needs_report and not self.selected_report):
            messagebox.showinfo('Choose a destination', 'Choose the required system file or report destination first.')
            return
        text = display_command(c, self.drive_var.get(), self.selected_file, self.selected_report,
                               self.host_var.get(), self.port_var.get())
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()
        self.status_var.set('Command copied to clipboard')

    def _run(self):
        c = self.current
        if not self._validate_network_before_action(c):
            return
        if c.uses_drive and self.drive_var.get() not in self.drives:
            messagebox.showwarning('Drive unavailable', 'Refresh drives and select an available local volume.')
            return
        if (c.needs_file and not self.selected_file) or (c.needs_report and not self.selected_report):
            messagebox.showwarning('Selection required', 'Choose the required system file or HTML report destination first.')
            return
        if c.risk != 'read':
            preview = display_command(c, self.drive_var.get(), self.selected_file, self.selected_report,
                                      self.host_var.get(), self.port_var.get())
            if c.risk == 'heavy':
                warning = ('This operation can be intensive or disrupt system/network configuration.\n\n'
                           'Back up important data and review the notes first.\n\n')
            else:
                warning = ('This action can change Windows settings, repair system files, or create/overwrite a report.\n\n')
            if c.restart != 'No':
                warning += f'Restart: {c.restart}\n\n'
            warning += f'Execute this command?\n\n{preview}'
            if not messagebox.askyesno('Confirm system command', warning, icon='warning'):
                return
        if os.name != 'nt':
            messagebox.showinfo('Windows required',
                                'This interface can be previewed here, but commands run only on Windows 10/11.')
            return
        try:
            launch(c, self.drive_var.get(), self.selected_file, self.selected_report,
                   self.host_var.get(), self.port_var.get())
            self.status_var.set('Command launched — see the separate Windows window for results')
            # Do not claim success: ShellExecute only confirms that Windows accepted the launch.
            if not self.expert_var.get():
                messagebox.showinfo('Launch requested',
                                    'Windows accepted the launch request.\n\n'
                                    'For console commands, a separate terminal stays open for output. '
                                    'This does not mean the operation completed successfully.')
        except (ValueError, FileNotFoundError, RuntimeError, OSError) as exc:
            messagebox.showerror('Command not launched', str(exc))
            self.status_var.set('Launch failed or canceled')


def main() -> int:
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    try:
        window = AdminToolkit()
        window.mainloop()
        return 0
    except tk.TclError as error:
        print(f'Could not start graphical interface: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
