import re
import os
from xml.sax.saxutils import escape as xml_escape

# Use 'markdown' PyPI library via subprocess to avoid name collision
# with local 'markdown' package (src/python/markdown/).
# For direct in-process usage, we delegate to a helper.
from docx import Document
from docx.shared import Pt


def _render_markdown_to_html(md_text: str) -> str:
    """Render Markdown to HTML using the PyPI markdown library, avoiding
    the namespace collision with our local markdown package."""
    import sys
    import codecs

    # Save and remove ALL markdown-related modules from sys.modules
    _saved = {}
    for key in list(sys.modules.keys()):
        if key == 'markdown' or key.startswith('markdown.'):
            _saved[key] = sys.modules.pop(key)

    # Remove ALL sys.path entries that could resolve to the local markdown package.
    # Check by seeing if the path contains 'markdown' subdir with __init__.py
    # that is NOT in site-packages.
    _orig_path = sys.path[:]
    sys.path = [p for p in sys.path
                if not (os.path.isfile(os.path.join(p, 'markdown', '__init__.py'))
                        and 'site-packages' not in p)]

    try:
        import markdown as _md_lib
        result = _md_lib.markdown(md_text, extensions=['tables', 'fenced_code'])
        return result
    except UnicodeDecodeError:
        # Fallback: try to clean the input text
        cleaned = md_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        return _md_lib.markdown(cleaned, extensions=['tables', 'fenced_code'])
    finally:
        # Restore everything
        sys.path = _orig_path
        sys.modules.update(_saved)


class MarkdownToDocument:
    def to_pdf(self, markdown_content: str, output_path: str) -> None:
        """将 Markdown 转换为 PDF，优先使用 WeasyPrint，回退使用 reportlab"""
        html_content = self._markdown_to_html(markdown_content)

        try:
            from weasyprint import HTML as WeasyHTML
            WeasyHTML(string=html_content).write_pdf(output_path)
        except (ImportError, OSError, Exception):
            # WeasyPrint 不可用或依赖缺失时，使用 reportlab 生成简单 PDF
            self._pdf_with_reportlab(markdown_content, output_path)

    def _pdf_with_reportlab(self, markdown_content: str, output_path: str) -> None:
        """使用 reportlab 生成 PDF（简化版本）"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 注册中文字体
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',   # 黑体
            'C:/Windows/Fonts/simsun.ttc',   # 宋体
        ]
        font_name = 'Helvetica'
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', fp))
                    font_name = 'ChineseFont'
                    break
                except Exception:
                    pass

        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                leftMargin=25*mm, rightMargin=25*mm,
                                topMargin=25*mm, bottomMargin=25*mm)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CNBody', fontName=font_name, fontSize=11, leading=18))
        styles.add(ParagraphStyle(name='CNH1', fontName=font_name, fontSize=20, leading=28, spaceAfter=12))
        styles.add(ParagraphStyle(name='CNH2', fontName=font_name, fontSize=16, leading=24, spaceAfter=10))
        styles.add(ParagraphStyle(name='CNH3', fontName=font_name, fontSize=13, leading=20, spaceAfter=8))

        elements = []
        for line in markdown_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # 标题
            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                level = len(heading.group(1))
                text = xml_escape(heading.group(2))
                style = [styles['CNH3'], styles['CNH3'], styles['CNH3'],
                          styles['CNH2'], styles['CNH1'], styles['CNH1']][min(level, 6) - 1]
                elements.append(Paragraph(text, style))
                continue

            # 列表
            if re.match(r'^[-*]\s+', line):
                elements.append(Paragraph(f'• {xml_escape(line[2:])}', styles['CNBody']))
                continue

            # 表格分隔行跳过
            if re.match(r'^\|[-\s|]+\|$', line):
                continue

            # 表格行
            if line.startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                row_text = ' | '.join(xml_escape(c) for c in cells)
                elements.append(Paragraph(row_text, styles['CNBody']))
                continue

            # 普通段落
            elements.append(Paragraph(xml_escape(line), styles['CNBody']))

        if elements:
            doc.build(elements)

    def to_docx(self, markdown_content: str, output_path: str) -> None:
        # Clean control characters that break XML
        markdown_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', markdown_content)
        doc = Document()

        lines = markdown_content.split('\n')
        in_code_block = False
        code_lines = []

        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    p = doc.add_paragraph()
                    run = p.add_run('\n'.join(code_lines))
                    run.font.name = 'Consolas'
                    run.font.size = Pt(10)
                    code_lines = []
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                level = len(heading.group(1))
                text = heading.group(2)
                doc.add_heading(text, level=min(level, 9))
                continue

            if re.match(r'^[-*]\s+', line):
                doc.add_paragraph(line[2:], style='List Bullet')
                continue

            if line.startswith('|'):
                # Skip separator rows
                if re.match(r'^\|[-\s|]+\|$', line):
                    continue
                # Render table rows as text
                cells = [c.strip() for c in line.split('|')[1:-1]]
                doc.add_paragraph(' | '.join(cells))
                continue

            if line.strip():
                doc.add_paragraph(line)

        doc.save(output_path)

    def to_pptx(self, markdown_content: str, output_path: str) -> None:
        """Convert Markdown to PPTX. Each H1 starts a new slide."""
        from pptx import Presentation
        from pptx.util import Inches, Pt, Emu

        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        # Split content by H1 headings into slides
        sections = re.split(r'\n(?=^#\s)', markdown_content, flags=re.MULTILINE)

        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue

            slide_layout = prs.slide_layouts[6]  # blank layout
            slide = prs.slides.add_slide(slide_layout)

            left = Inches(1)
            top = Inches(0.5)
            width = Inches(11.333)
            height = Inches(6.5)

            textbox = slide.shapes.add_textbox(left, top, width, height)
            tf = textbox.text_frame
            tf.word_wrap = True

            first = True
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                h_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if h_match:
                    level = len(h_match.group(1))
                    text = h_match.group(2)
                    p = tf.add_paragraph() if not first else tf.paragraphs[0]
                    first = False
                    p.text = text
                    if level == 1:
                        p.font.size = Pt(36)
                        p.font.bold = True
                    elif level == 2:
                        p.font.size = Pt(28)
                        p.font.bold = True
                    else:
                        p.font.size = Pt(22)
                        p.font.bold = True
                    p.space_after = Pt(12)
                    continue

                if re.match(r'^[-*]\s+', line):
                    p = tf.add_paragraph() if not first else tf.paragraphs[0]
                    first = False
                    p.text = f'  {line[2:]}'
                    p.font.size = Pt(18)
                    p.space_after = Pt(6)
                    continue

                if line.startswith('|'):
                    continue  # skip tables in PPT for simplicity

                # Regular paragraph
                p = tf.add_paragraph() if not first else tf.paragraphs[0]
                first = False
                p.text = line
                p.font.size = Pt(18)
                p.space_after = Pt(8)

        prs.save(output_path)

    def to_html(self, markdown_content: str, output_path: str) -> None:
        html_content = self._markdown_to_html(markdown_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _markdown_to_html(self, markdown_content: str) -> str:
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, "Noto Sans SC", "Microsoft YaHei", sans-serif;
        max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; }}
pre {{ background: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; }}
code {{ font-family: "JetBrains Mono", "Consolas", monospace; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
img {{ max-width: 100%; }}
</style>
</head>
<body>
{_render_markdown_to_html(markdown_content)}
</body>
</html>'''