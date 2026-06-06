from converters.base import BaseConverter, sanitize_text
import fitz
import io
import re
import cv2
import numpy as np
from PIL import Image


def enhance_scan_image(pil_image: Image.Image) -> Image.Image:
    """
    自适应图像增强，专为扫描件 OCR 预处理设计。

    处理步骤：
    1. 转为灰度（如果是彩色图像）
    2. 自适应去噪
    3. CLAHE 自适应对比度增强
    4. 自适应二值化
    """
    try:
        img = np.array(pil_image)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img

        denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
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

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def to_markdown(self, file_path: str, output_dir: str, options: dict | None = None) -> str:
        doc = fitz.open(file_path)
        try:
            ocr_available = self.ocr and self.ocr.available
            force_ocr = (options or {}).get('forceOCR', False)

            if not force_ocr:
                scanned, sparse = self._detect_pdf_type(doc)
                if scanned:
                    if ocr_available:
                        return self._extract_with_ocr(file_path)
                    else:
                        print("[PDFConverter] Scanned PDF detected but OCR unavailable")
                elif sparse:
                    force_ocr = True

            if force_ocr:
                if ocr_available:
                    return self._extract_with_ocr(file_path)
                else:
                    print("[PDFConverter] Sparse text PDF but OCR unavailable")

            # 文字版 PDF：结构化提取
            return self._extract_text(doc, file_path, ocr_available)
        finally:
            doc.close()

    # ------------------------------------------------------------------
    # PDF 类型检测（单次遍历）
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_pdf_type(doc: fitz.Document) -> tuple[bool, bool]:
        """单次遍历同时检测：是否扫描版 + 是否文本极度稀少。
        Returns: (is_scanned, is_sparse)"""
        total_pages = len(doc)
        if total_pages == 0:
            return False, False

        image_pages = 0
        text_pages = 0
        total_text = 0

        for page in doc:
            text = page.get_text().strip()
            text_len = len(text)
            total_text += text_len
            if text_len > 50:
                text_pages += 1
            if len(page.get_images(full=True)) > 0:
                image_pages += 1

        image_ratio = image_pages / total_pages
        text_ratio = text_pages / total_pages
        is_scanned = image_ratio > 0.3 and text_ratio < 0.3
        is_sparse = (total_text / total_pages) < 10

        return is_scanned, is_sparse

    # ------------------------------------------------------------------
    # 文字版 PDF：结构化提取（dict 格式，保留粗体/斜体/字号）
    # ------------------------------------------------------------------

    def _extract_text(self, doc: fitz.Document, file_path: str, ocr_available: bool) -> str:
        """用 page.get_text('dict', flags=TEXT_PRESERVE_WHITESPACE) 提取，
        同时获取文字内容和字体信息，速度与纯文本相当。"""
        # 全局检测：整份文档的正文字号和正文字体（跨页统计，避免单页误判）
        global_body_size, global_body_font = self._detect_global_body_font(doc)

        markdown_content = []
        needs_full_ocr = False

        for page_num, page in enumerate(doc, 1):
            page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            blocks = page_dict.get("blocks", [])

            has_text = any(b.get("type") == 0 for b in blocks)
            if not has_text:
                continue

            # 用全局正文字号和字体转换
            page_md = self._dict_page_to_markdown(blocks, global_body_size, global_body_font)

            if not page_md:
                continue

            cleaned = sanitize_text(page_md)
            if not cleaned:
                continue

            if self._text_looks_garbled(cleaned):
                if ocr_available:
                    needs_full_ocr = True
                    break
                else:
                    markdown_content.append('---')
                    markdown_content.append(cleaned)
            else:
                markdown_content.append('---')
                markdown_content.append(cleaned)

        if needs_full_ocr:
            return self._extract_with_ocr(file_path)

        if not markdown_content:
            return f"[No extractable text content found in: {file_path}]"

        return '\n\n'.join(markdown_content)

    @staticmethod
    def _detect_body_font_size(blocks: list) -> float:
        """检测页面正文字号（按文字总量取众数），用于区分标题和正文。"""
        size_count: dict[float, int] = {}
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span.get("size", 0), 1)
                    if size > 0:
                        size_count[size] = size_count.get(size, 0) + len(span.get("text", ""))
        if not size_count:
            return 10.0
        return max(size_count, key=size_count.get)

    @staticmethod
    def _detect_global_body_font(doc: fitz.Document) -> tuple[float, str]:
        """跨整份文档统计：找出正文字号（众数）和该字号下的正文字体（众数）。
        全局统计避免了单页（如版权页）字体特征不同导致的误判。"""
        size_count: dict[float, int] = {}
        font_at_body: dict[str, int] = {}

        for page in doc:
            page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text_len = len(span.get("text", ""))
                        if text_len == 0:
                            continue
                        size = round(span.get("size", 0), 1)
                        size_count[size] = size_count.get(size, 0) + text_len

        if not size_count:
            return 10.0, ""

        body_size = max(size_count, key=size_count.get)

        # 在正文字号下统计字体
        for page in doc:
            page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if abs(span.get("size", 0) - body_size) < 0.5:
                            fn = span.get("font", "")
                            text_len = len(span.get("text", ""))
                            if fn and text_len > 0:
                                font_at_body[fn] = font_at_body.get(fn, 0) + text_len

        body_font = max(font_at_body, key=font_at_body.get) if font_at_body else ""
        return body_size, body_font

    @staticmethod
    def _dict_page_to_markdown(blocks: list, body_size: float, body_font: str) -> str:
        """将 PyMuPDF dict blocks 转为 Markdown，保留粗体/斜体，按字号检测标题。
        粗体检测逻辑：许多 PDF（尤其中文）不用 flags 标记粗体，
        而是切换为更粗的字体（如黑体替换宋体），因此需对比正文字体。"""
        lines_out = []

        for block in blocks:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue

                parts = []
                line_size = spans[0].get("size", 0)

                for span in spans:
                    text = span.get("text", "")
                    if not text or not text.strip():
                        continue

                    span_font = span.get("font", "")
                    span_flags = span.get("flags", 0)

                    # 粗体检测：flags 位 + 字体名 + 与正文字体对比
                    is_bold = PDFConverter._is_bold_span(
                        span_font, span_flags, body_font, body_size,
                        span.get("size", 0)
                    )
                    is_italic = bool(span_flags & (1 << 1))

                    if is_bold and is_italic:
                        parts.append(f"***{text.strip()}***")
                    elif is_bold:
                        parts.append(f"**{text.strip()}**")
                    elif is_italic:
                        parts.append(f"*{text.strip()}*")
                    else:
                        parts.append(text.strip())

                if not parts:
                    continue

                full_line = ' '.join(parts)

                # 标题检测：字号明显大于正文时才标记
                if body_size > 0 and line_size > body_size * 1.5:
                    full_line = f"# {full_line}"
                elif body_size > 0 and line_size > body_size * 1.3:
                    full_line = f"## {full_line}"
                elif body_size > 0 and line_size > body_size * 1.15:
                    full_line = f"### {full_line}"

                lines_out.append(full_line)

        return '\n'.join(lines_out)

    @staticmethod
    def _detect_body_font(blocks: list, body_size: float) -> str:
        """检测正文字号下使用最多的字体（即正文字体），用于粗体对比。"""
        font_count: dict[str, int] = {}
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if abs(span.get("size", 0) - body_size) < 0.5:
                        fn = span.get("font", "")
                        if fn:
                            font_count[fn] = font_count.get(fn, 0) + len(span.get("text", ""))
        if not font_count:
            return ""
        return max(font_count, key=font_count.get)

    @staticmethod
    def _is_bold_span(font_name: str, flags: int, body_font: str,
                       body_size: float, span_size: float) -> bool:
        """综合判断 span 是否为粗体，支持中文字体的多种粗体实现方式。"""
        lower = font_name.lower()

        # 方式1：flags bit 4 标记（西方字体常用）
        if flags & (1 << 4):
            return True

        # 方式2：字体名包含常见粗体关键词
        if any(kw in lower for kw in ('bold', 'black', 'heavy', 'demi', 'ultra')):
            return True

        # 方式3（核心）：与正文字体不同 + 同字号 → 可能是加粗
        # 但需排除：细体、斜体、衬线体（宋体/仿宋/楷体等不是粗体）
        if (body_font
                and font_name != body_font
                and abs(span_size - body_size) < 0.5):
            # 排除明确不是粗体的字体
            if any(kw in lower for kw in ('light', 'thin', 'italic',
                                           'song', 'kai', 'fs', 'fangsong')):
                return False
            return True

        return False

    # ------------------------------------------------------------------
    # 全文档 OCR 流
    # ------------------------------------------------------------------

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
                    markdown_content.append('---')
                    markdown_content.append(f"[OCR error on this page: {e}]")
                    continue
                if text.strip():
                    cleaned = sanitize_text(text.strip())
                    if cleaned:
                        markdown_content.append('---')
                        markdown_content.append(cleaned)

            if not markdown_content:
                return f"[OCR produced no text for: {file_path}]"

            return '\n\n'.join(markdown_content)
        finally:
            doc.close()

    # ------------------------------------------------------------------
    # 辅助检测方法
    # ------------------------------------------------------------------

    @staticmethod
    def _text_looks_garbled(text: str) -> bool:
        """启发式检测：高比例替换字符或私有区字符 → 文本可能乱码。"""
        if not text:
            return False
        replacement = text.count('�')
        pua = sum(1 for c in text if '' <= c <= '')
        nonchars = sum(1 for c in text if c in '￾￿')
        length = max(len(text), 1)
        bad_ratio = (replacement + pua + nonchars) / length
        return bad_ratio > 0.05 or replacement > 3
