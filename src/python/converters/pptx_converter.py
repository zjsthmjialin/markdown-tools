from .base import BaseConverter
from pptx import Presentation
from pptx.util import Inches
import os

class PptxConverter(BaseConverter):
    def get_supported_extensions(self) -> list[str]:
        return ['.pptx', '.ppt']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        prs = Presentation(file_path)
        markdown_parts = []

        for slide_num, slide in enumerate(prs.slides, 1):
            markdown_parts.append(f"## 幻灯片 {slide_num}\n")

            for shape in slide.shapes:
                if hasattr(shape, 'text') and shape.text.strip():
                    markdown_parts.append(shape.text.strip())
                    markdown_parts.append('')

                if shape.has_table:
                    markdown_parts.append(self._table_to_markdown(shape.table))
                    markdown_parts.append('')

        return '\n\n'.join(markdown_parts)

    def _table_to_markdown(self, table) -> str:
        rows = []
        for i, row in enumerate(table.rows):
            cells = [cell.text.strip() for cell in row.cells]
            rows.append('| ' + ' | '.join(cells) + ' |')
            if i == 0:
                rows.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
        return '\n'.join(rows)