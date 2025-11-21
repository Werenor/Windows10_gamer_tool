# modules/diagnostics_core.py
"""
核心诊断模块：
- setupapi.dev.log 高级解析
- System.evtx 扫描（USB/HID/驱动相关 EventID）
- WER 错误报告扫描
- LiveKernelReports 扫描
"""

import os
import subprocess
from typing import List

from .device_id import resolve_vid_pid


# ============================================================
#                读取 setupapi.dev.log（驱动安装日志）
# ============================================================
SETUPAPI_PATH = r"C:\Windows\INF\setupapi.dev.log"

KEYWORDS = [
    "failed",
    "error",
    "not migrated",
    "device removed",
    "install failed",
    "driver",
    "HID",
    "USB",
    "Keyboard",
    "Mouse",
]

def scan_setupapi() -> List[str]:
    """扫描 setupapi.dev.log 并返回匹配的异常行（带 VID/PID 解析）"""

    if not os.path.exists(SETUPAPI_PATH):
        return ["未找到 setupapi.dev.log"]

    # 尝试 utf-8 读取
    try:
        with open(SETUPAPI_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except:
        # 再尝试 ANSI
        with open(SETUPAPI_PATH, "r", encoding="mbcs", errors="ignore") as f:
            lines = f.readlines()

    lines = lines[-500:]  # 只取最近 500 行，避免太旧数据干扰

    result = []
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in KEYWORDS):
            vendor, hint = resolve_vid_pid(line)
            if vendor != "Unknown Vendor" or hint:
                result.append(
                    f"{line.strip()}\n    → 设备识别：{vendor}"
                    + (f"（{hint}）" if hint else "")
                )
            else:
                result.append(line.strip())

    if not result:
        return ["未检测到 setupapi.dev.log 中的 HID/USB 相关异常记录。"]

    return ["【setupapi.dev.log 检测到异常】"] + result


# ============================================================
#       使用 wevtutil 扫描 System.evtx（系统事件日志）
# ============================================================

EVENT_IDS = [22, 51, 2100, 2101, 7000, 7001, 7005, 7034, 10110, 10111]

def scan_system_event_log() -> List[str]:
    """
    扫描 System.evtx 里和 USB/HID/驱动有关的事件
    使用系统内置 wevtutil，不依赖第三方库
    """

    result = ["【System.evtx 事件日志】"]

    for event_id in EVENT_IDS:
        cmd = (
            f'wevtutil qe System /q:"*[System[(EventID={event_id})]]" /c:10 /f:text'
        )
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT,
                encoding="utf-8", errors="ignore"
            )
            if output.strip():
                result.append(f"[EventID {event_id}]")
                result.append(output.strip())
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            result.append(f"读取事件 {event_id} 时出错：{e}")

    if len(result) == 1:
        return ["System.evtx 中未找到相关事件。"]

    return result


# ============================================================
#                   扫描 WER 崩溃报告
# ============================================================

WER_PATH = r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive"

def scan_wer_reports() -> List[str]:
    result = ["【WER 错误报告】"]

    if not os.path.exists(WER_PATH):
        return ["未找到 WER 报告目录"]

    found = False
    for root, _, files in os.walk(WER_PATH):
        for f in files:
            if "Report.wer" in f:
                found = True
                full = os.path.join(root, f)
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as fp:
                        text = fp.read()
                        if ("HID" in text or "USB" in text
                            or "driver" in text.lower()
                            or "nvlddmkm" in text
                            or "Kernel" in text):
                            result.append(f"\n报告：{full}\n{text}")
                except:
                    pass

    if not found:
        return ["未检测到 WER 报告"]

    return result


# ============================================================
#                   扫描 LiveKernelReports
# ============================================================

LIVEKERNEL_PATH = r"C:\Windows\LiveKernelReports"

def scan_livekernel() -> List[str]:
    result = ["【LiveKernelReports】"]

    if not os.path.exists(LIVEKERNEL_PATH):
        return ["未找到 LiveKernelReports 目录"]

    found = False
    for root, _, files in os.walk(LIVEKERNEL_PATH):
        for f in files:
            if f.endswith(".dmp"):
                found = True
                result.append(f"检测到内核转储文件：{os.path.join(root, f)}")

    if not found:
        return ["未检测到 LiveKernelReports 相关文件"]

    return result


# ============================================================
#                  合并所有诊断结果（统一输出）
# ============================================================

def run_full_diagnostics() -> str:
    """执行所有诊断并合并成文本"""

    sections = [
        scan_setupapi(),
        scan_system_event_log(),
        scan_wer_reports(),
        scan_livekernel(),
    ]

    output = []
    for sec in sections:
        output.append("\n".join(sec))
        output.append("\n" + "=" * 60 + "\n")

    return "\n".join(output)
