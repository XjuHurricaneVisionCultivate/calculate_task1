import os
import random
from PIL import Image, ImageDraw, ImageFont


OPERATORS = ['+', '-', '×', '÷']


def safe_eval(expr: str):
    """
    计算表达式结果
    """
    eval_expr = expr.replace('×', '*').replace('÷', '/')
    return eval(eval_expr)


def build_expression(numbers, operators, generate_paren=False):
    """
    根据数字和运算符构造表达式
    """
    if not generate_paren:
        return f"{numbers[0]} {operators[0]} {numbers[1]} {operators[1]} {numbers[2]} {operators[2]} {numbers[3]} {operators[3]} {numbers[4]}"

    # 生成一对合法括号，括住连续的一段
    start = random.randint(0, 3)
    end = random.randint(start + 1, 4)

    parts = []
    for i in range(5):
        token = str(numbers[i])
        if i == start:
            token = "(" + token
        if i == end:
            token = token + ")"
        parts.append(token)

    expression = parts[0]
    for i in range(4):
        expression += f" {operators[i]} {parts[i + 1]}"

    return expression


def is_valid_expression(expr: str):
    """
    判断表达式是否合法：
    1. 能正常计算
    2. 没有除零
    3. 最终结果是整数
    """
    try:
        result = safe_eval(expr)
        if isinstance(result, float):
            if not result.is_integer():
                return False, None
            result = int(result)
        return True, result
    except ZeroDivisionError:
        return False, None
    except Exception:
        return False, None


def generate_math_expression(generate_paren=False, min_num=1, max_num=20, max_attempts=10000):
    """
    生成一条符合要求的表达式
    """
    for _ in range(max_attempts):
        numbers = [random.randint(min_num, max_num) for _ in range(5)]
        operators = [random.choice(OPERATORS) for _ in range(4)]

        expr = build_expression(numbers, operators, generate_paren=generate_paren)
        valid, result = is_valid_expression(expr)

        if valid:
            return expr, result

    raise RuntimeError("在限定次数内未生成符合条件的表达式，请调整数字范围后重试。")


def load_times_font(size=100):
    """
    加载 Times New Roman 字体
    """
    font_candidates = [
        "times.ttf",
        "Times New Roman.ttf",
        "timesbd.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/times.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
    ]

    for font_path in font_candidates:
        try:
            font = ImageFont.truetype(font_path, size=size)
            print(f"已加载字体: {font_path}")
            return font
        except IOError:
            continue

    print("警告：未找到 Times New Roman 字体，使用默认字体")
    return ImageFont.load_default()


def render_expression_to_image(expression, output_path, font):
    """
    将表达式渲染为图片
    """
    width, height = 1600, 900
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), expression, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), expression, fill="black", font=font)
    image.save(output_path)


def batch_generate_questions(
    count=10,
    output_dir="output_questions",
    generate_paren=False,
    min_num=1,
    max_num=20
):
    """
    批量生成题目并保存
    参数：
        count: 生成数量
        output_dir: 输出文件夹
        generate_paren: 是否带括号
        min_num: 最小数字
        max_num: 最大数字
    """
    os.makedirs(output_dir, exist_ok=True)
    font = load_times_font(size=100)

    answers_path = os.path.join(output_dir, "answers.txt")

    with open(answers_path, "w", encoding="utf-8") as f:
        for i in range(1, count + 1):
            expression, result = generate_math_expression(
                generate_paren=generate_paren,
                min_num=min_num,
                max_num=max_num
            )

            image_path = os.path.join(output_dir, f"{i}.png")
            render_expression_to_image(expression, image_path, font)

            f.write(f"{i}.png\t{expression}\t{result}\n")
            print(f"已生成: {image_path} | 题目: {expression} | 答案: {result}")

    print(f"\n全部生成完成，共 {count} 题")
    print(f"图片保存在: {output_dir}")
    print(f"答案文件保存在: {answers_path}")


def main():
    print("=" * 60)
    print("智力题目批量生成系统")
    print("=" * 60)

    # ===== 可在这里改参数 =====
    count = 5                  # 一次生成多少张
    output_dir = "q"    # 输出文件夹
    generate_paren = True       # True 有括号，False 无括号
    min_num = 0                 # 数字最小值
    max_num = 100                # 数字最大值
    # =========================

    batch_generate_questions(
        count=count,
        output_dir=output_dir,
        generate_paren=generate_paren,
        min_num=min_num,
        max_num=max_num
    )


if __name__ == "__main__":
    main()