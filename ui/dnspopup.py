# ui/dnspopup.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable


class DNSConfigPopup(tk.Toplevel):
    """
    DNS 配置窗口。
    通过回调把选中的 DNS IP 返回给主界面。
    """

    def __init__(self, parent, on_dns_selected: Callable[[str], None]):
        super().__init__(parent)
        self.title("配置 DNS")
        self.resizable(False, False)
        self.on_dns_selected = on_dns_selected

        self.var_choice = tk.StringVar(value="ali")
        self.var_custom = tk.StringVar(value="")

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="选择一个 DNS 提供商：").pack(anchor="w", pady=(0, 5))

        choices = [
            ("阿里 223.5.5.5", "223.5.5.5"),
            ("DNSPod 119.29.29.29", "119.29.29.29"),
            ("Google 8.8.8.8", "8.8.8.8"),
        ]

        self.dns_map = {}

        for text, ip in choices:
            val = ip
            self.dns_map[val] = text
            ttk.Radiobutton(
                frm,
                text=text,
                variable=self.var_choice,
                value=val
            ).pack(anchor="w")

        ttk.Radiobutton(
            frm,
            text="自定义：",
            variable=self.var_choice,
            value="custom"
        ).pack(anchor="w", pady=(5, 0))

        entry = ttk.Entry(frm, textvariable=self.var_custom, width=20)
        entry.pack(anchor="w", pady=(0, 10))

        btns = ttk.Frame(frm)
        btns.pack(anchor="e", pady=(5, 0))

        ttk.Button(btns, text="取消", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(btns, text="应用", command=self._on_ok).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.focus_set()

    def _on_ok(self):
        choice = self.var_choice.get()
        if choice == "custom":
            ip = self.var_custom.get().strip()
            if not ip:
                messagebox.showerror("错误", "请输入自定义 DNS IP。", parent=self)
                return
        else:
            ip = choice

        self.on_dns_selected(ip)
        self.destroy()
