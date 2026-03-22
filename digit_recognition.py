import rclpy
import cv2
import pytesseract
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class DigitRecognitionNode(Node):
    def __init__(self):
        super().__init__("digitrecognition_node")
        self.bridge = CvBridge()  #创建转换工具，初始化
        self.create_subscription(
            Image,  #消息类型
            "/image_raw",  #订阅的话题
            self.callback,
            10
        )
        self.get_logger().info("数字识别节点已启动")

    def callback(self,msg):
        img = self.bridge.imgmsg_to_cv2(msg,"bgr8")  #ROS2图像转换为OpenCV图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #灰度化
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)  #把灰度图变成纯黑纯白的二值图，大于127变黑，小于127变白
        #实际用的阈值不用，所以用 _ 扔掉

        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-×÷/'
        test = pytesseract.image_to_string(img,lang='eng')  #数字识别用eng
        print(test)

        try:
            print(eval(test.replace('x','*')))
            print(eval(test.replace('÷','/')))
        except:
            pass


def main(args=None):
    rclpy.init(args=args)  #初始化 ROS 2 系统
    rclpy.spin(DigitRecognitionNode())
    rclpy.shutdown()


if __name__ == "__main__":
    main()  