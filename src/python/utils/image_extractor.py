import os
import shutil
from PIL import Image
import fitz  # PyMuPDF
from typing import Dict

class ImageExtractor:
    def extract_from_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, str]:
        """从 PDF 中提取所有图片"""
        image_map = {}

        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image['image']
                image_ext = base_image['ext']

                new_name = f'page{page_num + 1}_img{img_index + 1}.{image_ext}'
                new_path = os.path.join(output_dir, new_name)

                with open(new_path, 'wb') as f:
                    f.write(image_bytes)

                image_map[f'{xref}'] = new_name

        return image_map

    def extract_from_docx(self, docx_path: str, output_dir: str) -> Dict[str, str]:
        """从 Word 文档中提取所有图片"""
        from docx import Document
        image_map = {}

        doc = Document(docx_path)
        for rel in doc.part.rels.values():
            if 'image' in rel.reltype:
                image = rel.target_part.blob
                image_ext = rel.target_part.content_type.split('/')[-1]
                if 'jpeg' in rel.target_part.content_type:
                    image_ext = 'jpg'

                new_name = f'image_{len(image_map) + 1}.{image_ext}'
                new_path = os.path.join(output_dir, new_name)

                with open(new_path, 'wb') as f:
                    f.write(image)

                image_map[rel.target_ref] = new_name

        return image_map