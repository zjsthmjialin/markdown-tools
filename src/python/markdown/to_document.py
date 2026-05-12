import re
from weasyprint import HTML as WeasyHTML
from docx import Document
from docx.shared import Pt
from io import BytesIO

class MarkdownToDocument:
    def to_pdf(self, markdown_content: str, output_path: str) -> None:
        html_content = self._markdown_to_html(markdown_content)

        WeasyHTML(string=html_content).write_pdf(output_path)

    def to_docx(self, markdown_content: str, output_path: str) -> None:
        doc = Document()

        lines = markdown_content.split('\n')
        in_code_block = False
        code_lines = []

        for line in lines:
            # 代码块
            if line.strip().startswith('```'):
                if in_code_block:
                    # 结束代码块
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

            # 标题
            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                level = len(heading.group(1))
                text = heading.group(2)
                p = doc.add_heading(text, level=min(level, 9))
                continue

            # 列表
            if re.match(r'^[-*]\s+', line):
                p = doc.add_paragraph(line[2:], style='List Bullet')
                continue

            # 表格行
            if line.startswith('|'):
                continue  # 简化处理

            # 普通段落
            if line.strip():
                doc.add_paragraph(line)

        doc.save(output_path)

    def to_html(self, markdown_content: str, output_path: str) -> None:
        html_content = self._markdown_to_html(markdown_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _markdown_to_html(self, markdown_content: str) -> str:
        # 简单的 Markdown 到 HTML 转换
        import markdown
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, "Noto Sans SC", sans-serif;
        max-width: 800px; margin: 0 auto; padding: 20px; }}
pre {{ background: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; }}
code {{ font-family: "JetBrains Mono", monospace; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
</style>
</head>
<body>
{markdown.markdown(markdown_content)}
</body>
</html>'''