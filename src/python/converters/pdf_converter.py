from .base import BaseConverter
from ..ocr.tesseract_ocr import TesseractOCR
from ..utils.image_extractor import ImageExtractor
import pdfplumber
import fitz
import os
import io

class PDFConverter(BaseConverter):
    def __init__(self):
        self.ocr = TesseractOCR()
        self.image_extractor = ImageExtractor()

    def get_supported_extensions(self) -> list[str]:
        return ['.pdf']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        # 先尝试提取文本
        markdown_content = self._extract_text_pdf(file_path)

        # 如果文本内容过少，可能是扫描件，尝试 OCR
        if self._is_likely_scanned(file_path):
            markdown_content = self._extract_with_ocr(file_path)

        return markdown_content

    def _extract_text_pdf(self, file_path: str) -> str:
        markdown_content = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    markdown_content.append(f"## 第 {page_num} 页\n")
                    markdown_content.append(text)

        return '\n\n'.join(markdown_content)

    def _is_likely_scanned(self, file_path: str) -> bool:
        with pdfplumber.open(file_path) as pdf:
            total_text = sum(
                len(page.extract_text() or '') for page in pdf.pages
            )
        return total_text < 100

    def _extract_with_ocr(self, file_path: str) -> str:
        markdown_content = []
        doc = fitz.open(file_path)

        for page_num, page in enumerate(doc, 1):
            # 将页面转为图片
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes('png')

            # OCR 识别
            text = self.ocr.extract_text_from_image(img_bytes)

            if text.strip():
                markdown_content.append(f"## 第 {page_num} 页\n")
                markdown_content.append(text)

        return '\n\n'.join(markdown_content)