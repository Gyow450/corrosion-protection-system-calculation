from PySide6.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QComboBox, QDoubleSpinBox,
    QDialogButtonBox
)
from core.models import AppConfig


class AdvancedDialog(QDialog):
    """高级参数模态对话框"""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级参数")
        self.setModal(True)
        self.resize(300, 180)

        # --- 控件 ---
        self.precision_spin = QSpinBox()
        self.precision_spin.setRange(0, 10)
        self.precision_spin.setValue(config.precision)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["SI", "Imperial"])
        self.unit_combo.setCurrentText(config.unit_system)

        self.correction_spin = QDoubleSpinBox()
        self.correction_spin.setRange(0.0001, 100.0)
        self.correction_spin.setDecimals(4)
        self.correction_spin.setValue(config.correction_factor)

        # --- 按钮 ---
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        # --- 布局 ---
        layout = QFormLayout(self)
        layout.addRow("小数精度:", self.precision_spin)
        layout.addRow("单位制:", self.unit_combo)
        layout.addRow("修正系数:", self.correction_spin)
        layout.addRow(btn_box)

    def get_config(self) -> AppConfig:
        """对话框关闭后，主窗口调用此方法取回结果"""
        return AppConfig(
            precision=self.precision_spin.value(),
            unit_system=self.unit_combo.currentText(),
            correction_factor=self.correction_spin.value()
        )
