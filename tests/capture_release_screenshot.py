"""Produce an illustrative screenshot of the real Tkinter interface on a desktop."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import ImageGrab
from app import AdminToolkit
app=AdminToolkit()
try:
    app.geometry('1480x830+40+32')
    app.update()
    app._populate_commands(select_id='net.test_connection')
    app.middle_canvas.yview_moveto(.50)
    app.update()
    app.after(300)
    app.update()
    x=app.winfo_rootx();y=app.winfo_rooty();w=app.winfo_width();h=app.winfo_height()
    img=ImageGrab.grab(bbox=(x,y,x+w,y+h))
    out=Path(__file__).resolve().parents[1]/'assets/app_preview.png'
    img.save(out)
    print(out,img.size)
finally:
    app.destroy()
