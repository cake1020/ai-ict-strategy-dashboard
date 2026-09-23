from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
pdfmetrics.registerFont(TTFont('Korean', font_path))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='KTitle', parent=styles['Title'], fontName='Korean', fontSize=20, leading=26, textColor=HexColor('#0b1728'), spaceAfter=10))
styles.add(ParagraphStyle(name='KHeading', parent=styles['Heading2'], fontName='Korean', fontSize=13, leading=18, textColor=HexColor('#12355b'), spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name='KBody', parent=styles['BodyText'], fontName='Korean', fontSize=9.5, leading=15, spaceAfter=5))
styles.add(ParagraphStyle(name='KMeta', parent=styles['BodyText'], fontName='Korean', fontSize=8.5, leading=12, textColor=HexColor('#526174'), spaceAfter=2))
styles.add(ParagraphStyle(name='KBullet', parent=styles['BodyText'], fontName='Korean', fontSize=9.3, leading=14, leftIndent=12, firstLineIndent=-8, bulletIndent=0, spaceAfter=3))

def clean(s):
    s = s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    s = s.replace('**','').replace('`','')
    import re
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', s)
    return s

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Korean', 7.5)
    canvas.setFillColor(HexColor('#758195'))
    canvas.drawString(18*mm, 10*mm, 'AI·ICT 기술동향 분석 에이전트 | 자료 기반 생성본 | 2026-09-23')
    canvas.drawRightString(192*mm, 10*mm, f'{doc.page}')
    canvas.restoreState()

def convert(src):
    lines = src.read_text(encoding='utf-8').splitlines()
    story=[]
    first=True
    for line in lines:
        if not line.strip():
            story.append(Spacer(1, 3))
            continue
        if line.startswith('# '):
            story.append(Paragraph(clean(line[2:]), styles['KTitle']))
            first=False
        elif line.startswith('## '):
            story.append(Paragraph(clean(line[3:]), styles['KHeading']))
        elif line.startswith('- '):
            story.append(Paragraph('• ' + clean(line[2:]), styles['KBullet']))
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. '):
            story.append(Paragraph(clean(line), styles['KBullet']))
        elif line.startswith('---'):
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(clean(line), styles['KBody']))
    out=OUT/(src.stem+'.pdf')
    doc=SimpleDocTemplate(str(out), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm, title=src.stem, author='AI·ICT Strategy Desk')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out

if __name__ == '__main__':
    files=sorted(ROOT.glob('documents/report-*.md'))
    for f in files:
        print(convert(f))
    print('COUNT', len(files))
