import sys
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters.markitdown_converter import MarkItDownConverter
from converters.pdf_converter import PDFConverter
from converters.direct_converter import DirectConverter
from markdown.to_document import MarkdownToDocument

class ConversionHandler(BaseHTTPRequestHandler):
    # All non-PDF formats use MarkItDown, PDF uses its own with OCR fallback
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
    markdown_converter = MarkdownToDocument()

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
        source_format = data.get('sourceFormat', 'auto')
        target_format = data.get('targetFormat', 'md')

        if not file_path or not os.path.exists(file_path):
            return {'success': False, 'error': f'文件不存在: {file_path}'}

        output_dir = data.get('outputDir') or os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if source_format == 'auto':
            if ext in self.converters or ext == '.md':
                pass
            else:
                return {'success': False, 'error': f'不支持的文件格式: {ext}'}
        else:
            ext = '.' + source_format

        try:
            if target_format == 'md':
                if ext == '.md':
                    with open(file_path, encoding='utf-8') as f:
                        content = f.read()
                    return {'success': True, 'outputPath': file_path, 'content': content}
                return self.convert_to_markdown(file_path, ext, output_dir)

            if ext == '.md':
                return self.convert_from_markdown(file_path, target_format, output_dir)

            if DirectConverter.can_direct_convert(ext, target_format):
                return DirectConverter.convert(file_path, ext, target_format, output_dir)

            md_result = self.convert_to_markdown(file_path, ext, output_dir)
            if not md_result['success']:
                return md_result

            md_path = md_result['outputPath']
            target_result = self.convert_from_markdown(md_path, target_format, output_dir)
            if not target_result['success']:
                return target_result

            try:
                os.remove(md_path)
            except Exception:
                pass

            return target_result

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

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {'success': True, 'outputPath': output_path, 'content': markdown_content}

    def convert_from_markdown(self, file_path, target_format, output_dir):
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        os.makedirs(output_dir, exist_ok=True)

        if target_format == 'pdf':
            output_path = os.path.join(output_dir, base_name + '.pdf')
            self.markdown_converter.to_pdf(markdown_content, output_path)
        elif target_format == 'docx':
            output_path = os.path.join(output_dir, base_name + '.docx')
            self.markdown_converter.to_docx(markdown_content, output_path)
        elif target_format == 'html':
            output_path = os.path.join(output_dir, base_name + '.html')
            self.markdown_converter.to_html(markdown_content, output_path)
        elif target_format == 'pptx':
            output_path = os.path.join(output_dir, base_name + '.pptx')
            self.markdown_converter.to_pptx(markdown_content, output_path)
        else:
            return {'success': False, 'error': f'不支持的目标格式: {target_format}'}

        return {'success': True, 'outputPath': output_path}


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