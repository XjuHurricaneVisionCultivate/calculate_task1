import os
import cv2
from pix2text import Pix2Text
from latex2sympy2 import latex2sympy

def preprocess_image(img_path):
    """预处理：放大并二值化，强化特征"""
    img = cv2.imread(img_path)
    if img is None:
        return None
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    temp_path = "temp_pro.png"
    cv2.imwrite(temp_path, binary)
    return temp_path

def clean_latex(latex_str):
    """清洗：剔除空格，修正潜在错误"""
    return latex_str.replace(" ", "")

def process_and_solve(p2t, img_path):
    """核心逻辑：识别 -> 清洗 -> 计算"""
    if not os.path.exists(img_path):
        print(f"❌ 错误：未找到文件 '{img_path}'")
        return

    # 1. 预处理
    proc_img = preprocess_image(img_path)
    if not proc_img:
        print("❌ 错误：图片读取失败")
        return

    # 2. OCR 识别
    raw_out = p2t.recognize_formula(proc_img)
    clean_out = clean_latex(raw_out)
    print(f"\n[识别结果] LaTeX: {raw_out}")
    print(f"[清洗结果] Formula: {clean_out}")

    # 3. 计算
    try:
        res = latex2sympy(clean_out).doit()
        # 格式化输出
        final_val = res.evalf(6) if hasattr(res, 'evalf') else res
        print(f"✅ 计算成功！ 结果 = {final_val}")
    except Exception as e:
        print(f"⚠️ 计算失败：解析器无法处理此公式。报错信息: {e}")

    # 清理临时文件
    if os.path.exists(proc_img):
        os.remove(proc_img)

def main():
    print("--- 正在初始化 OCR 模型，请稍候... ---")
    # 只初始化一次，驻留内存提供快速响应
    try:
        p2t = Pix2Text(languages=('en', 'ch_sim'))
        print("--- ✅ 初始化完成！程序已就绪 ---")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    default_img = 'detect.png'

    while True:
        print("\n" + "="*40)
        user_input = input(f"请输入图片路径 (直接回车默认读取 {default_img}, 输入 'q' 退出): ").strip()

        if user_input.lower() == 'q':
            print("程序已退出。")
            break
        
        target_img = user_input if user_input else default_img
        
        print(f"正在处理: {target_img} ...")
        process_and_solve(p2t, target_img)

if __name__ == '__main__':
    main()
