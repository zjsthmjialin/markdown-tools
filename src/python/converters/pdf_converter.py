from converters.base import BaseConverter, sanitize_text
import fitz
import io
import cv2
import numpy as np
from PIL import Image


def enhance_scan_image(pil_image: Image.Image) -> Image.Image:
    """
    自适应图像增强，专为扫描件 OCR 预处理设计。
    根据图像实际内容自动调整，无需手动指定参数。

    处理步骤：
    1. 转为灰度（如果是彩色图像）
    2. 自适应去噪
    3. CLAHE 自适应对比度增强
    4. 自适应二值化
    """
    try:
        img = np.array(pil_image)

        # 1. 转灰度
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img

        # 2. 自适应去噪（保留文字边缘）
        denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

        # 3. CLAHE 自适应对比度增强（根据局部区域自动调整，不过曝）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. 自适应二值化（比全局阈值更智能，适应不均匀光照）
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )

        return Image.fromarray(binary)
    except Exception as e:
        print(f"[警告] 图像增强失败，使用原图: {e}")
        return pil_image


class PDFConverter(BaseConverter):
    def __init__(self, tesseract_path: str | None = None):
        self._tesseract_path = tesseract_path
        self._ocr = None

    @property
    def ocr(self):
        if self._ocr is None:
            try:
                from ocr.tesseract_ocr import TesseractOCR
                self._ocr = TesseractOCR(tesseract_path=self._tesseract_path)
            except Exception as e:
                self._ocr = False
                print(f"[PDFConverter] OCR not available: {e}")
        return self._ocr if self._ocr is not False else None

    def get_supported_extensions(self) -> list[str]:
        return ['.pdf']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        doc = fitz.open(file_path)
        try:
            ocr_available = self.ocr and self.ocr.available
            scanned = self._is_scanned_pdf(doc)

            if scanned and ocr_available:
                return self._extract_with_ocr(file_path)
            elif scanned:
                print("[PDFConverter] Scanned PDF detected but OCR unavailable")

            # Text extraction path — process page by page
            markdown_content = []
            needs_ocr = False
            total_text = 0

            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                text_len = len(text.strip())
                total_text += text_len

                # Pages with images but minimal text are scanned pages
                has_images = len(page.get_images(full=True)) > 0

                if has_images and text_len < 50 and ocr_available:
                    # This individual page is a scan — OCR it
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes('png')
                        pil_img = enhance_scan_image(Image.open(io.BytesIO(img_bytes)))
                        buf = io.BytesIO()
                        pil_img.save(buf, format='PNG')
                        text = self.ocr.extract_text_from_image(buf.getvalue())
                    except Exception as e:
                        markdown_content.append(f"## Page {page_num}\n")
                        markdown_content.append(f"[OCR error on this page: {e}]")
                        continue

                if text.strip():
                    cleaned = sanitize_text(text.strip())
                    if cleaned:
                        # Detect if extracted text looks like garbage
                        if self._text_looks_garbled(cleaned):
                            if ocr_available:
                                needs_ocr = True
                                break
                            else:
                                # Can't fix, include as-is with a warning
                                markdown_content.append(f"## Page {page_num}\n")
                                markdown_content.append(cleaned)
                        else:
                            markdown_content.append(f"## Page {page_num}\n")
                            markdown_content.append(cleaned)

            if needs_ocr:
                return self._extract_with_ocr(file_path)

            if not markdown_content and total_text == 0 and ocr_available:
                return self._extract_with_ocr(file_path)

            if not markdown_content:
                return f"[No extractable text content found in: {file_path}]"

            return '\n\n'.join(markdown_content)
        finally:
            doc.close()

    def _extract_with_ocr(self, file_path: str) -> str:
        ocr = self.ocr
        if not ocr:
            return f"[OCR unavailable — scanned PDF cannot be converted: {file_path}]"
        if not ocr.available:
            return f"[Tesseract OCR not functional. Check language data (eng, chi_sim). File: {file_path}]"

        markdown_content = []
        doc = fitz.open(file_path)
        try:
            for page_num, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes('png')
                try:
                    pil_img = enhance_scan_image(Image.open(io.BytesIO(img_bytes)))
                    buf = io.BytesIO()
                    pil_img.save(buf, format='PNG')
                    text = ocr.extract_text_from_image(buf.getvalue())
                except Exception as e:
                    markdown_content.append(f"## Page {page_num}\n")
                    markdown_content.append(f"[OCR error on this page: {e}]")
                    continue
                if text.strip():
                    cleaned = sanitize_text(text.strip())
                    if cleaned:
                        markdown_content.append(f"## Page {page_num}\n")
                        markdown_content.append(cleaned)

            if not markdown_content:
                return f"[OCR produced no text for: {file_path}]"

            return '\n\n'.join(markdown_content)
        finally:
            doc.close()

    def _is_scanned_pdf(self, doc: fitz.Document) -> bool:
        """Detect scanned PDF: most pages are image-only with negligible embedded text."""
        image_pages = 0
        text_pages = 0
        total_pages = len(doc)

        if total_pages == 0:
            return False

        for page in doc:
            text = page.get_text().strip()
            if len(text) > 30:
                text_pages += 1
            if len(page.get_images(full=True)) > 0:
                image_pages += 1

        image_ratio = image_pages / total_pages
        text_ratio = text_pages / total_pages

        return image_ratio > 0.3 and text_ratio < 0.3

    def _text_looks_garbled(self, text: str) -> bool:
        """Heuristic: text likely garbled if it has high ratio of replacement chars
        or control-like Unicode blocks."""
        if not text:
            return False
        # Replacement character U+FFFD
        replacement = text.count('�')
        # Private use area
        pua = sum(1 for c in text if '' <= c <= '')
        # Unicode non-characters
        nonchars = sum(1 for c in text if c in '￾￿')
        length = max(len(text), 1)
        bad_ratio = (replacement + pua + nonchars) / length
        return bad_ratio > 0.05 or replacement > 3
