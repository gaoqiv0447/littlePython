import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger

def select_pdf1():
    global pdf1_path
    pdf1_path = filedialog.askopenfilename(filetypes=[("PDF文件", "*.pdf")])
    pdf1_button.config(text=f"已选择: {pdf1_path}")

def select_pdf2():
    global pdf2_path
    pdf2_path = filedialog.askopenfilename(filetypes=[("PDF文件", "*.pdf")])
    pdf2_button.config(text=f"已选择: {pdf2_path}")

def save_merged_pdf():
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF文件", "*.pdf")])
    if output_path:
        merger = PdfMerger()
        merger.append(pdf1_path)
        merger.append(pdf2_path)
        merger.write(output_path)
        merger.close()
        save_button.config(text=f"已保存至: {output_path}")

# 创建主窗口
root = tk.Tk()
root.title("PDF合并工具")
root.geometry("400x200")

# 创建三个按钮
pdf1_button = tk.Button(root, text="选择第一个PDF文件", command=select_pdf1)
pdf1_button.pack(pady=10)

pdf2_button = tk.Button(root, text="选择第二个PDF文件", command=select_pdf2)
pdf2_button.pack(pady=10)

save_button = tk.Button(root, text="选择保存位置并合并", command=save_merged_pdf)
save_button.pack(pady=10)

# 运行主循环
root.mainloop()
