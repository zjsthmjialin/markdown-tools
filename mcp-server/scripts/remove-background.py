#!/usr/bin/env python3
"""
remove-background.py
去底色 - 去除文档背景颜色

功能：
1. 自动检测背景色（通过边缘采样或直方图分析）
2. 生成背景掩码
3. 背景去除 + 文字增强
4. 自适应阈值处理

用法：
    python scripts/remove-background.py <input_path> <output_path>
    python scripts/remove-background.py <input_path> <output_path> --threshold 15
"""

import sys
import argparse
import cv2
import numpy as np
from PIL import Image


def detect_background_color(img_array: np.ndarray) -> tuple[int, int, int]:
    """
    自动检测背景色
    通过分析图像四角和边缘区域，取最常见的颜色
    """
    h, w = img_array.shape[:2]
    margin = 5

    # 采集四个角的区域
    corners = [
        img_array[:margin, :margin],           # 左上
        img_array[:margin, -margin:],         # 右上
        img_array[-margin:, :margin],         # 左下
        img_array[-margin:, -margin:],        # 右下
    ]

    # 合并所有角落像素
    corner_pixels = np.vstack([c.reshape(-1, c.shape[-1]) for c in corners])

    # 简化处理：取 BGR 平均值作为背景色
    return tuple(int(x) for x in np.mean(corner_pixels, axis=0))


def remove_background(input_path: str, output_path: str, threshold: int = 15) -> dict:
    """
    去除图像背景颜色

    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        threshold: 背景检测阈值（颜色距离小于此值被认为是背景）

    Returns:
        处理结果字典
    """
    try:
        # 读取图像
        img = Image.open(input_path)
        img_array = np.array(img)

        # 保持原始通道数以检测背景色
        if len(img_array.shape) == 3:
            # 检测背景色
            bg_color = detect_background_color(img_array)

            # 转为灰度进行进一步处理
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # 创建一个掩码：背景区域为白色，文字区域为黑色
            mask = np.ones(gray.shape, dtype=np.uint8) * 255

            # 对每个通道检查背景距离
            for c in range(3):
                channel = img_array[:, :, c]
                diff = np.abs(channel.astype(int) - bg_color[c])
                # 创建该通道的背景掩码
                bg_mask_c = (diff < threshold).astype(np.uint8) * 255
                mask = cv2.bitwise_and(mask, bg_mask_c)

            # 确保文字区域不被标记为背景
            # 使用形态学操作清理掩码
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # 反转掩码：文字区域为白色
            mask_inv = cv2.bitwise_not(mask)

            # 对灰度图应用掩码
            result = cv2.bitwise_and(gray, gray, mask=mask_inv)

            # 轻微锐化增强文字
            kernel_sharpen = np.array([[-1, -1, -1],
                                       [-1,  9, -1],
                                       [-1, -1, -1]])
            result = cv2.filter2D(result, -1, kernel_sharpen)

        else:
            # 已经是灰度图
            gray = img_array
            # 自适应二值化处理
            result = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                blockSize=11,
                C=2
            )

        # 保存结果
        Image.fromarray(result).save(output_path)

        return {
            "status": "success",
            "input": input_path,
            "output": output_path,
            "threshold": threshold
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "input": input_path
        }


def main():
    parser = argparse.ArgumentParser(description="去底色 - 去除文档背景颜色")
    parser.add_argument("input_path", help="输入图像路径")
    parser.add_argument("output_path", help="输出图像路径")
    parser.add_argument("--threshold", type=int, default=15, help="背景检测阈值 (默认: 15)")

    args = parser.parse_args()
    result = remove_background(args.input_path, args.output_path, args.threshold)

    print(result)
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()