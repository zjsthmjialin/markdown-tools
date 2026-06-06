import os
import sys
import pytesseract
from PIL import Image
import io


def _find_bundled_tesseract() -> str | None:
    """Locate tesseract.exe bundled alongside this application.
    支持三种部署环境：PyInstaller _MEIPASS 临时目录、frozen 可执行文件旁、开发环境。"""
    candidates = []

    # 0. 显式环境变量（最高优先级）
    env_path = os.environ.get('TESSERACT_PATH')
    if env_path:
        candidates.append(os.path.abspath(env_path))

    # 1. PyInstaller _MEIPASS 临时释放目录（单文件模式）
    if hasattr(sys, '_MEIPASS'):
        candidates.append(os.path.join(sys._MEIPASS, 'tesseract', 'tesseract.exe'))

    # 2. PyInstaller frozen 可执行文件所在目录（生产环境 — extraResources）
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, 'tesseract', 'tesseract.exe'))

    # 3. 相对于本源文件（开发环境）
    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(this_dir, '..', 'tesseract-portable', 'tesseract.exe'))

    for path in candidates:
        normalized = os.path.normpath(os.path.abspath(path))
        if os.path.isfile(normalized):
            return normalized

    return None


def _find_bundled_tessdata(tesseract_exe: str) -> str | None:
    """Find tessdata directory bundled alongside the tesseract executable.
    支持三种部署环境查找 tessdata 语言包目录。"""
    candidates = []

    # 0. 显式环境变量（最高优先级）
    env_tessdata = os.environ.get('TESSDATA_PREFIX')
    if env_tessdata:
        candidates.append(os.path.abspath(env_tessdata))

    # 1. PyInstaller _MEIPASS 临时释放目录
    if hasattr(sys, '_MEIPASS'):
        candidates.append(os.path.join(sys._MEIPASS, 'tesseract', 'tessdata'))

    # 2. tesseract.exe 同级 tessdata/ 目录
    tesseract_dir = os.path.dirname(tesseract_exe)
    candidates.append(os.path.join(tesseract_dir, 'tessdata'))

    # 3. 上级目录中的 tessdata/（如果 tesseract 在子目录中）
    parent_dir = os.path.dirname(tesseract_dir)
    candidates.append(os.path.join(parent_dir, 'tessdata'))

    for path in candidates:
        normalized = os.path.normpath(os.path.abspath(path))
        if os.path.isdir(normalized):
            return normalized

    return None


class TesseractOCR:
    def __init__(self, languages='chi_sim+eng', tesseract_path: str | None = None):
        self.languages = languages

        # Determine tesseract executable path
        exe_path = tesseract_path or _find_bundled_tesseract()
        if exe_path:
            pytesseract.pytesseract.tesseract_cmd = exe_path
            self._tesseract_path = exe_path
        else:
            self._tesseract_path = None
            # Let pytesseract try the system PATH
            if os.name == 'nt':
                default = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'),
                                       'Tesseract-OCR', 'tesseract.exe')
                if os.path.isfile(default):
                    pytesseract.pytesseract.tesseract_cmd = default
                    self._tesseract_path = default

        # Determine tessdata directory
        if self._tesseract_path:
            tessdata_dir = _find_bundled_tessdata(self._tesseract_path)
            if tessdata_dir:
                os.environ['TESSDATA_PREFIX'] = tessdata_dir
                self._tessdata_dir = tessdata_dir
            else:
                self._tessdata_dir = None
        else:
            self._tessdata_dir = None

        # Verify the setup works
        self._available = self._check_availability()

    @property
    def _tesseract_config(self) -> str:
        cfg = '--psm 6'
        return cfg

    def _check_availability(self) -> bool:
        """Verify Tesseract is actually callable."""
        try:
            version = pytesseract.get_tesseract_version()
            print(f"[TesseractOCR] Tesseract {version} ready")
            print(f"[TesseractOCR] Executable: {pytesseract.pytesseract.tesseract_cmd}")
            print(f"[TesseractOCR] Tessdata dir: {self._tessdata_dir or 'default'}")
            # Quick language check: try listing available langs
            import subprocess
            env = os.environ.copy()
            if self._tessdata_dir:
                env['TESSDATA_PREFIX'] = self._tessdata_dir
            result = subprocess.run(
                [pytesseract.pytesseract.tesseract_cmd, '--list-langs'],
                capture_output=True, text=True, env=env, timeout=10
            )
            print(f"[TesseractOCR] Available langs: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"[TesseractOCR] Not available: {e}")
            return False

    @property
    def available(self) -> bool:
        return self._available

    def extract_text_from_image(self, image_data: bytes) -> str:
        image = Image.open(io.BytesIO(image_data))
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.languages,
                config=self._tesseract_config
            )
            return text
        except pytesseract.TesseractError as e:
            # If chi_sim language data is missing, fall back to English only
            if 'chi_sim' in self.languages:
                print(f"[TesseractOCR] Combined languages failed ({e}), retrying with eng only")
                text = pytesseract.image_to_string(
                    image,
                    lang='eng',
                    config=self._tesseract_config
                )
                return text
            raise
