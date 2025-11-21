# 🎮 Windows10 Gamer Tool

一个轻量、实用、无广告的 **Windows 系统优化 & 故障诊断工具**。
适合游戏玩家、普通用户，以及希望快速排查系统问题的人群。

本工具基于 **Python + Tkinter** 开发，并提供 **Windows 单文件 .exe 版本**，开箱即用。

---

## ✨ 功能特性

### 🧹 **系统优化工具**

* 清理临时文件（Temp）
* 清理 Prefetch 和 Shader Cache（DirectX / NVIDIA）
* 清理最近使用记录（Recent）
* 清理 Windows 更新缓存（SoftwareDistribution）

---

### 🌐 **网络优化工具**

* DNS 缓存刷新（`ipconfig /flushdns`）
* Winsock 重置（`netsh winsock reset`）
* TCP/IP 轻量重置（`netsh int ip reset`）
* DNS 配置面板（可自定义、支持公共 DNS）

---

### 🎨 **GPU / 显示优化**

* 刷新 DWM（显示管理器，会短暂黑屏）
* 刷新 GPU IdleTasks（NVIDIA/AMD 常用操作，不稳定设备可能无反应）

---

### 🔋 **电源模式一键切换**

* 性能模式（高性能）
* 平衡模式
* 节能模式

---

### 🔧 **高级功能**

* 深度干净重启（相当于 `shutdown /g`，可解决大量系统性问题）
* 以管理员权限重新启动本程序
* 一键打开任务管理器
* 系统信息查看

---

### 🩺 **HID / USB 设备故障诊断系统**

自动扫描以下日志并生成可读报告：

* Windows 日志（System.evtx）
* 驱动安装日志（setupapi.dev.log）
* 设备相关错误（EventID 51 / 7000 / 7001 / 7034 等）
* WER 系统错误报告
* LiveKernelReports 内核错误报告（如果存在）

可用于排查：

* 键盘/鼠标突然失效
* USB 断连
* 驱动加载失败
* 游戏导致外设异常（Steam Workshop MOD 等情况）

---

## 📦 下载

👉 前往 Releases 页面下载最新版：
**[https://github.com/Werenor/Windows10_gamer_tool/releases](https://github.com/Werenor/Windows10_gamer_tool/releases)**

下载 `GamerTool.exe` 即可使用，无需安装。

---

## ⚠️ 使用须知

* 本工具不会对系统进行危险写入操作，但某些功能（Winsock、TCP/IP）会导致网络暂时断开。
* “刷新 DWM” 会造成 **0.1 秒黑屏**，并可能导致 **Wallpaper Engine 短暂异常**（重启后恢复）。
* “深度干净重启” 会 **立即重启电脑**，请保存好您的工作。

---

## 🛠️ 开发环境

* Python 3.10+
* Tkinter（内置）
* PyInstaller（用于打包）
* 仅依赖标准库，无第三方包

项目结构：

```
Windows10_gamer_tool/
│── app/
│── modules/
│── ui/
│── main.py
│── GamerTool.spec
│── .gitignore
```

---

## 🤝 贡献方式

欢迎提交：

* Bug report
* 功能建议
* PR（欢迎！）

---

## 📄 License

MIT License
可自由用于个人/商业项目。
