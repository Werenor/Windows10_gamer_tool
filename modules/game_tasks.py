# modules/game_tasks.py
import subprocess
import winreg
from typing import Callable
import os


Logger = Callable[[str], None]


def _run_simple_command(cmd: list, logger: Logger):
    try:
        logger(f"  执行命令：{' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger(f"  命令执行失败：{e}")
        raise


# ------------------------
# A. 禁用不必要的 UWP 后台
# ------------------------
def disable_uwp_background(logger: Logger):
    logger("  禁用 UWP 应用后台活动...")

    paths = [
        r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
        r"Software\Microsoft\Windows\CurrentVersion\Search",
        r"Software\Microsoft\Windows\CurrentVersion\Search\BackgroundAccess",
    ]

    try:
        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "Disabled", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                logger(f"    已设置 Disabled=1: {path}")
            except FileNotFoundError:
                logger(f"    路径不存在（跳过）: {path}")

        logger("  UWP 后台已禁用（可逆操作）。")

    except Exception as e:
        logger(f"  禁用 UWP 后台失败：{e}")

def enable_game_mode(logger: Logger):
    logger("  正在启用 GameMode...")

    path = r"Software\Microsoft\GameBar"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)

    winreg.SetValueEx(key, "GameModeEnabled", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

    logger("  GameMode 已开启。")


def clean_game_shader_cache(logger: Logger):
    """
    清理 Steam / WeGame Shader Cache
    """
    logger("  开始清理游戏 Shader / Cache 文件...")

    local = os.getenv("LOCALAPPDATA")
    prog86 = os.getenv("ProgramFiles(x86)")

    targets = [
        # Steam
        os.path.join(local, "Steam", "htmlcache"),
        os.path.join(local, "Steam", "shadercache"),
        os.path.join(prog86 or "", "Steam", "steamapps", "shadercache"),

        # WeGame
        os.path.join(local, "Tencent", "WeGameAppsCache"),
        os.path.join(local, "Tencent", "WeGame", "ui_cache"),
        os.path.join(local, "Tencent", "WeGame", "cache"),
    ]

    import shutil

    for path in targets:
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                logger(f"    已删除：{path}")
            except Exception as e:
                logger(f"    删除失败：{path} | {e}")
        else:
            logger(f"    路径不存在（跳过）：{path}")

    logger("  游戏 Cache 清理完成。")

def set_high_performance_plan(logger: Logger):
    """
    切换到“高性能”电源计划。

    使用内置 GUID：
        8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c  → Windows 默认高性能电源方案

    说明：
    - 需要管理员权限；
    - 若 OEM 修改或禁用了该方案，命令可能失败，会在日志中提示。
    """
    high_perf_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    logger("  正在切换到高性能电源计划…")

    try:
        _run_simple_command(
            ["powercfg", "/setactive", high_perf_guid],
            logger
        )
        logger("  已尝试切换到高性能电源计划（如命令无报错，则切换成功）。")
    except Exception as e:
        logger(f"  切换高性能电源计划失败：{e}\n"
               "  可能原因：\n"
               "    - 当前系统策略不允许修改电源计划；\n"
               "    - 该电源方案被 OEM 禁用或移除；\n"
               "    - 未以管理员身份运行。")

def set_balanced_plan(logger: Logger):
    """
    切换到“平衡（Balanced）”电源计划。

    使用内置 GUID：
        381b4222-f694-41f0-9685-ff5bb260df2e  → Windows 默认平衡电源方案
    """
    balanced_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
    logger("  正在切换到平衡电源计划…")

    try:
        _run_simple_command(
            ["powercfg", "/setactive", balanced_guid],
            logger
        )
        logger("  已尝试切换到平衡电源计划（如命令无报错，则切换成功）。")
    except Exception as e:
        logger(f"  切换平衡电源计划失败：{e}\n"
               "  可能原因：\n"
               "    - 当前系统策略不允许修改电源计划；\n"
               "    - 该电源方案被 OEM 禁用或移除；\n"
               "    - 未以管理员身份运行。")

def set_power_saver_plan(logger: Logger):
    """
    切换到“节能（Power Saver）”电源计划。

    使用内置 GUID：
        a1841308-3541-4fab-bc81-f71556f20b4a  → Windows 节能模式
    """
    saver_guid = "a1841308-3541-4fab-bc81-f71556f20b4a"
    logger("  正在切换到节能电源计划（Power Saver）…")

    try:
        _run_simple_command(
            ["powercfg", "/setactive", saver_guid],
            logger
        )
        logger("  已尝试切换到节能模式（如命令无报错，则切换成功）。")
    except Exception as e:
        logger(f"  切换节能电源计划失败：{e}\n"
               "  可能原因：\n"
               "    - 当前系统策略不允许修改电源计划；\n"
               "    - 该电源方案被 OEM 禁用或移除；\n"
               "    - 未以管理员身份运行。")
