from converters.base import BaseConverter
from ocr.tesseract_ocr import TesseractOCR
import fitz

class PDFConverter(BaseConverter):
    def __init__(self):
        self.ocr = TesseractOCR()

    def get_supported_extensions(self) -> list[str]:
        return ['.pdf']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        doc = fitz.open(file_path)
        try:
            markdown_content = []
            total_text = 0

            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                total_text += len(text)
                if text.strip():
                    markdown_content.append(f"## 第 {page_num} 页\n")
                    markdown_content.append(text)

            # If almost no text, it's likely a scanned PDF — retry with OCR
            if total_text < 100 and markdown_content:
                return self._extract_with_ocr(file_path)

            return '\n\n'.join(markdown_content)
        finally:
            doc.close()

    def _extract_with_ocr(self, file_path: str) -> str:
        markdown_content = []
        doc = fitz.open(file_path)
        try:
            for page_num, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes('png')
                text = self.ocr.extract_text_from_image(img_bytes)
                if text.strip():
                    markdown_content.append(f"## 第 {page_num} 页\n")
                    markdown_content.append(text)
        finally:
            doc.close()
        return '\n\n'.join(markdown_content)
