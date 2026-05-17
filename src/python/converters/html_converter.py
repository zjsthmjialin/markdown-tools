from .base import BaseConverter
from bs4 import BeautifulSoup
import html2text
import os

class HtmlConverter(BaseConverter):
    def get_supported_extensions(self) -> list[str]:
        return ['.html', '.htm']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除脚本和样式
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # 使用 html2text 转换
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # 不换行

        return h.handle(str(soup))

    def extract_images(self, file_path: str, output_dir: str) -> dict:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        image_map = {}

        for i, img in enumerate(soup.find_all('img'), 1):
            src = img.get('src', '')
            if src.startswith('http') or src.startswith('data:'):
                continue

            # 下载本地图片
            img_path = os.path.join(os.path.dirname(file_path), src)
            if os.path.exists(img_path):
                ext = os.path.splitext(src)[1] or '.png'
                new_name = f'image_{i}{ext}'
                new_path = os.path.join(output_dir, new_name)

                import shutil
                shutil.copy(img_path, new_path)
                image_map[src] = new_name

        return image_map