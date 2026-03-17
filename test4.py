import re
from paddleocr import PaddleOCR
from PIL import Image, ImageOps
import numpy as np

def recognize_and_calculate(image_path):
    img = Image.open(image_path)  # 直接读取，兼容中文路径

    width = 700
    height = int(img.height * (width / img.width))
    img_resized = img.resize((width, height), Image.LANCZOS)
    ocr = PaddleOCR(use_textline_orientation=True, lang='ch', log_level=0)

    result = ocr.ocr(np.array(img), cls=False)

    # 提取文本（兼容不同格式）
    text_parts = []
    if result and len(result) > 0 and result[0]:
        for line in result[0]:
            if isinstance(line, list) and len(line) >= 2:
                text = line[1][0] if isinstance(line[1], (list, tuple)) else line[1]
            elif isinstance(line, tuple) and len(line) >= 2:
                text = line[0]
            else:
                continue
            text_parts.append(text)

    raw_expr = ''.join(text_parts).replace(' ', '').replace('\n', '')
    print(f"[调试] 识别到的原始文本: {raw_expr}")

    if not raw_expr:
        print("未识别到任何文本")
        return None

    # 标准化：替换常见符号
    expr = raw_expr.replace('×', '*').replace('÷', '/')
    expr = expr.replace('x', '*').replace('X', '*')
    expr = expr.replace(':', '/')   # 关键修复：冒号 → 除号
    expr = re.sub(r'[^0-9+\-*/()]', '', expr)
    print(f"[调试] 标准化后的表达式: {expr}")

    # 验证合法性
    if not re.match(r'^[0-9+\-*/()]+$', expr):
        print("表达式包含非法字符，无法计算")
        return None

    try:
        result = eval(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result
    except Exception as e:
        print(f"计算错误: {e}")
        return None

if __name__ == "__main__":
    image_path = "/home/zxy/weektest/1/q/3.png"  # 请确认路径正确
    result = recognize_and_calculate(image_path)
    if result is not None:
        print(result)
    else:
        print("无法识别或计算")