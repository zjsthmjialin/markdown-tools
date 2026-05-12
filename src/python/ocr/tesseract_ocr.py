import pytesseract
from PIL import Image
import io

class TesseractOCR:
    def __init__(self, languages='chi_sim+eng'):
        self.languages = languages

    def extract_text_from_image(self, image_data: bytes) -> str:
        """从图片数据中提取文字"""
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(
            image,
            lang=self.languages,
            config='--psm 6'
        )
        return text

    def extract_text_from_file(self, image_path: str) -> str:
        """从图片文件中提取文字"""
        text = pytesseract.image_to_string(
            Image.open(image_path),
            lang=self.languages,
            config='--psm 6'
        )
        return text

    def is_scanned_page(self, image_data: bytes, threshold: int = 100) -> bool:
        """判断是否为扫描件（文字内容少）"""
        text = self.extract_text_from_image(image_data)
        return len(text.strip()) < threshold