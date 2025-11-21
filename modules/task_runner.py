# modules/task_runner.py
import enum
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
from tkinter import messagebox


class TaskLevel(enum.Enum):
    LEVEL1 = 1  # 安全任务
    LEVEL2 = 2  # 执行时不建议操作电脑，会短暂掉线/黑屏
    LEVEL3 = 3  # 执行后会立刻重启


# 执行函数不带参数，内部自己调用 logger
TaskFunc = Callable[[], None]


@dataclass
class TaskDef:
    key: str                 # 唯一标识
    label: str               # UI 显示名称
    level: TaskLevel         # 任务等级
    func: TaskFunc           # 实际执行函数
    description: str = ""    # 详细描述（可选）
    warn: str = ""           # 特殊警告（可选，用于 UI 或日志）
    is_dns_task: bool = False  # 是否是 DNS 相关任务（用于额外提示）


class TaskRunner:
    """
    负责：
    - 收集用户勾选的任务
    - 按 L1 -> L2 -> L3 顺序执行
    - 弹提示确认框
    - 记录日志
    """

    def __init__(self, logger: Callable[[str], None], tk_root):
        self.logger = logger
        self.root = tk_root

    def run_selected_tasks(
        self,
        all_task_map: Dict[str, Tuple[TaskDef, "bool"]],  # key -> (TaskDef, bool_selected)
    ):
        # 收集勾选任务
        selected: List[TaskDef] = [
            task for key, (task, selected) in all_task_map.items() if selected
        ]

        if not selected:
            messagebox.showinfo("提示", "你还没有勾选任何任务。", parent=self.root)
            return

        # 分类
        l1 = [t for t in selected if t.level == TaskLevel.LEVEL1]
        l2 = [t for t in selected if t.level == TaskLevel.LEVEL2]
        l3 = [t for t in selected if t.level == TaskLevel.LEVEL3]

        # 先看有没有 L2
        if l2:
            has_dns = any(t.is_dns_task for t in l2)
            msg_lines = ["将要执行一些需要谨慎的任务："]
            if has_dns:
                msg_lines.append("- 部分操作会通过 netsh 修改 DNS，会导致短暂掉线；")
            msg_lines.append("- 执行期间不建议你操作电脑。")
            msg_lines.append("")
            msg_lines.append("确定现在要执行吗？")

            if not messagebox.askyesno("确认执行", "\n".join(msg_lines), parent=self.root):
                self.logger("用户取消：含 LEVEL2 任务的执行。")
                return

        # 再看有没有 L3
        if l3:
            msg = (
                "你勾选了会触发『立刻重启』的任务（LEVEL3）。\n"
                "这些任务会在所有其它任务执行完之后立即重启电脑。\n\n"
                "请确认：\n"
                "1. 你已经保存了所有重要文件；\n"
                "2. 重启发生在本次执行的最后。\n\n"
                "是否继续？"
            )
            if not messagebox.askyesno("即将重启", msg, parent=self.root):
                self.logger("用户取消：含 LEVEL3 任务的执行。")
                return

        # 真正开始执行
        self.logger("========== 开始执行勾选任务 ==========")
        self._run_task_group("LEVEL1 安全任务", l1)
        self._run_task_group("LEVEL2 谨慎任务", l2)
        self._run_task_group("LEVEL3 重启任务", l3)
        self.logger("========== 所有任务执行结束（如包含重启任务则系统会重启） ==========")

    def _run_task_group(self, title: str, tasks: List[TaskDef]):
        if not tasks:
            return
        self.logger(f"[{title}] 共 {len(tasks)} 个任务。")
        for t in tasks:
            self._run_single_task(t)

    def _run_single_task(self, task: TaskDef):
        self.logger(f"→ 开始：{task.label}")
        if task.warn:
            self.logger(f"  注意：{task.warn}")
        try:
            task.func()
            self.logger(f"√ 完成：{task.label}")
        except Exception as e:
            self.logger(f"× 失败：{task.label} | 错误：{e}")

