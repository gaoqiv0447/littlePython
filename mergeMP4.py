#!/usr/bin/python
# coding=utf-8
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import subprocess
import time
import shutil

class MergeMP4UI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("MP4拼接工具（请保证视频文件各个参数一致）")
        self.window.geometry("800x300")

        self.folder_path = None

        # 选择文件夹按钮
        self.select_folder_btn = tk.Button(
            self.window,
            text="选择文件夹",
            command=self.select_folder,
            width=20,
            height=2
        )
        self.select_folder_btn.pack(pady=20)

        # 文件夹路径标签
        self.folder_label = tk.Label(self.window, text="未选择文件夹")
        self.folder_label.pack()

        # 合并按钮
        self.merge_btn = tk.Button(
            self.window,
            text="合并视频",
            command=self.merge_videos,
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.merge_btn.pack(pady=20)

        # 进度条
        self.progress_bar = ttk.Progressbar(
            self.window,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress_bar.pack(pady=20)

        # 进度标签
        self.progress_label = tk.Label(self.window, text="")
        self.progress_label.pack()

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=f"已选择文件夹: {self.folder_path}")
            self.merge_btn.config(state=tk.NORMAL)

    def merge_videos(self):
        try:
            # 获取所有MP4文件
            mp4_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.mp4')]
            if not mp4_files:
                messagebox.showinfo("提示", "所选文件夹中没有MP4文件")
                return

            mp4_files.sort()  # 按文件名排序

            # 创建临时工作目录
            temp_dir = os.path.join(self.folder_path, 'temp_merge')
            os.makedirs(temp_dir, exist_ok=True)

            # 复制文件而不是创建符号链接
            temp_files = []
            for i, video in enumerate(mp4_files):
                temp_name = f"{i:03d}.mp4"
                temp_path = os.path.join(temp_dir, temp_name)
                source_path = os.path.join(self.folder_path, video)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                # 使用复制替代符号链接
                shutil.copy2(source_path, temp_path)
                temp_files.append(temp_name)

            # 创建文件列表
            list_file = os.path.join(temp_dir, 'file_list.txt')
            with open(list_file, 'w', encoding='utf-8') as f:
                for video in temp_files:
                    f.write(f"file '{video}'\n")

            # 设置输出文件名
            output_file = os.path.join(self.folder_path, 'merged_output.mp4')

            # 切换到临时目录
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            # 合并命令
            merge_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', 'file_list.txt',
                '-c', 'copy',
                output_file
            ]

            # 更新进度条
            self.progress_bar["value"] = 0
            self.progress_label.config(text="开始合并视频...")
            self.window.update()

            # 执行合并
            process = subprocess.Popen(merge_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # 监控进度
            total_files = len(mp4_files)
            current_file = 0
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if 'Opening' in output and '.mp4' in output:
                    current_file += 1
                    progress = (current_file / total_files) * 100
                    self.progress_bar["value"] = progress
                    self.progress_label.config(text=f"合并进度: {current_file}/{total_files}")
                    self.window.update()

            # 切换回原始目录
            os.chdir(original_dir)

            if process.returncode == 0:
                # 合并成功,进度条显示100%
                self.progress_bar["value"] = 100
                self.progress_label.config(text="合并进度: 100%")
                self.window.update()

                # 清理临时文件和目录
                for temp_file in temp_files:
                    temp_path = os.path.join(temp_dir, temp_file)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                os.remove(list_file)
                os.rmdir(temp_dir)

                messagebox.showinfo("完成", f"视频合并完成!\n输出文件: {output_file}")
            else:
                raise Exception("FFmpeg合并失败")

        except Exception as e:
            messagebox.showerror("错误", f"合并视频时出错: {str(e)}")
            # 清理临时目录
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                try:
                    for f in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, f))
                    os.rmdir(temp_dir)
                except:
                    pass

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MergeMP4UI()
    app.run()
