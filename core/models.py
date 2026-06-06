from dataclasses import dataclass, field
from typing import List

@dataclass
class AppConfig:
    """需要持久化的高级参数"""
    precision: int = 4
    unit_system: str = "SI"
    correction_factor: float = 1.0

@dataclass
class InputPayload:
    """主界面表单数据"""
    mass: float = 0.0
    velocity: float = 0.0
    mode: str = "动能"

@dataclass
class ResultPayload:
    """计算结果"""
    text_summary: str = ""
    latex_items: List[str] = field(default_factory=list)
    html_details: str = ""
