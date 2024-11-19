#!/usr/bin/python
# coding=utf-8
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageSplitter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图片分割工具")
        self.root.geometry("800x600")

        # 图片显示区域
        self.canvas = tk.Canvas(self.root, bg='white')
        self.canvas.pack(expand=True, fill='both', padx=10, pady=10)

        # 控制区域
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="行数:").pack(side=tk.LEFT, padx=5)
        self.rows_var = tk.StringVar(value="2")
        self.rows_entry = tk.Entry(control_frame, textvariable=self.rows_var, width=5)
        self.rows_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="列数:").pack(side=tk.LEFT, padx=5)
        self.cols_var = tk.StringVar(value="2")
        self.cols_entry = tk.Entry(control_frame, textvariable=self.cols_var, width=5)
        self.cols_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="选择图片", command=self.select_image).pack(side=tk.LEFT, padx=20)
        tk.Button(control_frame, text="分割图片", command=self.split_image).pack(side=tk.LEFT)

        self.image_path = None
        self.image = None
        self.photo = None

        # 绑定输入变化事件
        self.rows_var.trace('w', self.draw_grid)
        self.cols_var.trace('w', self.draw_grid)

        self.root.mainloop()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.image_path = file_path
            self.load_image()

    def load_image(self):
        if self.image_path:
            # 加载并调整图片大小以适应画布
            image = Image.open(self.image_path)
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 计算缩放比例
            ratio = min(canvas_width/image.width, canvas_height/image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)

            self.image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)

            # 显示图片
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.photo, anchor='center')
            self.draw_grid()

    def draw_grid(self, *args):
        if not self.image:
            return

        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
        except ValueError:
            return

        # 清除原有的网格线
        self.canvas.delete("grid")

        # 获取图片在画布上的位置
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width = self.photo.width()
        img_height = self.photo.height()
        x_start = (canvas_width - img_width) / 2
        y_start = (canvas_height - img_height) / 2

        # 绘制垂直线
        for i in range(1, cols):
            x = x_start + (img_width * i / cols)
            self.canvas.create_line(x, y_start, x, y_start + img_height, fill="red", tags="grid")

        # 绘制水平线
        for i in range(1, rows):
            y = y_start + (img_height * i / rows)
            self.canvas.create_line(x_start, y, x_start + img_width, y, fill="red", tags="grid")

    def split_image(self):
        if not self.image_path:
            messagebox.showwarning("警告", "请先选择图片")
            return

        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
        except ValueError:
            messagebox.showerror("错误", "行数和列数必须是有效的数字")
            return

        # 加载原始图片
        img = Image.open(self.image_path)
        width = img.width
        height = img.height

        # 创建保存目录
        save_dir = os.path.join(os.path.dirname(self.image_path), "split_results")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 计算每个小块的大小
        piece_width = width // cols
        piece_height = height // rows

        # 分割图片
        for i in range(rows):
            for j in range(cols):
                left = j * piece_width
                top = i * piece_height
                right = left + piece_width
                bottom = top + piece_height

                piece = img.crop((left, top, right, bottom))
                piece.save(os.path.join(save_dir, f"piece_{i+1}_{j+1}.png"))

        messagebox.showinfo("成功", f"图片已分割完成，保存在: {save_dir}")

if __name__ == "__main__":
    ImageSplitter()
