from paddleocr import PaddleOCR
import cv2



ocr=PaddleOCR(
        use_angle_cls=True,
        lang='ch',
        show_log=False
    )

def picture_deal(image):
    result = ocr.ocr(image,cls=True)
    if result and result[0]:
        text = " ".join([line[1][0] for line in result[0]])
        text = text.replace('÷', '/').replace('×', '*')
        
        try:
            result_value = eval(text)
            print(f"计算结果: {text} = {result_value}")
        except Exception as e:
            print(f"计算错误: {e}")
    else:
        print("未识别到文本")


def main():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("image",frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            picture_deal(frame)


    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
