"""Direct format-to-format converters."""

import os


class DirectConverter:
    """Handles direct conversion between formats without Markdown intermediate."""

    @staticmethod
    def pdf_to_pptx(file_path: str, output_dir: str) -> dict:
        """Convert PDF to PPTX by rendering each page as a high-res image."""
        import fitz
        from pptx import Presentation
        from pptx.util import Inches
        import io

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, base_name + '.pptx')
        os.makedirs(output_dir, exist_ok=True)

        doc = fitz.open(file_path)
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(slide_layout)
            img_stream = io.BytesIO(img_data)
            slide.shapes.add_picture(img_stream, Inches(0), Inches(0),
                                     Inches(13.333), Inches(7.5))

        doc.close()
        prs.save(output_path)
        return {'success': True, 'outputPath': output_path}

    _DIRECT_PAIRS = {
        ('.pdf', 'pptx'): 'pdf_to_pptx',
    }

    @staticmethod
    def can_direct_convert(source_ext: str, target_format: str) -> bool:
        return (source_ext, target_format) in DirectConverter._DIRECT_PAIRS

    @staticmethod
    def convert(file_path: str, source_ext: str, target_format: str, output_dir: str) -> dict:
        pair = (source_ext, target_format)
        if pair not in DirectConverter._DIRECT_PAIRS:
            return {'success': False, 'error': f'不支持的直接转换: {source_ext} -> {target_format}'}

        method_name = DirectConverter._DIRECT_PAIRS[pair]
        method = getattr(DirectConverter, method_name)
        return method(file_path, output_dir)