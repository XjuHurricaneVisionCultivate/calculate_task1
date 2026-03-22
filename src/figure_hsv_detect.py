import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class ColorDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HSV/RGB Color Detector")
        self.root.configure(bg="#2b2b2b")
        self.root.geometry("400x150")

        self.image_path = None
        self.img_display = None
        self.orig_image = None
        self.label_img = None

        top_frame = tk.Frame(root, bg="#2b2b2b")
        top_frame.pack(pady=10)

        self.btn_open = tk.Button(
            top_frame, text="Open Image", command=self.open_image,
            bg="#4a4a4a", fg="white", font=("Arial", 12), padx=20, pady=5
        )
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_quit = tk.Button(
            top_frame, text="Quit", command=root.quit,
            bg="#4a4a4a", fg="white", font=("Arial", 12), padx=20, pady=5
        )
        self.btn_quit.pack(side=tk.LEFT, padx=10)

        self.info_frame = tk.Frame(root, bg="#2b2b2b")
        self.info_frame.pack(pady=5)

        self.hsv_label = tk.Label(
            self.info_frame, text="HSV: --", bg="#2b2b2b", fg="#00ff00",
            font=("Consolas", 14), width=30, anchor="w"
        )
        self.hsv_label.pack()

        self.rgb_label = tk.Label(
            self.info_frame, text="RGB: --", bg="#2b2b2b", fg="#00ff00",
            font=("Consolas", 14), width=30, anchor="w"
        )
        self.rgb_label.pack()

        self.canvas = tk.Canvas(root, bg="#1e1e1e", width=800, height=600)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Motion>", self.on_mouse_move)

    def open_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if not self.image_path:
            return

        self.orig_image = cv2.imread(self.image_path)
        if self.orig_image is None:
            return

        image_rgb = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]
        max_size = 800
        scale = min(max_size / w, max_size / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(image_rgb, (new_w, new_h))
        self.scale_x = w / new_w
        self.scale_y = h / new_h

        pil_img = Image.fromarray(resized)
        self.img_display = ImageTk.PhotoImage(pil_img)

        self.canvas.configure(width=new_w, height=new_h)
        self.canvas.delete("all")
        self.label_img = self.canvas.create_image(0, 0, anchor="nw", image=self.img_display)

        self.root.geometry(f"{new_w + 40}x{new_h + 200}")

    def on_mouse_move(self, event):
        if self.orig_image is None:
            return

        x = int(event.x * self.scale_x)
        y = int(event.y * self.scale_y)

        if 0 <= x < self.orig_image.shape[1] and 0 <= y < self.orig_image.shape[0]:
            b, g, r = self.orig_image[y, x]
            r, g, b = int(r), int(g), int(b)

            hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
            h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

            self.hsv_label.configure(text=f"HSV: H={h}, S={s}, V={v}")
            self.rgb_label.configure(text=f"RGB: R={r}, G={g}, B={b}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorDetectorApp(root)
    root.mainloop()