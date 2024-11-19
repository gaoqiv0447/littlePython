# 目前还存在一定的兼容性问题，需要进一步优化

import tkinter as tk
from tkinter import filedialog
from win32com import client
import os
import pythoncom  # 添加导入

class PPT2PDFConverter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("PPT转PDF工具")
        self.window.geometry("800x400")

        self.selected_file = None

        # 创建选择文件按钮
        self.select_btn = tk.Button(self.window,
                                  text="选择PPT文件",
                                  command=self.select_file,
                                  width=20,
                                  height=2)
        self.select_btn.pack(pady=20)

        # 创建转换按钮
        self.convert_btn = tk.Button(self.window,
                                   text="转换为PDF",
                                   command=self.convert_to_pdf,
                                   width=20,
                                   height=2,
                                   state=tk.DISABLED)
        self.convert_btn.pack(pady=20)

        # 状态标签
        self.status_label = tk.Label(self.window, text="")
        self.status_label.pack(pady=10)

    def select_file(self):
        filetypes = [("PowerPoint文件", "*.ppt;*.pptx")]
        self.selected_file = filedialog.askopenfilename(filetypes=filetypes)
        if self.selected_file:
            self.status_label.config(text=f"已选择文件: {os.path.basename(self.selected_file)}")
            self.convert_btn.config(state=tk.NORMAL)

    def convert_to_pdf(self):
        if not self.selected_file:
            return

        try:
            # 固定PDF保存路径为D:\1.pdf
            pdf_path = "D:\\1.pdf"

            print(f"转换路径: {self.selected_file} 到 {pdf_path}")  # 添加打印语句

            # 初始化COM
            pythoncom.CoInitialize()

            # 创建PowerPoint应用程序实例
            powerpoint = client.Dispatch("Powerpoint.Application")
            powerpoint.Visible = True

            # 打开PPT文件
            deck = powerpoint.Presentations.Open(self.selected_file)

            # 另存为PDF
            deck.SaveAs(pdf_path, 32)  # 32 代表 PDF 格式

            # 关闭文件和应用
            deck.Close()
            powerpoint.Quit()

            self.status_label.config(text="转换成功！PDF已保存到D:\\1.pdf")

        except Exception as e:
            self.status_label.config(text=f"转换失败: {str(e)}")
            print(f"转换失败: {str(e)}")
        finally:
            # 释放COM资源
            pythoncom.CoUninitialize()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PPT2PDFConverter()
    app.run()
