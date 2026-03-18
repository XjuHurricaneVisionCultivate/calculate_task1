import cv2
import numpy as np


def order_points(pts):
    """将4个顶点按 左上、右上、右下、左下 排序"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]     # 左上：x+y 最小
    rect[2] = pts[np.argmax(s)]     # 右下：x+y 最大
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # 右上：y-x 最小
    rect[3] = pts[np.argmax(diff)]  # 左下：y-x 最大
    return rect


def four_point_transform(image, pts):
    """透视变换，将检测到的四边形区域摆正"""
    rect = order_points(pts)
    tl, tr, br, bl = rect

    # 计算目标宽高
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


# 读取图片
img = cv2.imread(r"C:\Users\admin\Documents\GitHub\calculate_task1\src\t4.png")
if img is None:
    raise FileNotFoundError("无法读取图片，请检查路径")

# ---------- 1. 提取白色区域 ----------
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower_white = np.array([0,   0,   200])
upper_white = np.array([180, 30,  255])
mask = cv2.inRange(hsv, lower_white, upper_white)

# ---------- 2. 形态学去噪 ----------
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)

# ---------- 3. 找轮廓，取最大面积 ----------
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    largest = max(contours, key=cv2.contourArea)

    # ---------- 4. 多边形拟合逼近四边形 ----------
    peri   = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.04 * peri, True)

    result_img = img.copy()

    if len(approx) == 4:
        pts = approx.reshape(4, 2).astype("float32")
        print("检测到四边形，执行透视变换")
    else:
        # 拟合顶点不是4个，退回 minAreaRect
        print(f"拟合顶点数={len(approx)}，退回使用 minAreaRect")
        rect = cv2.minAreaRect(largest)
        box  = cv2.boxPoints(rect)
        pts  = box.astype("float32")

    # ---------- 5. 原图绘制绿色框 ----------
    ordered  = order_points(pts)
    box_draw = np.intp(ordered)
    cv2.drawContours(result_img, [box_draw], 0, (0, 255, 0), 3)

    # ---------- 6. 透视变换摆正屏幕 ----------
    warped = four_point_transform(img, pts)

    # ---------- 7. 保存与显示 ----------
    cv2.imwrite("result_boxed.png",  result_img)
    cv2.imwrite("result_warped.png", warped)
    print("已保存: result_boxed.png  /  result_warped.png")

    cv2.imshow("Original with Box", result_img)
    cv2.imshow("Warped Screen",     warped)
else:
    print("未检测到白色屏幕区域")
    cv2.imshow("Result", img)

cv2.waitKey(0)
cv2.destroyAllWindows()