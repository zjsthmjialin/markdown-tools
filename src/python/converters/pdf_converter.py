from .base import BaseConverter
import pdfplumber
import os
import re

class PDFConverter(BaseConverter):
    def get_supported_extensions(self) -> list[str]:
        return ['.pdf']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        markdown_content = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    markdown_content.append(f"## 第 {page_num} 页\n")
                    markdown_content.append(text)
                    markdown_content.append("\n")

        return '\n'.join(markdown_content)