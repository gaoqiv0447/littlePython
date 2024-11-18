import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

input_path = None

def select_image():
    global input_path
    input_path = filedialog.askopenfilename(filetypes=[
        ("所有支持的图片格式", "*.webp;*.png;*.psd;*.heic;*.gif;*.jpg;*.jpeg;*.bmp;*.tiff"),
        ("WEBP文件", "*.webp"),
        ("PNG文件", "*.png"),
        ("PSD文件", "*.psd"),
        ("HEIC文件", "*.heic"),
        ("GIF文件", "*.gif"),
        ("JPEG文件", "*.jpg;*.jpeg"),
        ("BMP文件", "*.bmp"),
        ("TIFF文件", "*.tiff")
    ])
    if input_path:
        input_button.config(text=f"已选择: {input_path}")

def convert_to_jpg():

    output_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG文件", "*.jpg")]
    )

    if output_path:
        try:
            with Image.open(input_path) as img:
                # 如果是动图,只保存第一帧
                if hasattr(img, 'n_frames'):
                    img.seek(0)
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                img.save(output_path, 'JPEG', quality=95)
                save_button.config(text=f"已保存至: {output_path}")
                tk.messagebox.showinfo("成功", "图片转换完成!")
        except Exception as e:
            tk.messagebox.showerror("错误", f"转换失败: {str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("图片转JPG工具")
root.geometry("400x200")

# 创建按钮
input_button = tk.Button(root, text="选择输入图片", command=select_image)
input_button.pack(pady=20)

save_button = tk.Button(root, text="选择保存位置并转换", command=convert_to_jpg)
save_button.pack(pady=20)

# 运行主循环
root.mainloop()
