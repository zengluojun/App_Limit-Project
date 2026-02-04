# 主程序入口文件
import tkinter as tk
from gui import ACEProcessMonitor

def main():
    root = tk.Tk()
    app = ACEProcessMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()