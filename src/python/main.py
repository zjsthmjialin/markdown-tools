import sys
import json
import os
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters.markitdown_converter import MarkItDownConverter
from converters.pdf_converter import PDFConverter
from utils.image_extractor import ImageExtractor


# 只支持正向转换：文档 -> Markdown
CONVERTERS = {
    '.pdf': PDFConverter(),
    '.docx': MarkItDownConverter(),
    '.doc': MarkItDownConverter(),
    '.xlsx': MarkItDownConverter(),
    '.xls': MarkItDownConverter(),
    '.pptx': MarkItDownConverter(),
    '.ppt': MarkItDownConverter(),
    '.html': MarkItDownConverter(),
    '.htm': MarkItDownConverter(),
    '.txt': MarkItDownConverter(),
}


def process_conversion(data):
    file_path = data.get('filePath')
    target_format = data.get('targetFormat', 'md')

    if not file_path or not os.path.exists(file_path):
        return {'success': False, 'error': f'文件不存在: {file_path}'}

    if target_format != 'md':
        return {'success': False, 'error': '仅支持转换为 Markdown 格式'}

    output_dir = data.get('outputDir') or os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in CONVERTERS and ext != '.md':
        return {'success': False, 'error': f'不支持的文件格式: {ext}'}

    try:
        return convert_to_markdown(file_path, ext, output_dir)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f'转换失败: {str(e)}'}


def convert_to_markdown(file_path, ext, output_dir):
    converter = CONVERTERS.get(ext)
    if not converter:
        return {'success': False, 'error': f'不支持的格式: {ext}'}

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, base_name + '.md')

    markdown_content = converter.to_markdown(file_path, output_dir)

    image_map = _extract_images(file_path, ext, output_dir)
    if image_map:
        image_lines = ['\n\n---\n\n## Extracted Images\n']
        for _, saved_filename in image_map.items():
            image_lines.append(f'\n![image](images/{saved_filename})\n')
        markdown_content += ''.join(image_lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return {'success': True, 'outputPath': output_path, 'content': markdown_content}


def _extract_images(file_path, ext, output_dir):
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


def parse_http_request(data):
    """Parse raw HTTP request, return (method, path, body)."""
    lines = data.split(b'\r\n')
    if not lines:
        return None, None, None
    request_line = lines[0].decode('utf-8', errors='replace')
    parts = request_line.split(' ')
    if len(parts) < 2:
        return None, None, None
    method = parts[0].upper()

    # Parse headers
    headers = {}
    body_start = data.index(b'\r\n\r\n') + 4 if b'\r\n\r\n' in data else len(data)
    for line in lines[1:]:
        if not line:
            break
        try:
            line_str = line.decode('utf-8', errors='replace')
            if ':' in line_str:
                key, val = line_str.split(':', 1)
                headers[key.strip().lower()] = val.strip()
        except Exception:
            continue

    body = data[body_start:]
    return method, parts[1], body, headers


def build_http_response(status_code, body_json, status_text='OK'):
    """Build HTTP response with JSON body."""
    body = json.dumps(body_json, ensure_ascii=False).encode('utf-8')
    return b'HTTP/1.1 %d %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\nConnection: close\r\n\r\n%s' % (
        status_code, status_text.encode(), len(body), body
    )


def handle_request(data):
    """Handle a single HTTP request, return response bytes."""
    result = parse_http_request(data)
    if result[0] is None:
        return build_http_response(400, {'success': False, 'error': 'Bad request'}, 'Bad Request')

    method, path, body, headers = result

    if method == 'GET':
        return build_http_response(200, {'status': 'ok'})

    if method == 'POST':
        try:
            request_data = json.loads(body.decode('utf-8'))
            response = process_conversion(request_data)
            status = 200 if response.get('success') else 500
            return build_http_response(status, response, 'OK' if status == 200 else 'Internal Server Error')
        except json.JSONDecodeError:
            return build_http_response(400, {'success': False, 'error': 'Invalid JSON'}, 'Bad Request')
        except Exception:
            import traceback
            traceback.print_exc()
            return build_http_response(500, {'success': False, 'error': 'Internal server error'}, 'Internal Server Error')

    return build_http_response(405, {'success': False, 'error': 'Method not allowed'}, 'Method Not Allowed')


class SimpleHTTPServer:
    """Minimal single-threaded HTTP server using raw sockets.

    Avoids http.server / socketserver modules which have a PyInstaller
    compatibility issue on Python 3.14.
    """

    def __init__(self, host='127.0.0.1', port=8765):
        self._host = host
        self._port = port
        self._sock = None

    def serve_forever(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))
        self._sock.listen(5)
        print(f'Python conversion service running on port {self._port}', flush=True)

        try:
            while True:
                conn, addr = self._sock.accept()
                try:
                    conn.settimeout(30)
                    data = b''
                    while True:
                        chunk = conn.recv(65536)
                        if not chunk:
                            break
                        data += chunk
                        if b'\r\n\r\n' in data:
                            # Check Content-Length to decide if we need more data
                            # For simplicity, assume the body is already received
                            # (small JSON requests fit in one recv)
                            if len(data) > 4096:
                                # If too large, try to get Content-Length
                                break
                            # Give a small window for more data
                            conn.settimeout(0.1)
                            try:
                                more = conn.recv(65536)
                                if more:
                                    data += more
                            except socket.timeout:
                                pass
                            break
                    if data:
                        response = handle_request(data)
                        conn.sendall(response)
                except Exception:
                    import traceback
                    traceback.print_exc()
                finally:
                    conn.close()
        finally:
            self._sock.close()


def run_server(port=8765):
    server = SimpleHTTPServer('127.0.0.1', port)
    server.serve_forever()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)
