# app/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import sys
import platform
import psutil
import subprocess
import os
from typing import Dict, Tuple

from ui.scrollpanel import ScrollableFrame
from ui.logpanel import LogPanel
from ui.dnspopup import DNSConfigPopup

from modules.task_runner import TaskRunner, TaskDef, TaskLevel
import modules.sys_tasks as sys_tasks
import modules.net_tasks as net_tasks
import modules.game_tasks as game_tasks
from modules import diagnostics

# GPU 信息（可选）
try:
    import GPUtil
    GPU_SUPPORT = True
except Exception:
    GPU_SUPPORT = False


# ============================================================
#                 管理员权限检测与提权
# ============================================================
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def restart_as_admin():
    """EXE 模式下提权，.py 模式只给提示。"""
    if sys.argv[0].endswith(".py"):
        messagebox.showinfo(
            "提示",
            "当前通过 .py 或 PyCharm 运行。\n\n"
            "若需管理员权限，请以管理员身份运行 PyCharm\n"
            "或使用打包后的 EXE。",
        )
        return

    exe_path = sys.executable
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        exe_path,
        None,
        None,
        1
    )
    os._exit(0)


# ============================================================
#                          主界面 App
# ============================================================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("多功能轻量优化工具（GamerTool）")
        self.root.geometry("1200x780")

        # 日志面板
        self.log_panel = LogPanel(self.root)
        self.log_panel.pack(side="bottom", fill="x")
        self.logger = self.log_panel.log

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # 任务变量映射： key → (TaskDef, BooleanVar)
        self.task_vars: Dict[str, Tuple[TaskDef, tk.BooleanVar]] = {}

        # DNS 设置
        self.dns_target_ip = None
        self._dns_checkbox = None

        # 每个 Tab 的说明区 Text
        self.desc_widgets = {}

        # 构建各个 Tab
        self._create_system_tab()
        self._create_network_tab()
        self._create_game_tab()
        self._create_tools_tab()

        # 底部执行按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(
            btn_frame,
            text="执行所有勾选任务",
            command=self._on_run_clicked
        ).pack()

        # 任务执行器
        self.runner = TaskRunner(logger=self.logger, tk_root=self.root)

    # ============================================================
    #        左右分栏布局：左任务列表 + 右说明区
    # ============================================================
    def _create_dual_pane(self, tab, tab_key: str):
        main = ttk.Frame(tab)
        main.pack(fill="both", expand=True)

        # 左侧滚动区
        left_frame = ScrollableFrame(main)
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        # 右侧说明区
        right_frame = ttk.Frame(main)
        right_frame.pack(side="right", fill="both", expand=True)

        desc = tk.Text(
            right_frame,
            wrap="word",
            font=("Microsoft YaHei", 10),
            state="disabled",
        )
        desc.pack(fill="both", expand=True)

        admin_text = "是" if is_admin() else "否"
        self._write_desc(
            desc,
            f"【当前管理员权限】：{admin_text}\n\n"
            f"当前页面：{tab_key}\n"
            f"请在左侧勾选或点击任务查看详细说明。",
        )

        self.desc_widgets[tab_key] = desc
        return left_frame.inner, desc

    def _write_desc(self, widget: tk.Text, text: str):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.config(state="disabled")

    def show_description(self, text: str):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        desc = self.desc_widgets.get(current_tab)
        if desc:
            self._write_desc(desc, text)

    # ============================================================
    #                       系统优化 TAB
    # ============================================================
    def _create_system_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="系统优化")

        left, _ = self._create_dual_pane(tab, "系统优化")

        ttk.Label(left, text="系统轻量任务（LEVEL 1）：").pack(anchor="w", pady=(0, 5))

        sys_items = [
            ("clean_temp", "清理临时文件 (TEMP)", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_temp(self.logger),
             "清理系统 TEMP 目录的临时文件，释放空间，提高响应速度。"),

            ("clean_prefetch", "清理 Prefetch", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_prefetch(self.logger),
             "清理 Windows 预取缓存，优化开机与程序启动。"),

            ("clean_dx_shader", "清理 DX Shader Cache", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_dx_shader_cache(self.logger),
             "删除 DirectX 着色器缓存，修复画面异常、着色器膨胀问题。"),

            ("clean_nv_shader", "清理 NVIDIA Shader Cache", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_nvidia_shader_cache(self.logger),
             "清除 NVIDIA Shader 缓存，缓解某些游戏卡顿、闪退。"),

            ("clean_recent", "清理最近使用文件 (Recent)", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_recent(self.logger),
             "清理 Recent 列表，保护隐私并减少资源管理器负担。"),

            ("clean_win_update_cache", "清理 Windows 更新缓存", TaskLevel.LEVEL1,
             lambda: sys_tasks.clean_windows_update_cache(self.logger),
             "清理 Windows Update 缓存，解决更新失败或磁盘占用。"),
        ]
        for key, label, level, func, desc_text in sys_items:
            self._add_task_row(left, key, label, level, func, desc_text, tab_key="系统优化")

        ttk.Label(left, text="系统谨慎任务（LEVEL 2）：").pack(anchor="w", pady=(15, 5))

        lv2_items = [
            ("refresh_gpu_idle", "刷新 GPU IdleTasks", TaskLevel.LEVEL2,
             lambda: sys_tasks.refresh_gpu_idle_tasks(self.logger),
             "刷新 GPU IdleTasks，有助于恢复图形相关组件的正常状态。"),

            ("refresh_dwm", "刷新 DWM（会黑屏）", TaskLevel.LEVEL2,
             lambda: sys_tasks.refresh_dwm(self.logger),
             "重启桌面窗口管理器 DWM，可修复：\n"
             "- 窗口透明异常\n"
             "- 程序边框失效\n"
             "- 桌面动画卡顿\n"
             "- 部分 GPU 画面异常\n\n"
             "⚠ 注意：刷新 DWM 会导致 Wallpaper Engine 的动态壁纸暂时停止播放，"
             "甚至卡死或不恢复。\n"
             "如遇异常，关闭并重新启动 Wallpaper Engine 即可恢复。"
             ),
        ]
        for key, label, level, func, desc_text in lv2_items:
            self._add_task_row(left, key, label, level, func, desc_text, tab_key="系统优化")

        # LEVEL 3 深度干净重启
        ttk.Label(left, text="系统重启相关（LEVEL 3）：").pack(anchor="w", pady=(15, 5))

        def reboot_func():
            self.logger("执行：shutdown /g /f /t 0")
            subprocess.run(["shutdown", "/g", "/f", "/t", "0"], check=True)

        self._add_task_row(
            left,
            "deep_reboot",
            "深度干净重启（立即重启）",
            TaskLevel.LEVEL3,
            reboot_func,
            "执行 shutdown /g /f /t 0 进行深度干净重启：\n"
            "- 重新初始化 GPU 驱动\n"
            "- 刷新图形堆栈\n"
            "- 清理大量系统内部状态\n\n"
            "适用于：黑屏、花屏、动画异常、驱动更新后莫名卡顿等情况。\n"
            "⚠ 执行后电脑会立即重启，请先保存好你的文件。",
            tab_key="系统优化"
        )

    # ============================================================
    #                       网络工具 TAB
    # ============================================================
    def _create_network_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="网络工具")

        left, _ = self._create_dual_pane(tab, "网络工具")

        ttk.Label(left, text="网络轻量任务（LEVEL 1）：").pack(anchor="w", pady=(0, 5))

        net_items = [
            ("flush_dns", "刷新 DNS 缓存", TaskLevel.LEVEL1,
             lambda: net_tasks.flush_dns(self.logger),
             "清除系统 DNS 缓存，用于解决 DNS 记录错误、网站打不开等问题。"),

            ("winsock_reset", "重置 Winsock", TaskLevel.LEVEL1,
             lambda: net_tasks.winsock_reset(self.logger),
             "重置网络协议栈 Winsock，修复网络异常或连接失败问题。"),

            ("tcpip_reset", "轻量重置 TCP/IP", TaskLevel.LEVEL1,
             lambda: net_tasks.tcpip_reset(self.logger),
             "轻量级修复 TCP/IP 协议栈，不修改你的 IP 配置。"),
        ]
        for key, label, level, func, desc_text in net_items:
            self._add_task_row(left, key, label, level, func, desc_text, tab_key="网络工具")

        ttk.Label(left, text="网络谨慎任务（LEVEL 2）：").pack(anchor="w", pady=(15, 5))

        frame = ttk.Frame(left)
        frame.pack(anchor="w", pady=2, fill="x")

        var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(frame, text="应用 DNS 设置（未配置）", variable=var)
        cb.pack(side="left")
        self._dns_checkbox = cb

        def dns_func():
            if not self.dns_target_ip:
                self.logger("DNS 未配置，跳过执行。")
                return
            net_tasks.set_dns(self.logger, self.dns_target_ip)

        dns_task = TaskDef(
            key="set_dns",
            label="应用 DNS 设置",
            level=TaskLevel.LEVEL2,
            func=dns_func,
            warn="执行后会通过 netsh 修改网卡 DNS，网络会短暂掉线。",
            is_dns_task=True
        )
        self.task_vars["set_dns"] = (dns_task, var)

        lbl = ttk.Label(frame, text="  查看说明")
        lbl.pack(side="left", padx=8)
        lbl.bind(
            "<Button-1>",
            lambda e: self.show_description(
                "通过 netsh 命令修改网卡 DNS 服务器地址。\n\n"
                "可用来切换阿里 / 腾讯 / Google / Cloudflare 等公共 DNS，"
                "提升解析速度或稳定性。\n\n"
                "注意：执行时会短暂掉线。"
            )
        )
        lbl.configure(cursor="hand2")

        ttk.Button(frame, text="配置…", command=self._open_dns_popup).pack(side="right")

    # ============================================================
    #                       游戏增强 TAB
    # ============================================================
    def _create_game_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="游戏增强")

        left, _ = self._create_dual_pane(tab, "游戏增强")

        ttk.Label(left, text="游戏增强（LEVEL 1）：").pack(anchor="w", pady=(0, 5))

        game_items = [
            ("disable_uwp_bg", "禁用部分 UWP 后台", TaskLevel.LEVEL1,
             lambda: game_tasks.disable_uwp_background(self.logger),
             "禁用部分 UWP 应用后台活动，减少后台占用，不影响 Store / 系统更新。"),

            ("high_perf_power", "切换高性能电源计划", TaskLevel.LEVEL1,
             lambda: game_tasks.set_high_performance_plan(self.logger),
             "切换为高性能电源计划，减少节能策略导致的降频。"),

            ("set_balanced_plan", "切换平衡电源计划", TaskLevel.LEVEL1,
             lambda: game_tasks.set_balanced_plan(self.logger),
             "切换到平衡电源模式。"),

            ("set_power_saver_plan", "切换节能电源计划", TaskLevel.LEVEL1,
             lambda: game_tasks.set_power_saver_plan(self.logger),
             "切换到节能模式，降低功耗的同时降低性能。"),

            ("enable_gamemode", "启用 GameMode", TaskLevel.LEVEL1,
             lambda: game_tasks.enable_game_mode(self.logger),
             "启用 Windows GameMode，使游戏获得更高 CPU/GPU 优先级。"),

            ("clean_game_cache", "清理游戏 Shader Cache", TaskLevel.LEVEL1,
             lambda: game_tasks.clean_game_shader_cache(self.logger),
             "清理 Steam / WeGame Shader 缓存，修复卡顿、异常着色等问题。"),
        ]
        for key, label, level, func, desc_text in game_items:
            self._add_task_row(left, key, label, level, func, desc_text, tab_key="游戏增强")

    # ============================================================
    #                     工具与设置 TAB
    # ============================================================
    def _create_tools_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="工具与设置")

        left, _ = self._create_dual_pane(tab, "工具与设置")

        is_adm = "是" if is_admin() else "否"
        ttk.Label(left, text=f"当前管理员权限：{is_adm}").pack(anchor="w", pady=(0, 10))

        ttk.Button(left, text="以管理员身份重新启动本工具", command=restart_as_admin)\
            .pack(anchor="w", pady=5)

        # 系统信息
        ttk.Label(left, text="系统信息：").pack(anchor="w", pady=(15, 5))

        def show_sysinfo():
            info = []
            info.append(f"系统：{platform.system()} {platform.release()}")
            info.append(f"版本号：{platform.version()}")

            freq = psutil.cpu_freq()
            if freq:
                info.append(f"CPU 频率：{freq.current:.0f} MHz")
            info.append(f"CPU：{platform.processor()}")
            info.append(f"物理核心：{psutil.cpu_count(logical=False)}")
            info.append(f"逻辑核心：{psutil.cpu_count(logical=True)}")

            mem = psutil.virtual_memory()
            info.append(f"内存总量：{mem.total / (1024 ** 3):.2f} GB")
            info.append(f"内存占用：{mem.percent}%")

            if GPU_SUPPORT:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        info.append(f"GPU：{gpu.name}")
                        info.append(f"显存占用：{gpu.memoryUsed} MB / {gpu.memoryTotal} MB")
                        info.append(f"GPU 温度：{gpu.temperature}°C")
                    else:
                        info.append("GPU：未检测到 GPU")
                except Exception:
                    info.append("GPU 信息读取失败（GPUtil 异常）")
            else:
                info.append("GPU 信息：未安装 GPUtil（可选依赖）")

            self.show_description("\n".join(info))

        ttk.Button(left, text="显示系统信息", command=show_sysinfo)\
            .pack(anchor="w", pady=5)

        # 打开任务管理器
        ttk.Button(left, text="打开任务管理器", command=lambda: subprocess.Popen("taskmgr"))\
            .pack(anchor="w", pady=10)

        # 设备驱动诊断（HID / USB / 键鼠）
        ttk.Label(left, text="诊断工具：").pack(anchor="w", pady=(15, 5))

        ttk.Button(left, text="分析设备驱动错误（HID/USB）", command=self._diagnose_hid)\
            .pack(anchor="w", pady=5)

    # ============================================================
    #                    公共：添加任务行
    # ============================================================
    def _add_task_row(self, parent, key, label, level, func, description, tab_key: str):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(row, variable=var)
        cb.pack(side="left")

        lbl = ttk.Label(row, text=f"{label}  [L{level.value}]")
        lbl.pack(side="left", padx=5)
        lbl.bind("<Button-1>", lambda e, text=description: self.show_description(text))
        lbl.configure(cursor="hand2")

        task = TaskDef(key=key, label=label, level=level, func=func, description=description)
        self.task_vars[key] = (task, var)

    # ============================================================
    #                       DNS 配置弹窗
    # ============================================================
    def _open_dns_popup(self):
        def on_selected(ip: str):
            self.dns_target_ip = ip
            if self._dns_checkbox:
                self._dns_checkbox.config(text=f"应用 DNS 设置（当前：{ip}）")

            self.show_description(
                f"已选择 DNS：{ip}\n\n"
                "此处仅配置目标 DNS，真正应用需要：\n"
                "1. 勾选左侧「应用 DNS 设置」任务；\n"
                "2. 点击底部「执行所有勾选任务」按钮。\n\n"
                "执行时会通过 netsh 修改网卡 DNS，网络会短暂掉线。"
            )
            self.logger(f"DNS 已配置为：{ip}")

        DNSConfigPopup(self.root, on_selected)

    # ============================================================
    #                   HID/USB 驱动诊断入口
    # ============================================================
    def _diagnose_hid(self):
        text = diagnostics.analyze_hid_usb_issues(self.logger)
        self.show_description(text)

    # ============================================================
    #                        执行任务入口
    # ============================================================
    def _on_run_clicked(self):
        selected = {
            key: (task_def, var.get())
            for key, (task_def, var) in self.task_vars.items()
        }
        self.runner.run_selected_tasks(selected)


# ============================================================
#                          启动函数
# ============================================================
def run_app():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
