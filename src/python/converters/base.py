from abc import ABC, abstractmethod
from typing import Optional
import os

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

    def get_file_info(self, file_path: str) -> dict:
        """获取文件基本信息"""
        return {
            'name': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'extension': os.path.splitext(file_path)[1]
        }