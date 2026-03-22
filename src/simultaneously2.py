import os
import cv2
import numpy as np
from pix2text import Pix2Text
from latex2sympy2 import latex2sympy


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    tl, tr, br, bl = rect

    dst_w = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    dst_h = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))

    dst = np.array([
        [0,         0        ],
        [dst_w - 1, 0        ],
        [dst_w - 1, dst_h - 1],
        [0,         dst_h - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (dst_w, dst_h))
    return warped


def find_roi(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0,   0,   200])
    upper_white = np.array([180, 40,  255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None

    largest = max(contours, key=cv2.contourArea)
    peri   = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.04 * peri, True)

    if len(approx) == 4:
        pts = approx.reshape(4, 2).astype("float32")
    else:
        rect = cv2.minAreaRect(largest)
        box  = cv2.boxPoints(rect)
        pts  = box.astype("float32")

    warped = four_point_transform(img, pts)
    return warped, pts


def preprocess_roi(roi_img):
    roi_resized = cv2.resize(roi_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def clean_latex(latex_str):
    import re
    result = latex_str.replace(" ", "")
    latex_spaces = [r"\;", r"\,", r"\:", r"\ ", r"\!", r"\quad", r"\qquad"]
    for space in latex_spaces:
        result = result.replace(space, "")
    result = result.replace("=", "")
    result = result.replace("?", "")
    result = result.replace(r"\cdots", r"-")
    result = result.replace(r"\lfloor", r"-")
    result = result.replace(r"\rfloor", r"-")
    result = result.replace(r"\sb", r"+")
    result = result.replace(r"\div", r"/")
    result = result.replace(r"\+", r"+")
    result = result.replace(r"\-", r"-")
    result = result.replace(r"\,", r"")
    result = re.sub(r'\\1', '1', result)
    result = re.sub(r'\\2', '2', result)
    result = re.sub(r'\\3', '3', result)
    result = re.sub(r'\\4', '4', result)
    result = re.sub(r'\\5', '5', result)
    result = re.sub(r'\\6', '6', result)
    result = re.sub(r'\\7', '7', result)
    result = re.sub(r'\\8', '8', result)
    result = re.sub(r'\\9', '9', result)
    result = re.sub(r'\\0', '0', result)
    result = re.sub(r'\^{\'+\^\{?\\?bullet\}?', '', result)
    result = re.sub(r'\\boxed\{([^}]*)\}', r'\1', result)
    result = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', result)
    result = re.sub(r'\\text(md|bf|it|rm|tt|sf)\{([^}]*)\}', r'\2', result)
    return result


def recognize_and_calculate(img_path, p2t):
    if not os.path.exists(img_path):
        print(f"错误：未找到文件 '{img_path}'")
        return

    img = cv2.imread(img_path)
    if img is None:
        print("错误：图片读取失败")
        return

    roi, pts = find_roi(img)
    if roi is None:
        print("错误：未检测到白色屏幕区域")
        return

    cv2.imwrite("temp_roi.png", roi)

    processed = preprocess_roi(roi)
    cv2.imwrite("temp_pro.png", processed)

    raw_out = p2t.recognize_formula("temp_pro.png")
    clean_out = clean_latex(raw_out)

    print(f"识别结果 LaTeX: {raw_out}")
    print(f"清洗结果 Formula: {clean_out}")

    try:
        res = latex2sympy(clean_out).doit()
        final_val = res.evalf(6) if hasattr(res, 'evalf') else res
        print(f"计算结果 = {final_val}")
    except Exception as e:
        print(f"计算失败：{e}")

    for temp_file in ["temp_roi.png", "temp_pro.png"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == '__main__':
    figure_dir = r"C:\Users\admin\Documents\GitHub\calculate_task1\src\figure"
    p2t = Pix2Text(languages=('en', 'ch_sim'))

    for i in range(1, 43):
        img_name = f"{i:04d}.jpg"
        img_path = os.path.join(figure_dir, img_name)
        print(f"\n{'='*50}")
        print(f"处理图片: {img_name}")
        print('='*50)
        recognize_and_calculate(img_path, p2t)