import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageTk import PhotoImage
from tkinter import filedialog, ttk, colorchooser
import os
from tkinter import font

class TextToImage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文字转图片工具")
        self.root.geometry("1920x1080")

        # 保存当前生成的图片和颜色设置
        self.current_image = None
        self.bg_color = (255, 255, 240)  # 默认背景色
        self.text_color = (255, 0, 0)  # 默认文字颜色
        self.outline_color = (0, 0, 255)  # 默认描边颜色

        # 文字位置
        self.text_x = None
        self.text_y = None
        self.dragging = False

        # 保存最终要输出的图片
        self.output_image = None

        # 颜色选择框架
        self.color_frame = tk.Frame(self.root)
        self.color_frame.pack(pady=5)

        # 背景色选择按钮
        self.bg_color_btn = tk.Button(self.color_frame, text="选择背景色", command=self.choose_bg_color, font=('SimHei', 12))
        self.bg_color_btn.pack(side=tk.LEFT, padx=5)

        # 文字颜色选择按钮
        self.text_color_btn = tk.Button(self.color_frame, text="选择文字颜色", command=self.choose_text_color, font=('SimHei', 12))
        self.text_color_btn.pack(side=tk.LEFT, padx=5)

        # 描边颜色选择按钮
        self.outline_color_btn = tk.Button(self.color_frame, text="选择描边颜色", command=self.choose_outline_color, font=('SimHei', 12))
        self.outline_color_btn.pack(side=tk.LEFT, padx=5)

        # 字体选择框
        self.font_frame = tk.Frame(self.root)
        self.font_frame.pack(pady=5)

        self.font_label = tk.Label(self.font_frame, text="选择字体:", font=('SimHei', 12))
        self.font_label.pack(side=tk.LEFT, padx=5)

        # 获取系统字体列表
        self.font_list = [f for f in font.families() if not f.startswith('@')]
        self.font_var = tk.StringVar(value='SimHei')  # 确保默认字体支持中文
        self.font_combo = ttk.Combobox(self.font_frame, textvariable=self.font_var, values=self.font_list, width=20)
        self.font_combo.pack(side=tk.LEFT, padx=5)

        # 字体大小选择
        self.size_label = tk.Label(self.font_frame, text="字体大小:", font=('SimHei', 12))
        self.size_label.pack(side=tk.LEFT, padx=5)

        self.size_var = tk.StringVar(value='40')
        self.size_combo = ttk.Combobox(self.font_frame, textvariable=self.size_var, values=[str(i) for i in range(12, 73, 4)], width=5)
        self.size_combo.pack(side=tk.LEFT, padx=5)

        # 文本输入框
        self.text_label = tk.Label(self.root, text="请输入要转换的文字:", font=('SimHei', 12))
        self.text_label.pack(pady=10)

        self.text_input = tk.Text(self.root, height=5, width=50, font=('SimHei', 12))
        self.text_input.pack(pady=10)

        # 转换按钮
        self.convert_btn = tk.Button(self.root, text="生成图片", command=self.convert_text_to_image, font=('SimHei', 12))
        self.convert_btn.pack(pady=10)

        # 保存按钮
        self.save_btn = tk.Button(self.root, text="保存图片", command=self.save_image, font=('SimHei', 12), state=tk.DISABLED)
        self.save_btn.pack(pady=10)

        # 图片显示区域
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

        # 绑定鼠标事件
        self.image_label.bind('<Button-1>', self.start_drag)
        self.image_label.bind('<B1-Motion>', self.drag)
        self.image_label.bind('<ButtonRelease-1>', self.stop_drag)

        # 绑定字体和大小变化事件
        self.font_combo.bind('<<ComboboxSelected>>', lambda e: self.convert_text_to_image())
        self.size_combo.bind('<<ComboboxSelected>>', lambda e: self.convert_text_to_image())

        self.root.mainloop()

    def start_drag(self, event):
        self.dragging = True
        self.text_x = event.x
        self.text_y = event.y

    def drag(self, event):
        if self.dragging:
            self.text_x = event.x
            self.text_y = event.y
            self.update_image()

    def stop_drag(self, event):
        self.dragging = False

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="选择背景颜色", color=self.rgb_to_hex(self.bg_color))
        if color[0]:
            self.bg_color = tuple(map(int, color[0]))
            self.convert_text_to_image()

    def choose_text_color(self):
        color = colorchooser.askcolor(title="选择文字颜色", color=self.rgb_to_hex(self.text_color))
        if color[0]:
            self.text_color = tuple(map(int, color[0]))
            self.convert_text_to_image()

    def choose_outline_color(self):
        color = colorchooser.askcolor(title="选择描边颜色", color=self.rgb_to_hex(self.outline_color))
        if color[0]:
            self.outline_color = tuple(map(int, color[0]))
            self.convert_text_to_image()

    def rgb_to_hex(self, rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def save_image(self):
        if self.output_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
            )
            if file_path:
                self.output_image.save(file_path)

    def convert_text_to_image(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            return

        # 创建背景图片
        width = 600
        height = 400
        image = Image.new('RGB', (width, height), self.bg_color)

        # 初始化文字位置为中心
        if self.text_x is None:
            self.text_x = width // 2
            self.text_y = height // 2

        self.current_image = image
        self.update_image()

    def update_image(self):
        if not self.current_image:
            return

        # 复制原始背景图片
        image = self.current_image.copy()
        draw = ImageDraw.Draw(image)
        text = self.text_input.get("1.0", tk.END).strip()

        # 设置字体
        try:
            font_size = int(self.size_var.get())
            selected_font = self.font_var.get()
            font_path = self.get_font_path(selected_font)
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except Exception as e:
            print(f"字体加载失败: {e}")
            font = ImageFont.load_default()

        # 计算文字边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 如果文字宽度超过图片宽度，进行自动折行处理
        if text_width > image.width - 40:  # 留出40像素的边距
            words = text
            lines = []
            current_line = ""

            for char in words:
                test_line = current_line + char
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = test_bbox[2] - test_bbox[0]

                if test_width <= image.width - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char

            if current_line:
                lines.append(current_line)

            # 重新计算总高度
            total_height = len(lines) * text_height
            y = self.text_y - total_height // 2

            # 绘制每一行文字
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                x = self.text_x - line_width // 2

                # 绘制描边
                for offset in range(-2, 3):
                    for offset2 in range(-2, 3):
                        draw.text((x + offset, y + offset2), line, font=font, fill=self.outline_color)

                # 绘制文字
                draw.text((x, y), line, font=font, fill=self.text_color)
                y += text_height
        else:
            # 计算文字位置，使文字中心点对齐鼠标位置
            x = self.text_x - text_width // 2
            y = self.text_y - text_height // 2

            # 绘制描边
            for offset in range(-2, 3):
                for offset2 in range(-2, 3):
                    draw.text((x + offset, y + offset2), text, font=font, fill=self.outline_color)

            # 绘制文字
            draw.text((x, y), text, font=font, fill=self.text_color)

        # 在界面上显示图片
        photo = PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # 保持引用防止被垃圾回收

        # 保存当前图片用于导出
        self.output_image = image

        # 启用保存按钮
        self.save_btn.config(state=tk.NORMAL)

    def get_font_path(self, font_name):
        """
        根据字体名称获取字体文件的路径。
        """
        from pathlib import Path
        import sys

        if sys.platform == "win32":
            font_dir = Path("C:/Windows/Fonts")
        elif sys.platform == "darwin":
            font_dir = Path("/Library/Fonts")
        else:
            font_dir = Path("/usr/share/fonts")

        # 常见中文字体文件映射
        font_mapping = {
            "SimHei": "simhei.ttf",
            "Microsoft YaHei": "msyh.ttc",
            "Arial": "arial.ttf",
            "宋体": "simsun.ttc",
            # 根据需要添加更多字体
        }

        font_file = font_mapping.get(font_name, None)
        if font_file:
            font_path = font_dir / font_file
            if font_path.exists():
                return str(font_path)
        return None

if __name__ == "__main__":
    TextToImage()
