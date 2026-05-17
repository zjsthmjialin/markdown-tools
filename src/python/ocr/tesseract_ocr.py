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