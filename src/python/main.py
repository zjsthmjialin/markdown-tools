import sys
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 导入转换器
from converters.pdf_converter import PDFConverter
from converters.docx_converter import DocxConverter
from converters.xlsx_converter import XlsxConverter
from converters.pptx_converter import PptxConverter
from converters.html_converter import HtmlConverter
from markdown.to_document import MarkdownToDocument

class ConversionHandler(BaseHTTPRequestHandler):
    # 转换器实例
    converters = {
        '.pdf': PDFConverter(),
        '.docx': DocxConverter(),
        '.doc': DocxConverter(),
        '.xlsx': XlsxConverter(),
        '.xls': XlsxConverter(),
        '.pptx': PptxConverter(),
        '.ppt': PptxConverter(),
        '.html': HtmlConverter(),
        '.htm': HtmlConverter(),
    }
    markdown_converter = MarkdownToDocument()

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # 处理转换请求
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
        """健康检查端点"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def process_conversion(self, data):
        file_path = data.get('filePath')
        source_format = data.get('sourceFormat', 'auto')
        target_format = data.get('targetFormat', 'md')
        output_dir = data.get('outputDir', os.path.dirname(file_path))

        if not file_path or not os.path.exists(file_path):
            return {'success': False, 'error': f'文件不存在: {file_path}'}

        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()

        # 确定源格式
        if source_format == 'auto':
            if ext in self.converters:
                pass  # 使用文件扩展名确定的格式
            else:
                return {'success': False, 'error': f'不支持的文件格式: {ext}'}
        else:
            # 使用指定的格式
            ext = '.' + source_format

        try:
            # 判断转换方向
            if ext == '.md':
                # Markdown 转换为其他格式
                return self.convert_from_markdown(file_path, target_format, output_dir)
            else:
                # 其他格式转换为 Markdown
                return self.convert_to_markdown(file_path, ext, output_dir)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'转换失败: {str(e)}'}

    def convert_to_markdown(self, file_path, ext, output_dir):
        """将各种格式转换为 Markdown"""
        converter = self.converters.get(ext)
        if not converter:
            return {'success': False, 'error': f'不支持的格式: {ext}'}

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, base_name + '.md')

        # 执行转换
        markdown_content = converter.to_markdown(file_path, output_dir)

        # 提取图片（如果有）
        if hasattr(converter, 'extract_images'):
            image_map = converter.extract_images(file_path, output_dir)
            # 替换 Markdown 中的图片路径
            for old_path, new_name in image_map.items():
                markdown_content = markdown_content.replace(old_path, new_name)

        # 保存 Markdown 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {'success': True, 'outputPath': output_path, 'content': markdown_content}

    def convert_from_markdown(self, file_path, target_format, output_dir):
        """将 Markdown 转换为其他格式"""
        # 读取 Markdown 内容
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # 生成输出文件名
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
        else:
            return {'success': False, 'error': f'不支持的目标格式: {target_format}'}

        return {'success': True, 'outputPath': output_path}


def run_server(port=8765):
    server = HTTPServer(('localhost', port), ConversionHandler)
    print(f'Python conversion service running on port {port}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)