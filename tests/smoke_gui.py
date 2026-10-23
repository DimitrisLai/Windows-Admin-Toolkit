"""Optional GUI smoke test: python tests/smoke_gui.py (needs a graphical display)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import AdminToolkit

app = AdminToolkit()
app.update()
assert len(app.visible_commands) == 69
assert not app.expert_var.get()
assert app.expert_toggle.cget('text') == 'EXPERT: OFF'
app.expert_toggle.invoke()
assert app.expert_var.get()
assert app.expert_toggle.cget('text') == 'EXPERT: ON'
assert 'launch notices hidden' in app.status_var.get()
app.expert_toggle.invoke()
assert not app.expert_var.get()
assert app.expert_toggle.cget('text') == 'EXPERT: OFF'
assert app.current.id == 'disk.recover'
assert str(app.drive_box.cget('state')) == 'readonly'
app.search_var.set('command-that-does-not-exist')
app.update()
assert len(app.visible_commands) == 0
assert str(app.file_button.cget('state')) == 'disabled'
assert str(app.report_button.cget('state')) == 'disabled'
assert str(app.run_button.cget('state')) == 'disabled'
app._refresh_drives()
assert str(app.run_button.cget('state')) == 'disabled'
app.search_var.set('sfc')
app.update()
assert {'sfc.scan', 'sfc.verify', 'sfc.file'}.issubset({x.id for x in app.visible_commands})
app.category_var.set('Networking')
app.search_var.set('')
app._populate_commands()
assert len(app.visible_commands) == 11
app.category_var.set('Power & battery')
app._populate_commands(select_id='power.battery')
app.update()
assert app.current.id == 'power.battery'
assert str(app.report_button.cget('state')) == 'normal'
assert str(app.run_button.cget('state')) == 'disabled'
assert str(app.drive_box.cget('state')) == 'disabled'
app.category_var.set('Temporary files')
app._populate_commands(select_id='temp.cleanmgr')
app.update()
assert app.current.id == 'temp.cleanmgr'
assert str(app.drive_box.cget('state')) == 'readonly'
app.category_var.set('All categories')
app._populate_commands(select_id='sfc.scan')
# Invalid file-picker paths must show an error instead of crashing Tk.
from unittest.mock import patch
app._populate_commands(select_id='sfc.file')
with patch('app.filedialog.askopenfilename', return_value=r'C:\Bad%TEMP%.dll'), \
     patch('app.messagebox.showerror') as error_box:
    app._choose_file()
    assert error_box.called
    assert app.selected_file is None
    assert str(app.run_button.cget('state')) == 'disabled'
app._populate_commands(select_id='sfc.scan')
assert str(app.drive_box.cget('state')) == 'disabled'
# Every command should render without exceptions (including missing report/file prompts).
for entry in __import__('command_catalog').COMMANDS:
    app.current = entry
    app._render_detail()
    app.update()
app.destroy()
print('GUI smoke checks OK')
