# modules/diagnostics.py
"""
GUI 使用的统一诊断入口
负责调用 diagnostics_core 的所有扫描功能，并组合成高可读性报告。
"""

from typing import Callable
from .diagnostics_core import run_full_diagnostics

Logger = Callable[[str], None]


def analyze_hid_usb_issues(logger: Logger) -> str:
    """
    执行完整诊断流程，为 GUI 返回可读性强的报告。
    日志面板显示实时运行状态。
    """

    logger("正在执行 HID/USB 设备诊断，请稍候……")

    # 调用完整诊断引擎（setupapi + evtx + WER + LiveKernel）
    report = run_full_diagnostics()

    logger("诊断完成。")

    # 新增声明区域
    header = (
        "=== HID / USB 驱动与系统事件诊断报告 ===\n\n"
        "【重要说明】\n"
        "本报告可能会非常长，这是正常现象，因为 Windows 驱动安装日志、事件日志\n"
        "和系统服务记录会产生大量信息，并不代表系统存在严重问题。\n\n"
        "如果报告中出现您无法理解的内容，您可以：\n"
        "  1. 将报告复制给熟悉系统的技术人员查看；\n"
        "  2. 或者将内容复制给 AI（例如 ChatGPT）进行详细解释；\n"
        "  3. 如无 HID/USB 设备错误，则表示近期没有类似驱动异常。\n\n"
        "—————————————————————————————————————————————\n\n"
    )

    # 返回右侧说明区显示的完整文本
    return header + report + "\n（提示：如需更深入分析，可查看原始日志文件。）"
