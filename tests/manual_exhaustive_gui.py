"""Full Tkinter click-flow exercise (real widgets, mocked Windows execution).

Windows: python tests/manual_exhaustive_gui.py
Linux CI with a virtual display: xvfb-run -a python tests/manual_exhaustive_gui.py
No Windows command is actually executed.
"""
import csv
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import AdminToolkit
from command_catalog import COMMANDS, categories, display_command

app = AdminToolkit()
checks = []

def check(entry, name, condition):
    ok = bool(condition)
    checks.append((entry, name, 'PASS' if ok else 'FAIL'))
    if not ok:
        raise AssertionError(f'{entry}: {name}')

try:
    app.update()
    check('GLOBAL', 'all commands initially present', len(app.visible_commands) == 73)
    check('GLOBAL', 'all 11 categories present', len(categories()) == 11)

    # Deliberately use a second drive so a hard-coded C: will be caught.
    with patch('app.available_drives', return_value=['C:', 'D:']):
        app._refresh_drives()
    check('GLOBAL','both drive choices available', list(app.drive_box['values']) == ['C:', 'D:'])
    app.drive_var.set('D:')

    for c in COMMANDS:
        # Actual listbox choice + actual Tk selection event, not a direct rendering shortcut.
        app.search_var.set('')
        app.category_var.set('All categories')
        app._populate_commands()
        idx = next(i for i,x in enumerate(app.visible_commands) if x.id == c.id)
        app.command_list.selection_clear(0, 'end')
        app.command_list.selection_set(idx)
        app.command_list.activate(idx)
        app.command_list.event_generate('<<ListboxSelect>>')
        app.update()
        check(c.id, 'listbox click selects the correct entry', app.current.id == c.id)
        check(c.id, 'category label correct', app.category_label.cget('text') == c.category)
        check(c.id, 'drive selector enabled only when needed',
              str(app.drive_box.cget('state')) == ('readonly' if c.uses_drive else 'disabled'))
        check(c.id, 'file chooser enabled only when needed',
              str(app.file_button.cget('state')) == ('normal' if c.needs_file else 'disabled'))
        check(c.id, 'report chooser enabled only when needed',
              str(app.report_button.cget('state')) == ('normal' if c.needs_report else 'disabled'))
        check(c.id, 'hostname entry enabled only when needed',
              str(app.host_entry.cget('state')) == ('normal' if c.needs_network else 'disabled'))
        check(c.id, 'port entry enabled only when needed',
              str(app.port_entry.cget('state')) == ('normal' if c.needs_network else 'disabled'))
        # Every command should have a visible explanation and a warning/notes.
        full_desc = ' '.join(w.cget('text') for w in app.detail_scroll.body.winfo_children()
                             if 'text' in w.keys())
        check(c.id, 'command explanation available in catalog', bool(c.description and c.notes and c.best_for))
        if c.needs_file or c.needs_report:
            check(c.id, 'action initially locked until target chosen',
                  str(app.copy_button.cget('state')) == 'disabled' and str(app.run_button.cget('state')) == 'disabled')
            if c.needs_file:
                with patch('app.filedialog.askopenfilename', return_value=r'C:\Windows\System32\kernel32.dll'):
                    app._choose_file()
                check(c.id, 'file chooser populates a valid target', bool(app.selected_file))
            else:
                # Test the actual save picker with a Windows path, but mock the
                # OS-dependent directory existence check in the Linux display.
                with patch('app.filedialog.asksaveasfilename', return_value=r'C:\Users\Public\My Report.html'), \
                     patch('app.Path') as path_mock:
                    path_mock.return_value.parent.is_dir.return_value = True
                    path_mock.return_value.name = 'My Report.html'
                    app._choose_report()
                check(c.id, 'report chooser populates a valid target', bool(app.selected_report))
        check(c.id, 'copy action unlocked for valid selection', str(app.copy_button.cget('state')) == 'normal')
        check(c.id, 'run action unlocked for valid selection', str(app.run_button.cget('state')) == 'normal')
        text = display_command(c, app.drive_var.get(), app.selected_file, app.selected_report)
        if c.uses_drive:
            check(c.id, 'selected D: inserted into command', 'D:' in text or 'DriveLetter D' in text or '/d D' in text)
        app.copy_button.invoke()
        check(c.id, 'copy button produces exact preview text', app.clipboard_get() == text)
        check(c.id, 'copy button updates status', 'copied' in app.status_var.get().lower())

        # Simulate 'No' on every system-changing confirmation, verify no launch.
        with patch('app.messagebox.askyesno', return_value=False) as ask, \
             patch('app.launch') as launch_mock, \
             patch('app.os.name', 'nt'), \
             patch('app.messagebox.showinfo'), patch('app.messagebox.showerror'):
            app.run_button.invoke()
            if c.risk != 'read':
                check(c.id, 'danger confirmation shown', ask.call_count == 1)
                check(c.id, 'cancel means no execution', launch_mock.call_count == 0)
            else:
                check(c.id, 'read-only command skips danger confirmation', ask.call_count == 0)
                check(c.id, 'read-only run reaches launcher', launch_mock.call_count == 1)
        # Positive click path: user accepts change, requested catalog command launches.
        with patch('app.messagebox.askyesno', return_value=True) as ask, \
             patch('app.launch') as launch_mock, \
             patch('app.os.name', 'nt'), \
             patch('app.messagebox.showinfo') as ok, patch('app.messagebox.showerror'):
            app.run_button.invoke()
            check(c.id, 'accepted run reaches launch exactly once', launch_mock.call_count == 1)
            check(c.id, 'correct command instance passed', launch_mock.call_args.args[0].id == c.id)
            check(c.id, 'launch-request dialog shown', ok.call_count == 1)

        # Emulate failed OS command launch: must never show success.
        with patch('app.messagebox.askyesno', return_value=True), \
             patch('app.launch', side_effect=OSError('Launch blocked')), \
             patch('app.os.name', 'nt'), \
             patch('app.messagebox.showinfo') as ok, \
             patch('app.messagebox.showerror') as fail:
            app.run_button.invoke()
            check(c.id, 'failed launch shows error not success', fail.call_count == 1 and ok.call_count == 0)

    # Invalid network input cannot activate Copy/Run or reach the launcher.
    app._populate_commands(select_id='net.test_connection')
    app.host_var.set('server;Remove-Item C:\\')
    app.update()
    check('NETWORK', 'injected hostname locks actions',str(app.run_button.cget('state'))=='disabled' and str(app.copy_button.cget('state'))=='disabled')
    app.host_var.set('192.0.2.10')
    app.port_var.set('0')
    app.update()
    check('NETWORK','invalid port locks actions',str(app.run_button.cget('state'))=='disabled')
    app.port_var.set('8443')
    app.update()
    check('NETWORK','valid network target unlocks actions',str(app.run_button.cget('state'))=='normal')
    app.copy_button.invoke()
    check('NETWORK','custom host and port appear in copy', '192.0.2.10' in app.clipboard_get() and '8443' in app.clipboard_get())
    app.host_var.set('www.microsoft.com');app.port_var.set('443')

    # Search by label, category, and description, plus empty-match controls.
    for term in ('sfc', 'ram', 'DNS', 'temporary', 'recovery', 'powercfg', 'no-such-command-xyz'):
        app.category_var.set('All categories')
        app.search_var.set(term)
        app.update()
        expected = [c for c in COMMANDS if term.lower() in (c.label+' '+c.category+' '+c.description+' '+c.best_for).lower()]
        check('SEARCH', term+' result count correct', len(app.visible_commands) == len(expected))
    check('SEARCH', 'no hits disables run', str(app.run_button.cget('state')) == 'disabled')
    check('SEARCH', 'no hits disables copy', str(app.copy_button.cget('state')) == 'disabled')
    app._refresh_drives()
    check('SEARCH', 'refresh drive cannot reactivate empty list', str(app.run_button.cget('state')) == 'disabled')
    app.search_var.set('')

    for category in categories():
        app.category_var.set(category)
        app._populate_commands()
        check('FILTER',category+' lists only its commands',len(app.visible_commands)==sum(c.category==category for c in COMMANDS))
    app.category_var.set('All categories')
    app._populate_commands()

    # Ctrl+F keyboard shortcut.
    app.event_generate('<Control-f>')
    app.update()
    check('KEYBOARD','Ctrl+F focuses search box', app.focus_get() == app.search_entry)

    # Check actual widgets do not get clipped when the user resizes down.
    for dimension in ('1080x620','1200x700','1460x865'):
        app.geometry(dimension)
        app.update()
        app.middle_canvas.yview_moveto(1)
        app.update()
        mid_bottom = app.mid.winfo_rooty()+app.mid.winfo_height()
        check('LAYOUT',dimension+' report control reachable after scrolling',
              app.report_button.winfo_height()>30 and app.report_button.winfo_rooty()+app.report_button.winfo_height() < mid_bottom)
        check('LAYOUT',dimension+' bottom action controls visible',
              app.copy_button.winfo_rooty()+app.copy_button.winfo_height()<=app.winfo_rooty()+app.winfo_height())

    # No drive and drive-list-change scenario: even a beginner cannot
    # accidentally run CHKDSK against a made-up C: volume.
    app._populate_commands(select_id='disk.fix')
    with patch('app.available_drives', return_value=[]):
        app._refresh_drives()
    check('DRIVES', 'no detected volumes disables drive picker',str(app.drive_box.cget('state'))=='disabled')
    check('DRIVES', 'no detected volumes disables run and copy',str(app.run_button.cget('state'))=='disabled' and str(app.copy_button.cget('state'))=='disabled')
    check('DRIVES', 'no detected volumes clears selected drive',app.drive_var.get()=='')
    with patch('app.messagebox.showwarning') as warn:
        app._run()
        check('DRIVES','forced run refuses missing drive',warn.called)
    with patch('app.available_drives',return_value=['D:']):
        app._refresh_drives()
    check('DRIVES','drive list can recover with only D:',app.drive_var.get()=='D:' and str(app.run_button.cget('state'))=='normal')

    # The overlooked novice clicks: small icon, double click, TEMP shortcut,
    # help link, middle mouse wheel and non-Windows message.
    app._populate_commands(select_id='sys.info')
    app.update()
    from tkinter import Button
    small_copy = [w for parent in app.detail_scroll.body.winfo_children()
                   for row in parent.winfo_children()
                   for w in row.winfo_children()
                   if isinstance(w, Button) and w.cget('text') == '▣']
    check('MISC','small copy icon present',len(small_copy)==1)
    small_copy[0].invoke()
    check('MISC','small copy icon copies command',app.clipboard_get()==display_command(app.current))
    check('MISC','double-click copy binding installed', bool(app.command_list.bind('<Double-Button-1>')))
    with patch('app.open_temp_cleaner') as cleaner:
        app.temp_button.invoke()
        check('MISC','TEMP button requests the cleaner dialog',cleaner.call_count==1)
    with patch('app.messagebox.showinfo') as info,patch('app.launch') as accidental:
        app.run_button.invoke()
        check('MISC','non-Windows execution shows explicit warning',info.call_count==1 and accidental.call_count==0)
    app.geometry('1080x620');app.update()
    app.middle_canvas.yview_moveto(0);app.update()
    from types import SimpleNamespace
    w=app.file_button
    event=SimpleNamespace(x_root=w.winfo_rootx()+5,y_root=w.winfo_rooty()+5,delta=-120,num=0)
    before=app.middle_canvas.yview()[0]
    app._wheel(event)
    app.update()
    check('MISC','scroll wheel moves middle panel',app.middle_canvas.yview()[0]>before)
    app.geometry('1460x865');app.update()
    app._populate_commands(select_id='sfc.scan')
    app.update()
    from tkinter import Label
    doc_links = [w for w in app.detail_scroll.body.winfo_children()
                 if isinstance(w, Label) and 'View official Microsoft documentation' in w.cget('text')]
    check('MISC','official documentation link visible for sourced command',len(doc_links)==1)
    with patch('app.webbrowser.open') as browse:
        doc_links[0].event_generate('<Button-1>')
        app.update()
        check('MISC','documentation link opens official URL',browse.call_count==1 and browse.call_args.args[0]==app.current.doc_url)

    # Invalid SFC picker cancels without keeping an unsafe path.
    app._populate_commands(select_id='sfc.file')
    with patch('app.filedialog.askopenfilename', return_value=r'C:\Bad%PATH%.dll'), \
         patch('app.messagebox.showerror') as err:
        app._choose_file()
        check('FILE', 'unsafe file path blocked',err.called and app.selected_file is None)
    check('FILE','unsafe file keeps run disabled',str(app.run_button.cget('state'))=='disabled')
    with patch('app.filedialog.askopenfilename', return_value=''):
        app._choose_file()
    check('FILE','cancel file picker no crash',app.selected_file is None)
    app._populate_commands(select_id='power.battery')
    with patch('app.filedialog.asksaveasfilename', return_value=''):
        app._choose_report()
    check('REPORT','cancel save picker retains disabled run',str(app.run_button.cget('state'))=='disabled')
    with patch('app.filedialog.asksaveasfilename', return_value=r'C:\unsafe&foo.html'), \
         patch('app.messagebox.showerror') as err:
        app._choose_report()
        check('REPORT','unsafe save path blocked',err.called and app.selected_report is None)

    print(f'PASS: {len(checks)} independently checked GUI conditions over 73 command entries.')
finally:
    app.destroy()
    export = Path(__file__).resolve().parents[1]/'GUI_TEST_MATRIX.csv'
    with export.open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(('command_id','test','status'));w.writerows(checks)
    print('Report:',export)
