from abc import ABC, abstractmethod
import re


def sanitize_text(text: str) -> str:
    """Remove NULL bytes and control characters invalid in XML/Markdown."""
    # Remove NULL bytes
    text = text.replace('\x00', '')
    # Remove control characters except tab, newline, carriage return
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text


class BaseConverter(ABC):
    @abstractmethod
    def to_markdown(self, file_path: str, output_dir: str) -> str:
        """将文件转换为 Markdown"""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """返回支持的文件扩展名"""
        pass

    def extract_images(self, file_path: str, output_dir: str) -> dict:
        """提取文件中的图片，返回 {original_name: new_path}"""
        return {}