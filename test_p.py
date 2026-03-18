from paddleocr import PaddleOCR
import re

ocr = PaddleOCR(use_angle_cls=True, lang='ch')

def normalize_expr(expr):
    # 替换中文符号为英文符号
    expr = expr.replace('（', '(').replace('）', ')')
    expr = expr.replace('＋', '+').replace('－', '-').replace('＊', '*').replace('／', '/')
    expr = expr.replace('×', '*').replace('÷', '/')
    expr = expr.replace(' ', '').replace('\n', '')
    return expr

def extract_expression(image_path):#提取表达式
    result = ocr.ocr(image_path, cls=False)#使用ocr识别
    texts = []#提取识别到的所有文本行
    for line in result:
        for w in line:
            texts.append(w[1][0])#w[1][0]是文本内容,把每次识别到的文本加到test列表末尾
    print("所有识别结果：", texts)
    merged = ''.join(texts)#将所有的文本合成为一个字符串
    merged = normalize_expr(merged)#调用函数，优化表达式
    print("合并规范化后：", merged)
    expr_pattern = re.compile(r'^[\d+\-*/()]+$')#只包含数字，加减乘除和括号
    if expr_pattern.match(merged):#检查整个字符串
        return merged
    for t in texts:
        norm_t = normalize_expr(t)#检查每个单独的文本行，看看是否有符合条件的表达式
        if expr_pattern.match(norm_t):
            return norm_t
    return None#没有找到合格的表达式

def calc_expression(expr):#计算表达式
    if not re.fullmatch(r'^[\d+\-*/()]+$', expr):#^：字符串开始，+：一个或多个上述字符，$：字符串结束
        return "表达式不安全，拒绝计算"
    try:
        return eval(expr)
    except Exception as e:
        return "表达式解析失败：" + str(e)#将异常对象e转换为字符串，然后拼接到错误消息中

if __name__ == "__main__":
    image_path = '20260315-205223.png'
    expr = extract_expression(image_path)
    if expr:
        print(f"识别到表达式: {expr}")
        result = calc_expression(expr)
        print(f"计算结果: {result}")
    else:
        print("未找到符合格式的表达式")