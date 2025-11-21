import subprocess
from typing import Callable

Logger = Callable[[str], None]


def _run_simple(cmd: list, logger: Logger):
    try:
        logger(f"  执行命令：{' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            logger("  命令返回 1：系统当前状态无需修复（非真正错误）")
            return
        logger(f"  命令执行错误码：{e.returncode}")
        raise

# --------------------------
#  刷新 DNS 缓存
# --------------------------
def flush_dns(logger: Logger):
    logger("  刷新 DNS 缓存（ipconfig /flushdns）")
    _run_simple(["ipconfig", "/flushdns"], logger)


# --------------------------
#  重置 Winsock
# --------------------------
def winsock_reset(logger: Logger):
    logger("  重置 Winsock（netsh winsock reset）")
    _run_simple(["netsh", "winsock", "reset"], logger)


# --------------------------
#  轻量重置 TCP/IP
# --------------------------
def tcpip_reset(logger: Logger):
    logger("  轻量重置 TCP/IP（netsh int ip reset）")
    _run_simple(["netsh", "int", "ip", "reset"], logger)


# --------------------------
#  设置 DNS
# --------------------------
def set_dns(logger: Logger, ip: str):
    logger(f"  设置 DNS：{ip}")
    _run_simple(["netsh", "interface", "ip", "set", "dns", "name=Wi-Fi", f"static", ip], logger)
