#!/usr/bin/env python3
"""
optimize-clarity.py
调清晰度 - 自适应图像增强处理

功能：
1. 转为灰度（如果是彩色图像）
2. 自适应去噪（保留文字边缘）
3. CLAHE 自适应对比度增强
4. 自适应二值化

用法：
    python scripts/optimize-clarity.py <input_path> <output_path>
    python scripts/optimize-clarity.py <input_path> <output_path> --dpi 300
"""

import sys
import argparse
import cv2
import numpy as np
from PIL import Image
import io


def optimize_clarity(input_path: str, output_path: str, dpi: int = 300) -> dict:
    """
    自适应图像增强，提升扫描件清晰度

    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        dpi: 渲染 DPI，默认 300

    Returns:
        处理结果字典
    """
    try:
        # 读取图像
        img = Image.open(input_path)
        img_array = np.array(img)

        # 1. 转灰度
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # 2. 自适应去噪（保留文字边缘）
        denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

        # 3. CLAHE 自适应对比度增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. 自适应二值化
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )

        # 保存结果
        result = Image.fromarray(binary)
        result.save(output_path)

        return {
            "status": "success",
            "input": input_path,
            "output": output_path,
            "dpi": dpi
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "input": input_path
        }


def main():
    parser = argparse.ArgumentParser(description="调清晰度 - 自适应图像增强")
    parser.add_argument("input_path", help="输入图像路径")
    parser.add_argument("output_path", help="输出图像路径")
    parser.add_argument("--dpi", type=int, default=300, help="渲染 DPI (默认: 300)")

    args = parser.parse_args()
    result = optimize_clarity(args.input_path, args.output_path, args.dpi)

    print(result)
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()