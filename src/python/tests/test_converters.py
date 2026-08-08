import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters.markitdown_converter import MarkItDownConverter
from converters.pdf_converter import PDFConverter

TEST_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEST_FILES = os.path.join(TEST_DIR, 'test_files')
OUTPUT_DIR = os.path.join(TEST_DIR, 'test_output')


@pytest.fixture(autouse=True)
def setup_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    # Cleanup handled manually


def _test_file(name):
    path = os.path.join(TEST_FILES, name)
    if not os.path.exists(path):
        pytest.skip(f'Test file not found: {path}')
    return path


class TestMarkItDownConverter:
    converter = MarkItDownConverter()

    def test_docx_to_markdown(self):
        path = _test_file('sample.docx')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_xlsx_to_markdown(self):
        path = _test_file('sample.xlsx')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pptx_to_markdown(self):
        path = _test_file('sample.pptx')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_html_to_markdown(self):
        path = _test_file('sample.html')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_txt_to_markdown(self):
        path = _test_file('sample.md')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0


class TestPDFConverter:
    converter = PDFConverter()

    def test_pdf_to_markdown(self):
        path = _test_file('sample.pdf')
        result = self.converter.to_markdown(path, OUTPUT_DIR)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pdf_supported_extensions(self):
        assert self.converter.get_supported_extensions() == ['.pdf']
