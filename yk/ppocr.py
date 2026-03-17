import os
import re

# 1. 禁用联网检查，提高启动速度
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

def solve_math():
    # --- 配置区域 ---
    IMAGE_PATH = r"k\t1.png"
    # ---------------

    # 2. 初始化 OCR
    # 针对最新版 PaddleX 架构，不传参数是最高兼容模式
    print("正在初始化本地 OCR 模型...")
    try:
        ocr = PaddleOCR() 

    except Exception as e:
        print(f"初始化失败: {e}")
        return

    if not os.path.exists(IMAGE_PATH):
        print(f"错误：在当前目录下找不到文件 {IMAGE_PATH}")
        return
    print("初始化成功！")
    # 3. 执行识别
    print(f"正在识别图片: {IMAGE_PATH}")
    # 注意：新版返回的是一个包含字典的列表
    result = ocr.ocr(IMAGE_PATH)

    if not result:
        print("未检测到文本内容。")
        return

    # 4. 精确解析文字内容（针对你提供的字典结构）
    combined_text = ""
    for res in result:
        # 核心：从字典中提取 'rec_texts' 键对应的列表
        if isinstance(res, dict) and 'rec_texts' in res:
            texts = res['rec_texts']
            # 将所有识别到的行拼接起来
            combined_text += "".join(texts)

    if not combined_text:
        print("解析失败：未能从返回结果中找到文本字段。")
        return

    print(f"OCR 识别内容: {combined_text}")

    # 5. 符号转换（印刷体纠错）
    # 将常见的乘除号变体统一为 Python 可计算的符号
    clean_expr = combined_text.replace('×', '*').replace('x', '*').replace('X', '*')
    clean_expr = clean_expr.replace('÷', '/').replace(':', '/')
    
    # 6. 正则白名单过滤
    # 只保留：数字 0-9，加减乘除 + - * /，括号 ( )，小数点 .
    clean_expr = "".join(re.findall(r'[0-9+\-*/().]', clean_expr))

    print(f"最终待计算算式: {clean_expr}")

    # 7. 自动执行计算
    if not clean_expr:
        print("错误：清洗后未发现有效算式内容。")
        return

    try:
        # 使用 Python 内置 eval 计算结果
        answer = eval(clean_expr)
        
        # 美化输出：如果是整数则去掉 .0 尾缀
        if isinstance(answer, float) and answer.is_integer():
            answer = int(answer)
            
        print("\n" + "="*35)
        print(f" 图片算式: {combined_text}")
        print(f" 提取算式: {clean_expr}")
        print(f" 计算结果: {answer}")
        print("="*35)
    except ZeroDivisionError:
        print("计算失败：除数不能为零。")
    except Exception as e:
        print(f"计算失败：解析算式时出错。错误详情: {e}")

if __name__ == "__main__":
    solve_math()
