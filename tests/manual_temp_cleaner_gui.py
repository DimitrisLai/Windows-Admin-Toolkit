"""Full TEMP cleaner GUI exercise; test fixture only, never touch actual system TEMP."""
import os, sys, tempfile, time, csv
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import AdminToolkit
from temp_cleaner import TempCleanerWindow

checks=[]
def chk(test,pred):
 checks.append((test,'PASS' if pred else 'FAIL'))
 if not pred: raise AssertionError(test)

def wait(app, predicate, timeout=8):
 until=time.monotonic()+timeout
 while time.monotonic()<until:
  app.update()
  if predicate():return
  time.sleep(.02)
 raise AssertionError('Timed out waiting for async TEMP task')

with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
 root=Path(tmp)
 old=root/'old (1).tmp'; old.write_bytes(b'x'*157)
 old2=root/'old2.txt'; old2.write_bytes(b'j'*120)
 fresh=root/'fresh.txt'; fresh.write_bytes(b'new file not eligible')
 fixed=(time.time()-18*86400)
 for f in [old,old2]: os.utime(f,(fixed,fixed))
 external=Path(outside)/'do-not-delete.tmp'; external.write_bytes(b'outside')
 os.utime(external,(fixed,fixed))
 try: (root/'shortcut').symlink_to(external)
 except (NotImplementedError,OSError): pass

 app=AdminToolkit()
 try:
  with patch('temp_cleaner.user_temp_root',return_value=tmp),patch('temp_cleaner.messagebox.showerror') as errors:
   win=TempCleanerWindow(app)
   wait(app,lambda: win.scan_data is not None and not win._busy)
   chk('scan finds only two aged local files',win.scan_data.eligible_files==2)
   chk('fresh file excluded',str(fresh) not in [f.path for f in win.scan_data.files])
   chk('external symlink excluded',str(root/'shortcut') not in [f.path for f in win.scan_data.files])
   chk('nothing selected automatically',not win.table.selection())
   chk('delete button disabled until user selection',win.delete_btn.cget('state')=='disabled')
   first=next(k for k,v in win.file_rows.items() if v.path==str(old))
   win.table.selection_set(first);win._update_delete_state();app.update()
   chk('select enables delete',win.delete_btn.cget('state')=='normal')
   with patch('temp_cleaner.messagebox.askyesno',return_value=False) as confirm:
    win.delete_selected()
   chk('cancel confirmation does not delete',old.exists() and confirm.called)
   with patch('temp_cleaner.messagebox.askyesno',return_value=True) as confirm:
    win.delete_selected()
    wait(app,lambda: win.scan_data is not None and win.scan_data.eligible_files==1 and not win._busy)
   chk('confirmed selection permanently removed',not old.exists())
   chk('other old file still present',old2.exists())
   chk('young file still present',fresh.exists())
   chk('outside symlink target remains',external.exists())
   chk('not silently reporting errors',not errors.called)
   chk('delete confirmation report visible', 'Deleted 1' in win.summary_var.get())
   win.destroy()
 finally:
  app.destroy()
 print('PASS',len(checks),'TEMP GUI checks')
