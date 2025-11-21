import os
import shutil
import subprocess
from typing import Callable

Logger = Callable[[str], None]


# --------------------------
#  通用命令执行
# --------------------------
def _run_simple_command(cmd: list, logger: Logger):
    try:
        logger(f"  执行命令：{' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger(f"  命令执行错误码：{e.returncode}")
        raise
    except Exception as e:
        logger(f"  命令执行失败：{e}")
        raise


# --------------------------
#  TEMP 清理
# --------------------------
def clean_temp(logger: Logger):
    temp = os.getenv("TEMP")
    if not temp:
        logger("  未找到 TEMP 目录。")
        return
    logger(f"  清理临时文件夹：{temp}")
    for root, _, files in os.walk(temp):
        for f in files:
            fp = os.path.join(root, f)
            try:
                os.remove(fp)
            except Exception:
                pass


# --------------------------
#  Prefetch 清理
# --------------------------
def clean_prefetch(logger: Logger):
    path = r"C:\Windows\Prefetch"
    logger(f"  清理 Prefetch：{path}")
    if os.path.isdir(path):
        for f in os.listdir(path):
            fp = os.path.join(path, f)
            try:
                os.remove(fp)
            except Exception:
                pass
    else:
        logger("  Prefetch 不存在。")


# --------------------------
#  DX Shader Cache
# --------------------------
def clean_dx_shader_cache(logger: Logger):
    local = os.getenv("LOCALAPPDATA")
    if not local:
        logger("  未找到 LOCALAPPDATA。")
        return
    path = os.path.join(local, "D3DSCache")
    logger(f"  清理 DX Shader Cache：{path}")
    try:
        shutil.rmtree(path)
    except Exception:
        pass


# --------------------------
#  NVIDIA Shader Cache
# --------------------------
def clean_nvidia_shader_cache(logger: Logger):
    path = r"C:\ProgramData\NVIDIA Corporation\NV_Cache"
    logger(f"  清理 NVIDIA Shader Cache：{path}")
    try:
        shutil.rmtree(path)
    except Exception:
        pass


# --------------------------
#  Windows 更新缓存
# --------------------------
def clean_windows_update_cache(logger: Logger):
    path = r"C:\Windows\SoftwareDistribution\Download"
    logger(f"  清理 Windows 更新缓存：{path}")
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    os.remove(fp)
                except Exception:
                    pass
    else:
        logger("  缓存目录不存在。")


# --------------------------
#  Recent 清理
# --------------------------
def clean_recent(logger: Logger):
    user = os.getenv("USERPROFILE")
    if not user:
        return
    path = os.path.join(user, r"AppData\Roaming\Microsoft\Windows\Recent")
    logger(f"  清理 Recent：{path}")
    if os.path.isdir(path):
        for f in os.listdir(path):
            try:
                os.remove(os.path.join(path, f))
            except Exception:
                pass


# --------------------------
#  刷新 GPU IdleTasks（带异常吞掉）
# --------------------------
def refresh_gpu_idle_tasks(logger: Logger):
    logger("  刷新 GPU IdleTasks（ProcessIdleTasks）")
    try:
        subprocess.run(
            ["rundll32.exe", "advapi32.dll,ProcessIdleTasks"],
            check=True
        )
    except Exception:
        logger("  GPU IdleTasks 执行异常（已忽略）。")


# --------------------------
#  刷新 DWM
# --------------------------
def refresh_dwm(logger: Logger):
    logger("警告：刷新 DWM 会导致 Wallpaper Engine 暂时异常。")
    logger("刷新 DWM（可能会瞬间黑屏）")
    try:
        _run_simple_command(["taskkill", "/IM", "dwm.exe", "/F"], logger)
    except Exception:
        logger("  刷新 DWM 失败（权限或系统限制）。")
