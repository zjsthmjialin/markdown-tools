from .base import BaseConverter, sanitize_text
from markitdown import MarkItDown as _MarkItDown


class MarkItDownConverter(BaseConverter):
    SUPPORTED = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.html', '.htm', '.txt']

    def get_supported_extensions(self) -> list[str]:
        return MarkItDownConverter.SUPPORTED

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        md = _MarkItDown()
        result = md.convert(file_path)
        # Clean control characters (MarkItDown may still emit some)
        return sanitize_text(result.text_content)