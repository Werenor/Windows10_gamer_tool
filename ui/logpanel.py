# ui/logpanel.py
import tkinter as tk
from tkinter import ttk
import datetime


class LogPanel(ttk.Frame):
    """
    底部日志区域：
    - 不可编辑
    - 自动追加日志
    - 自动滚动到底部
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        label = ttk.Label(self, text="执行日志：")
        label.pack(anchor="w")

        self.text = tk.Text(
            self,
            height=10,
            state="disabled",
            wrap="word",
        )
        scrollbar = ttk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.text.configure(state="normal")
        self.text.insert("end", line)
        self.text.see("end")
        self.text.configure(state="disabled")
