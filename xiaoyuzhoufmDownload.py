import requests
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread

def download_with_retry(url, headers, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            return response
        except Exception as e:
            if i == max_retries - 1:
                raise e
            print(f"下载失败,正在进行第{i+2}次尝试...")
            time.sleep(2)

class DownloaderUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("小宇宙FM下载器")
        self.window.geometry("800x500")

        # URL输入框
        url_frame = ttk.Frame(self.window)
        url_frame.pack(pady=20, padx=20, fill="x")

        ttk.Label(url_frame, text="播客URL:").pack(side="left")
        self.url_var = tk.StringVar(value="https://www.xiaoyuzhoufm.com/episode/674069e7330e2b35372dec69")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # 保存路径选择框
        path_frame = ttk.Frame(self.window)
        path_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(path_frame, text="保存路径:").pack(side="left")
        self.path_var = tk.StringVar(value="")
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))

        self.browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_path)
        self.browse_btn.pack(side="right")

        # 下载按钮
        self.download_btn = ttk.Button(self.window, text="开始下载", command=self.start_download)
        self.download_btn.pack(pady=10)

        # 状态标签
        self.status_label = ttk.Label(self.window, text="")
        self.status_label.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.window, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # 日志文本框
        self.log_text = tk.Text(self.window, height=8, width=50)
        self.log_text.pack(pady=10)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def update_progress(self, value):
        self.progress["value"] = value
        self.window.update_idletasks()

    def start_download(self):
        self.download_btn.config(state="disabled")
        self.progress["value"] = 0
        Thread(target=self.download_mp3, daemon=True).start()

    def download_mp3(self):
        url = self.url_var.get()
        self.update_status("开始下载小宇宙FM音频...")

        try:
            driver = webdriver.Chrome()
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            audio_element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "audio"))
            )

            content = driver.page_source
            driver.quit()

            soup = BeautifulSoup(content, 'html.parser')
            audio_tag = soup.find('audio')
            if not audio_tag:
                self.update_status("未找到音频标签!")
                return

            audio_url = audio_tag.get('src')
            if not audio_url:
                self.update_status("未找到音频地址!")
                return

            title_tag = soup.find('title')
            title = title_tag.text if title_tag else 'podcast'

            self.update_status(f"正在下载: {title}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }

            response = download_with_retry(audio_url, headers)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded_size = 0

            filename = f"{title}.mp3"
            filename = "".join(x for x in filename if x.isalnum() or x in (' ', '-', '_', '.'))

            save_path = self.path_var.get()
            if save_path:
                filename = f"{save_path}/{filename}"

            with open(filename, 'wb') as f:
                for data in response.iter_content(block_size):
                    size = f.write(data)
                    downloaded_size += size
                    progress = (downloaded_size / total_size) * 100
                    self.update_progress(progress)

            self.update_status(f"下载完成! 文件已保存为: {filename}")

        except Exception as e:
            self.update_status(f"下载失败: {str(e)}")
            if 'driver' in locals():
                driver.quit()
        finally:
            self.download_btn.config(state="normal")

if __name__ == "__main__":
    app = DownloaderUI()
    app.window.mainloop()
