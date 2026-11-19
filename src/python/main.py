import sys
import json
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Event, Lock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters.markitdown_converter import MarkItDownConverter
from converters.pdf_converter import PDFConverter
from utils.image_extractor import ImageExtractor


class ConversionHandler(BaseHTTPRequestHandler):
    state_lock = Lock()
    active_job = None
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
        if self.path == '/cancel':
            with self.state_lock:
                job = self.active_job
                if job:
                    job['cancel'].set()
            return self._send_json({'success': True, 'cancelRequested': bool(job)})
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
        if self.path == '/status':
            with self.state_lock:
                state = self.active_job.copy() if self.active_job else None
            if state:
                state.pop('cancel', None)
            return self._send_json({'status': 'ok', 'job': state})
        ocr_status = 'unknown'
        pdf_converter = self.converters.get('.pdf')
        if pdf_converter and hasattr(pdf_converter, 'ocr') and pdf_converter.ocr:
            ocr_status = 'available' if pdf_converter.ocr.available else 'unavailable'
        elif pdf_converter and pdf_converter.ocr is False:
            ocr_status = 'unavailable'

        return self._send_json({
            'status': 'ok',
            'ocr': ocr_status
        })

    def _send_json(self, payload, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def process_conversion(self, data):
        file_path = data.get('filePath')
        target_format = data.get('targetFormat', 'md')
        source_format = data.get('sourceFormat', 'auto')
        options = data.get('options', {})

        if not file_path or not os.path.exists(file_path):
            return {'success': False, 'error': f'文件不存在: {file_path}'}

        # 只支持转换为 Markdown
        if target_format != 'md':
            return {'success': False, 'error': f'仅支持转换为 Markdown 格式'}

        output_dir = data.get('outputDir') or os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.converters:
            return {'success': False, 'error': f'不支持的文件格式: {ext}'}

        format_groups = {
            'pdf': {'.pdf'}, 'docx': {'.doc', '.docx'}, 'xlsx': {'.xls', '.xlsx'},
            'pptx': {'.ppt', '.pptx'}, 'html': {'.htm', '.html'}, 'txt': {'.txt'}
        }
        if source_format != 'auto' and ext not in format_groups.get(source_format, set()):
            return {'success': False, 'error': f'所选源格式与文件扩展名 {ext} 不匹配'}

        try:
            job = {'file': os.path.basename(file_path), 'page': 0, 'pageCount': 0,
                   'phase': '准备转换', 'cancel': Event()}
            with self.state_lock:
                if self.active_job:
                    return {'success': False, 'error': '已有文件正在转换，请等待或先取消当前任务'}
                self.active_job = job
            def progress(page, page_count, phase):
                with self.state_lock:
                    job.update({'page': page, 'pageCount': page_count, 'phase': phase})
            options.update({'progressCallback': progress, 'isCancelled': job['cancel'].is_set})
            try:
                result = self.convert_to_markdown(file_path, ext, output_dir, options)
                if job['cancel'].is_set():
                    return {'success': False, 'cancelled': True, 'error': '转换已取消'}
                return result
            finally:
                with self.state_lock:
                    if self.active_job is job:
                        self.active_job = None
        except Exception as e:
            if options and options.get('isCancelled', lambda: False)():
                return {'success': False, 'cancelled': True, 'error': '转换已取消'}
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'转换失败: {str(e)}'}

    def convert_to_markdown(self, file_path, ext, output_dir, options=None):
        converter = self.converters.get(ext)
        if not converter:
            return {'success': False, 'error': f'不支持的格式: {ext}'}

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, base_name + '.md')
        suffix = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f'{base_name} ({suffix}).md')
            suffix += 1

        markdown_content = converter.to_markdown(file_path, output_dir, options)
        if options and options.get('isCancelled', lambda: False)():
            return {'success': False, 'cancelled': True, 'error': '转换已取消'}
        if not isinstance(markdown_content, str) or not markdown_content.strip():
            return {'success': False, 'error': '未提取到可用内容，未生成 Markdown 文件'}

        # Extract embedded images from the source document
        image_dir_name = os.path.splitext(os.path.basename(output_path))[0] + '_assets'
        image_output_dir = os.path.join(output_dir, image_dir_name)
        image_map = self._extract_images(file_path, ext, image_output_dir)
        if image_map:
            image_lines = ['\n\n---\n\n## Extracted Images\n']
            for _, saved_filename in image_map.items():
                image_lines.append(f'\n![image]({image_dir_name}/images/{saved_filename})\n')
            markdown_content += ''.join(image_lines)

        try:
            with open(output_path, 'x', encoding='utf-8') as f:
                f.write(markdown_content)
        except FileExistsError:
            suffix += 1
            output_path = os.path.join(output_dir, f'{base_name} ({suffix}).md')
            return self._write_markdown(output_path, markdown_content)

        return {'success': True, 'outputPath': output_path, 'content': markdown_content}

    @staticmethod
    def _write_markdown(output_path, content):
        with open(output_path, 'x', encoding='utf-8') as f:
            f.write(content)
        return {'success': True, 'outputPath': output_path, 'content': content}

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
    server = ThreadingHTTPServer(('127.0.0.1', port), ConversionHandler)
    print(f'Python conversion service running on port {port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)
