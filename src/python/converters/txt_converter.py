from .base import BaseConverter, sanitize_text


class TxtConverter(BaseConverter):
    def get_supported_extensions(self) -> list[str]:
        return ['.txt']

    def to_markdown(self, file_path: str, output_dir: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return sanitize_text(content)
