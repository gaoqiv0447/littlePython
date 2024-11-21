import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
from PIL import Image
import os

class VideoConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图片视频转换器")
        self.image_path = None
        self.video_path = None
        self.setup_ui()

    def setup_ui(self):
        # 创建按钮
        self.btn_select_image = tk.Button(self.root, text="选择图片", command=self.select_image)
        self.btn_select_image.pack(pady=10)

        self.image_label = tk.Label(self.root, text="未选择图片")
        self.image_label.pack()

        self.btn_select_video = tk.Button(self.root, text="选择视频", command=self.select_video)
        self.btn_select_video.pack(pady=10)

        self.video_label = tk.Label(self.root, text="未选择视频")
        self.video_label.pack()

        self.btn_merge = tk.Button(self.root, text="合并拼接", command=self.merge_files)
        self.btn_merge.pack(pady=10)

        # 创建进度条
        self.progress_bar = ttk.Progressbar(
            self.root,
            orient='horizontal',
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
        )
        if self.image_path:
            self.image_label.config(text=f"已选择图片: {os.path.basename(self.image_path)}")
            print(f"选择的图片: {self.image_path}")

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4")]
        )
        if self.video_path:
            self.video_label.config(text=f"已选择视频: {os.path.basename(self.video_path)}")
            print(f"选择的视频: {self.video_path}")

    def resize_image(self, input_path, output_path):
        """调整图片尺寸为偶数"""
        try:
            with Image.open(input_path) as img:
                # 获取原始尺寸
                width, height = img.size
                # 确保宽度和高度都是偶数
                new_width = width - (width % 2)
                new_height = height - (height % 2)
                # 调整尺寸
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # 保存调整后的图片
                resized_img.save(output_path, quality=95)
            return True
        except Exception as e:
            print(f"调整图片尺寸时出错: {e}")
            return False

    def convert_image_to_video(self):
        """将图片转换为视频"""
        if not self.image_path:
            messagebox.showwarning("警告", "请先选择图片")
            return False

        try:
            # 创建临时目录
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)

            # 调整图片尺寸
            temp_image = os.path.join(temp_dir, "resized_image.jpg")
            if not self.resize_image(self.image_path, temp_image):
                return False

            # 转换为视频
            temp_video = os.path.join(temp_dir, "image_video.mp4")
            result = subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', temp_image,
                '-c:v', 'libx264',
                '-t', '2',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
                temp_video
            ], capture_output=True)

            if result.returncode == 0:
                print("图片成功转换为视频")
                return temp_video
            else:
                print(f"转换失败: {result.stderr.decode()}")
                return False

        except Exception as e:
            print(f"转换过程中出错: {e}")
            return False

    def merge_files(self):
        if not self.image_path or not self.video_path:
            messagebox.showwarning("警告", "请先选择图片和视频文件")
            return

        try:
            self.status_label.config(text="正在处理...")
            self.progress_bar["value"] = 0
            self.root.update()

            # 转换图片为视频
            temp_video = self.convert_image_to_video()
            if not temp_video:
                messagebox.showerror("错误", "图片转换失败")
                return

            # 创建合并列表
            list_file = os.path.join("temp", "concat_list.txt")
            with open(list_file, 'w', encoding='utf-8') as f:
                f.write(f"file '{os.path.abspath(temp_video)}'\n")
                f.write(f"file '{os.path.abspath(self.video_path)}'\n")

            # 合并视频
            output_video = "output.mp4"
            result = subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_video
            ], capture_output=True)

            if result.returncode == 0:
                self.progress_bar["value"] = 100
                self.status_label.config(text="处理完成!")
                messagebox.showinfo("成功", f"视频已保存为: {output_video}")
            else:
                print(f"合并失败: {result.stderr.decode()}")
                messagebox.showerror("错误", "视频合并失败")

        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出错: {str(e)}")
        finally:
            # 清理临时文件
            self.cleanup()

    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists("temp"):
                for file in os.listdir("temp"):
                    try:
                        os.remove(os.path.join("temp", file))
                    except:
                        pass
                os.rmdir("temp")
        except:
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoConverter()
    app.run()
