'''
pip install pytesseract opencv-python pillow
# Linux（机器人常见系统）
sudo apt install tesseract-ocr
'''


import cv2
import re
import numpy as np
import pytesseract
from PIL import Image
def preprocess_image(image_path: str) -> Image.Image:
    """
    针对算式优化的图像预处理
    放大 + 锐化 + 二值化，重点提升 ÷ 等符号的识别
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 放大 2 倍，防止小图符号粘连
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # 锐化，突出 ÷ 上下两点与横线
    kernel = np.array([[0, -1, 0],
                       [-1,  5, -1],
                       [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)
    # OTSU 自动二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(binary)
def extract_expression(image_path: str) -> str:
    """
    Tesseract OCR 识别，使用白名单限定字符集
    只允许出现数字和运算符，大幅减少误识别
    """
    img = preprocess_image(image_path)
    # 关键配置：
    # --oem 1  使用 LSTM 引擎（更准）
    # --psm 7  单行文本模式（算式通常一行）
    # whitelist 限定只识别这些字符
    config = (
        '--oem 1 --psm 7 '
        '-c tessedit_char_whitelist=0123456789+-×÷*/'
    )
    text = pytesseract.image_to_string(img, config=config)
    return text.strip()
def clean_expression(raw: str) -> str:
    """清洗并统一运算符"""
    expr = raw.replace('×', '*').replace('x', '*').replace('X', '*')
    expr = expr.replace('÷', '/').replace('=', '')
    # 过滤所有非法字符
    expr = re.sub(r'[^0-9+\-*/().\s]', '', expr).strip()
    return expr
def safe_evaluate(expr: str):
    """白名单校验后安全计算"""
    if not re.fullmatch(r'[\d+\-*/().\s]+', expr):
        raise ValueError(f"非法算式：{expr}")
    result = eval(expr)
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result
def solve(image_path: str):
    raw = extract_expression(image_path)
    print(f"OCR 识别：{raw}")
    expr = clean_expression(raw)
    print(f"清洗结果：{expr}")
    if not expr:
        print("未识别到有效算式")
        return
    answer = safe_evaluate(expr)
    print(f"算式：{expr} = {answer}")
if __name__ == "__main__":
    solve("detect.png")