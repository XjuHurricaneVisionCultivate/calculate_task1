import cv2
import numpy as np
import os

# 强制切换到脚本所在目录
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)
print(f"✅ 当前工作目录：{os.getcwd()}")

#               1. 加载数字+符号模板 
def load_templates():
    templates = {}
    # 1. 加载数字模板（0~9）
    for digit in range(10):
        template_path = f"{digit}.png"
        if os.path.exists(template_path):
            template = cv2.imread(template_path, 0)
            if template is not None:
                template = cv2.threshold(template, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                templates[str(digit)] = template  # 数字存为字符串，方便拼接
    
    # 2. 加载符号模板（新增！和数字模板逻辑一致）,映射字典 symbol_map，把运算符号和对应的模板文件名关联起来
    symbol_map = {
        "+": "jia.png",
        "-": "jian.png",
        "×": "cheng.png",
        "÷": "chu.png"
    }
    for symbol, filename in symbol_map.items():
        if os.path.exists(filename):
            template = cv2.imread(filename, 0)#参数 0 代表灰度模式
            if template is not None:
                template = cv2.threshold(template, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                """cv2.THRESH_BINARY_INV：反二值化（亮区域→0，暗区域→255）。
                   cv2.THRESH_OTSU：自动计算最佳阈值，不用手动指定。
                   [1]：取函数返回的第二个值，即处理后的二值图像。
               """
                templates[symbol] = template#把处理好的二值符号模板存入 templates 字典，键是符号本身
                
    
    return templates

# 2.统一识别数字/符号 ,用模板识别匹配待检测的图
def recognize_char(img_gray, templates):
    """替代原来的recognize_single_digit，既能识别数字也能识别符号"""
    max_score = 0
    best_char = ""  # 不再返回数字，返回字符（数字/符号）
    for char, template in templates.items():
        # 缩放模板到待识别区域大小
        resized_template = cv2.resize(template, (img_gray.shape[1], img_gray.shape[0]))
        """把模板图像缩放到和待识别区域 img_gray 完全一样的尺寸：
           img_gray.shape[0]：待识别图的高度,img_gray.shape[1]：待识别图的宽度
        """
        res = cv2.matchTemplate(img_gray, resized_template, cv2.TM_CCOEFF_NORMED)#用 TM_CCOEFF_NORMED 方法计算匹配度
        score = np.max(res)#从匹配结果矩阵 res 中取出最大值
        
        if score > max_score:
            max_score = score
            best_char = char

    return best_char if max_score > 0.2 else "", max_score

# 3. 删掉像素识别符号的逻辑 
def split_and_recognize_expr_simple(img_path, templates):
    img = cv2.imread(img_path)
    if img is None:
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU )[1]

    expr_chars = []
    char_width = 20  # 可根据你的图片调整
    for i in range(0, binary.shape[1], char_width):
        char_region = binary[:, i:i+char_width]#:：表示取所有行（从图片顶部到底部）,i:i+char_width：表示取从第 i 列到第 i+35 列的所有列
        if np.sum(char_region) < 10:  # 空白区域跳过
            continue
        # 缩放到模板尺寸
        char_img = cv2.resize(char_region, (27, 27))
        # 调用统一的字符识别函数（替代原来的recognize_single_digit）
        char, score = recognize_char(char_img, templates)
        if char and score > 0.1:  # 只要识别到有效字符就拼接
            expr_chars.append(char)#如果识别成功，就把字符添加到列表 expr_chars 中
    
    return "".join(expr_chars)

# 计算表达式（不变）
def calculate_expr(expr):
    if not expr:
        return "识别失败"
    try:
        safe_expr = expr.replace("×", "*").replace("÷", "/")
        return eval(safe_expr)
    except:
        return "计算错误"

# 主函数（不变）
if __name__ == "__main__":
    templates = load_templates()
    if not templates:
        print(" 模板加载失败（检查0.png~9.png和符号模板）")
        exit()

    expr = split_and_recognize_expr_simple("test2_photo.png", templates)
    print(f" 识别到的表达式：{expr}")
    print(f" 计算结果：{calculate_expr(expr)}")