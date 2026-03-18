import cv2
import numpy as np

# 读取图片
img = cv2.imread(r"C:\Users\admin\Documents\GitHub\calculate_task1\src\t1.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 定义白色范围（低饱和度、高亮度）
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 30, 255])
mask = cv2.inRange(hsv, lower_white, upper_white)

# 形态学操作去噪
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# 查找轮廓
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # 取面积最大的轮廓
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)


cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()