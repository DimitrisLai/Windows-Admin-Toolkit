#!/usr/bin/env python3
"""Generate a printable PDF from the repository's official manual and command reference.

Requires: pip install mistune==3.2.0 weasyprint==68.0
Run: python docs/build_pdf.py
"""
from pathlib import Path
import re
import html
import mistune
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Windows_Admin_Toolkit_Detailed_Guide.pdf"

STYLE = """
@page {size:A4; margin:17mm 16mm 19mm;
 @top-left{content:'WINDOWS ADMIN TOOLKIT  /  USER GUIDE';color:#6b7e95;font:8pt sans-serif;}
 @top-right{content:'v1.2.0 BETA';color:#6b7e95;font:8pt sans-serif;}
 @bottom-right{content:counter(page);color:#52657c;font:9pt sans-serif;}
 @bottom-left{content:'Free and open source  •  MIT License';color:#8794a5;font:8pt sans-serif;}}
@page:first{margin:0;@top-left{content:none}@top-right{content:none}
 @bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}
body{margin:0;font:9.2pt/1.5 'DejaVu Sans',sans-serif;color:#22364b}
.cover{height:297mm;page-break-after:always;background:#0d1929;color:white;padding:22mm 21mm}
.cover h1{font-size:29pt;line-height:1.2;margin:16mm 0 6mm;color:white}
.cover .cap{color:#7db7ff;letter-spacing:2px;font-weight:bold}
.cover .sub{font-size:14pt;color:#b2c7dd;margin-bottom:12mm}
.cover .metric{display:inline-block;background:#20344d;border-radius:5px;padding:3mm 4mm;
 margin:0 3mm 7mm 0;font-weight:bold}
.cover img{max-width:100%;max-height:106mm;border:2px solid #364b65;border-radius:7px}
.cover .fine{margin-top:10mm;color:#bbcee2;font-size:9pt}
.cover .last{color:#96abc3;font-size:8pt;margin-top:5mm}
a{color:#1664ae;text-decoration:none;overflow-wrap:anywhere}
h1{font-size:19pt;color:#133d71;margin:7mm 0 5mm;break-after:avoid}
h2{font-size:15pt;color:#194a7d;margin:7mm 0 3mm;break-after:avoid}
h3{font-size:10.8pt;color:#12436f;margin:6mm 0 3mm;break-after:avoid}
p{margin:2mm 0 3mm;orphans:3;widows:3}
ol,ul{padding-left:6mm;margin:2mm 0 4mm}li{margin-bottom:1.2mm}
strong{color:#153557}
code{font-family:'DejaVu Sans Mono',monospace;font-size:8.3pt;background:#edf3fa;
 padding:1px 3px;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#12243a;color:white;padding:4mm}
pre code{background:none;color:white}
table{width:100%;border-collapse:collapse;font-size:8.4pt;margin:3mm 0 5mm}
td,th{padding:2mm;border-bottom:1px solid #dae4ef;vertical-align:top}
th{background:#173e6c;color:white}
tr:nth-child(even){background:#f6f9fc}
.entry{page-break-after:avoid;background:#f0f6fc;border-left:4px solid #2770b6;padding:3mm 4mm}
.entry code{background:none;color:#124570;font-size:9.1pt}
.category{font-size:16pt;color:#124477;border-bottom:1.5px solid #bad1eb;padding-bottom:2mm}
.chapter{page-break-before:always;font-size:19pt;border-bottom:2px solid #2668ac;padding-bottom:2mm}
.toc{page-break-after:always}.toc h1{margin-top:5mm}
.toc a{display:block;padding:1.8mm 0;border-bottom:1px solid #dce5ef}
.toc a:after{content:leader('.') target-counter(attr(href),page);color:#728399}
.caution{background:#eef6ff;border:1px solid #c7dcf2;padding:4mm;margin:5mm 0}
"""
def main():
    manual = (ROOT / "USER_MANUAL.md").read_text(encoding="utf-8")
    commands = (ROOT / "COMMAND_REFERENCE.md").read_text(encoding="utf-8")
    assert commands.count("### \`") == 69, "Unexpected catalog count; review before publishing"
    markdown = mistune.create_markdown(plugins=["table", "strikethrough", "url"])
    sections = []
    num = 0
    def anchor(m):
        nonlocal num
        num += 1
        name = re.sub(r"<[^>]+>", "", m.group(1))
        sections.append((num, name))
        return '<h2 id="cat-%d" class="category">%s</h2>' % (num,m.group(1))
    ref = markdown(commands)
    ref = re.sub(r"<h2>(.*?)</h2>",anchor,ref,flags=re.S)
    ref = ref.replace("<h3>","<h3 class='entry'>")
    toc = "<section class='toc'><h1>Contents</h1><p>Step-by-step usage instructions and every available Windows command.</p>"
    toc += "<a href='#guide'>1. Getting started and safety</a><a href='#reference'>2. Complete command reference</a>"
    for num, name in sections:
        toc += "<a href='#cat-%d'>%s</a>" % (num, html.escape(name))
    toc += "<div class='caution'><strong>Important:</strong> A successful launch is not proof that a command completed or repaired Windows. Always read its output.</div></section>"
    cover = """<section class='cover'><div class='cap'>WINDOWS ADMIN TOOLKIT</div>
    <h1>The Complete User Guide<br>&amp; Command Handbook</h1>
    <div class='sub'>Understand 69 Windows maintenance and diagnostic tools</div>
    <div class='metric'>69 built-in commands</div><div class='metric'>11 categories</div>
    <div class='metric'>v1.2.0 Beta</div><br>
    <img src='assets/app_preview.png'>
    <p class='fine'>Installation · explanations · real examples · safety · official references</p>
    <p class='last'>October 2026 · Windows 10/11 · MIT License<br>github.com/DimitrisLai/Windows-Admin-Toolkit</p></section>"""
    page = "<!doctype html><html lang='en'><head><meta charset='utf-8'><style>"+STYLE+"</style></head><body>"
    page += cover + toc + "<h1 class='chapter' id='guide'>Part 1 · Getting started and safety</h1>"
    page += markdown(manual) + "<h1 class='chapter' id='reference'>Part 2 · The 69-command handbook</h1>"
    page += "<div class='caution'>Each entry gives a description, use case, warnings, example syntax, elevation/drive requirements, and official documentation. Descriptions come from the tested beta's command catalog; command execution still requires Windows validation.</div>"
    page += ref + "</body></html>"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=page, base_url=str(ROOT)+"/").write_pdf(str(OUT), pdf_version="1.7")
    print("Generated", OUT, "bytes", OUT.stat().st_size)
if __name__ == "__main__":
    main()
