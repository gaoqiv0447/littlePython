import os
import torch
from pathlib import Path
import warnings
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
# import openai.whisper as whisper
import whisper

class TranscriberUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("音频转文字工具")
        self.window.geometry("800x600")

        # 文件选择框
        file_frame = ttk.Frame(self.window)
        file_frame.pack(pady=20, padx=20, fill="x")

        ttk.Label(file_frame, text="音频文件:").pack(side="left")
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))

        self.browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        self.browse_btn.pack(side="right")

        # 转换按钮
        self.convert_btn = ttk.Button(self.window, text="开始转换", command=self.start_transcribe)
        self.convert_btn.pack(pady=10)

        # 状态标签
        self.status_label = ttk.Label(self.window, text="")
        self.status_label.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.window, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # 文本显示框
        self.text_display = tk.Text(self.window, height=20, width=60)
        self.text_display.pack(pady=10, padx=20, fill="both", expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("音频文件", "*.mp3;*.wav;*.m4a")])
        if file_path:
            self.file_var.set(file_path)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.window.update_idletasks()

    def update_progress(self, value):
        self.progress["value"] = value
        self.window.update_idletasks()

    def start_transcribe(self):
        if not self.file_var.get():
            self.update_status("请先选择音频文件!")
            return

        self.convert_btn.config(state="disabled")
        self.progress["value"] = 0
        Thread(target=self.transcribe_process, daemon=True).start()

    def transcribe_process(self):
        try:
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)

            self.update_status("正在加载模型...")
            self.update_progress(20)

            if not torch.cuda.is_available():
                self.update_status("警告: 未检测到GPU,将使用CPU进行转换,速度会较慢...")
                device = "cpu"
            else:
                device = "cuda"
                torch.cuda.empty_cache()

            model = whisper.load_model(
                "base",
                device=device,
                download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            )

            self.update_status("开始转录音频...")
            self.update_progress(40)

            options = {
                "language": "zh",
                "task": "transcribe",
                "fp16": True  # 默认启用fp16加速
            }

            result = model.transcribe(self.file_var.get(), **options)
            self.update_progress(80)

            # 保存文本结果到音频文件同目录下
            audio_path = Path(self.file_var.get())
            output_path = audio_path.with_suffix('.txt')
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

            # 显示结果
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, result["text"])
            self.update_progress(100)
            self.update_status(f"转录完成！结果已保存至: {output_path}")

        except Exception as e:
            self.update_status(f"转录失败: {str(e)}")
        finally:
            self.progress["value"] = 0
            self.convert_btn.config(state="normal")

if __name__ == "__main__":
    app = TranscriberUI()
    app.window.mainloop()
