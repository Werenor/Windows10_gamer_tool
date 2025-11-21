# ui/scrollpanel.py
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """
    一个可以竖向滚动的 Frame，里面放你的勾选框列表。
    用法：
        sf = ScrollableFrame(parent)
        sf.pack(fill="both", expand=True)
        inner = sf.inner  # 在 inner 里放控件
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 鼠标滚轮支持
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

    @staticmethod
    def _on_mousewheel(event, canvas: tk.Canvas):
        # Windows 上 event.delta 通常是 ±120
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
