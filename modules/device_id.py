# modules/device_id.py
"""
VID/PID 自动识别模块
可根据 USB\VID_xxxx&PID_xxxx 返回设备制造商名称与可能的设备类型。
"""

import re

# 常见 USB 设备 VID 对照表（部分示例）
VID_DATABASE = {
    "046D": "Logitech",
    "1B1C": "Corsair",
    "1532": "Razer",
    "0930": "Toshiba",
    "0955": "NVIDIA",
    "8086": "Intel",
    "045E": "Microsoft",
    "054C": "Sony",
    "04E8": "Samsung",
    "1987": "Eluktronics (产线 USB 控制器)",
    "174C": "ASMedia USB 控制器",
    "0B05": "ASUS",
    "04F2": "Chicony",
    "0A5C": "Broadcom",
    "13D3": "AzureWave",
    "0C45": "Microdia",
    "0BB4": "HTC",
    "05AC": "Apple",
    "12D1": "Huawei",
    "0FCE": "Sony Mobile",
    "0489": "Foxconn",
    "05E3": "Genesys Logic (USB Hub)",
    "1A86": "Qinheng（常见 USB 串口）",
}

# 根据常见 PID 简单识别类型（可选）
PID_HINTS = {
    "C33F": "Logitech Receiver / 键鼠无线接收器",
    "C077": "Logitech 鼠标",
    "00B4": "Logitech 键盘",
    "9000": "NVIDIA Virtual Audio 或 USB 接口",
    "6001": "CH340 串口设备",
    "6000": "USB Hub / 控制器",
}


USB_ID_REGEX = re.compile(r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})")


def resolve_vid_pid(dev_line: str):
    """
    解析行文本，返回： (厂商名称, 可能的设备名)
    若无法识别，返回 ("Unknown Vendor", None)
    """

    match = USB_ID_REGEX.search(dev_line)
    if not match:
        return "Unknown Vendor", None

    vid, pid = match.group(1).upper(), match.group(2).upper()

    vendor = VID_DATABASE.get(vid, f"Unknown Vendor ({vid})")
    hint = PID_HINTS.get(pid, None)

    return vendor, hint


if __name__ == "__main__":
    # 测试
    s = r"Device USB\VID_046D&PID_C33F was removed unexpectedly"
    print(resolve_vid_pid(s))
