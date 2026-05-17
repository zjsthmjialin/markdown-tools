import sys
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters.markitdown_converter import MarkItDownConverter
from converters.pdf_converter import PDFConverter
from utils.image_extractor import ImageExtractor


class ConversionHandler(BaseHTTPRequestHandler):
    # 只支持正向转换：文档 -> Markdown
    converters = {
        '.pdf': PDFConverter(),         # fast PyMuPDF text extraction + OCR fallback
        '.docx': MarkItDownConverter(),  # Microsoft MarkItDown
        '.doc': MarkItDownConverter(),
        '.xlsx': MarkItDownConverter(),
        '.xls': MarkItDownConverter(),
        '.pptx': MarkItDownConverter(),
        '.ppt': MarkItDownConverter(),
        '.html': MarkItDownConverter(),
        '.htm': MarkItDownConverter(),
        '.txt': MarkItDownConverter(),
    }

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            result = self.process_conversion(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            error_result = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def process_conversion(self, data):
        file_path = data.get('filePath')
        target_format = data.get('targetFormat', 'md')

        if not file_path or not os.path.exists(file_path):
            return {'success': False, 'error': f'文件不存在: {file_path}'}

        # 只支持转换为 Markdown
        if target_format != 'md':
            return {'success': False, 'error': f'仅支持转换为 Markdown 格式'}

        output_dir = data.get('outputDir') or os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.converters and ext != '.md':
            return {'success': False, 'error': f'不支持的文件格式: {ext}'}

        try:
            return self.convert_to_markdown(file_path, ext, output_dir)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'转换失败: {str(e)}'}

    def convert_to_markdown(self, file_path, ext, output_dir):
        converter = self.converters.get(ext)
        if not converter:
            return {'success': False, 'error': f'不支持的格式: {ext}'}

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, base_name + '.md')

        markdown_content = converter.to_markdown(file_path, output_dir)

        # Extract embedded images from the source document
        image_map = self._extract_images(file_path, ext, output_dir)
        if image_map:
            image_lines = ['\n\n---\n\n## Extracted Images\n']
            for _, saved_filename in image_map.items():
                image_lines.append(f'\n![image](images/{saved_filename})\n')
            markdown_content += ''.join(image_lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {'success': True, 'outputPath': output_path, 'content': markdown_content}

    def _extract_images(self, file_path, ext, output_dir):
        """Dispatch to the appropriate ImageExtractor method based on file extension."""
        try:
            if ext == '.pdf':
                return ImageExtractor.extract_from_pdf(file_path, output_dir)
            elif ext == '.docx':
                return ImageExtractor.extract_from_docx(file_path, output_dir)
            elif ext == '.pptx':
                return ImageExtractor.extract_from_pptx(file_path, output_dir)
        except Exception:
            pass
        return {}


def run_server(port=8765):
    server = HTTPServer(('127.0.0.1', port), ConversionHandler)
    print(f'Python conversion service running on port {port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)