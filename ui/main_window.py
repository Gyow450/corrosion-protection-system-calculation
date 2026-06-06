from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QDoubleSpinBox, QComboBox, QTextEdit,
    QGroupBox, QApplication
)
from PySide6.QtCore import Qt, QSettings

from core.models import AppConfig, InputPayload
from core.calculator import Calculator
from ui.dialogs import AdvancedDialog
from ui.latex_renderer import latex_to_pixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("物理计算骨架")
        self.resize(650, 550)

        # --- 配置与持久化 ---
        self.settings = QSettings("DemoOrg", "PhysicsCalc")
        self.config = AppConfig()
        self._load_config()

        # --- 中央部件 ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ===== 输入区 =====
        input_group = QGroupBox("输入参数")
        form_layout = QFormLayout()

        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0, 1_000_000)
        self.mass_input.setDecimals(2)
        self.mass_input.setSuffix(" kg")

        self.velocity_input = QDoubleSpinBox()
        self.velocity_input.setRange(0, 1_000_000)
        self.velocity_input.setDecimals(2)
        self.velocity_input.setSuffix(" m/s")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["动能", "动量"])

        form_layout.addRow("质量:", self.mass_input)
        form_layout.addRow("速度:", self.velocity_input)
        form_layout.addRow("计算模式:", self.mode_combo)
        input_group.setLayout(form_layout)

        # ===== 按钮行 =====
        btn_layout = QHBoxLayout()
        self.adv_btn = QPushButton("高级参数...")
        self.adv_btn.setToolTip("修改小数精度、修正系数等")
        self.adv_btn.clicked.connect(self._open_advanced_dialog)

        self.calc_btn = QPushButton("  开始计算  ")
        self.calc_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.calc_btn.clicked.connect(self._on_calculate)

        btn_layout.addWidget(self.adv_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.calc_btn)

        # ===== 结果区 =====
        self.summary_label = QLabel("点击“开始计算”查看结果")
        self.summary_label.setStyleSheet("font-size: 15px; color: #333;")
        self.summary_label.setWordWrap(True)

        # 公式画廊：横向排列 QLabel(图片)
        self.formula_container = QWidget()
        self.formula_layout = QHBoxLayout(self.formula_container)
        self.formula_layout.setAlignment(Qt.AlignLeft)
        self.formula_layout.setSpacing(16)

        # HTML 详情
        self.details_edit = QTextEdit()
        self.details_edit.setReadOnly(True)
        self.details_edit.setMaximumHeight(140)
        self.details_edit.setStyleSheet("background-color: #F5F5F5; border-radius: 4px;")

        # --- 组装 ---
        main_layout.addWidget(input_group)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(QLabel("<b>结果摘要:</b>"))
        main_layout.addWidget(self.summary_label)
        main_layout.addWidget(QLabel("<b>公式渲染:</b>"))
        main_layout.addWidget(self.formula_container)
        main_layout.addWidget(QLabel("<b>详细数据:</b>"))
        main_layout.addWidget(self.details_edit)

        # --- 恢复上次输入 ---
        self._restore_inputs()

    # ---------- 事件处理 ----------

    def _open_advanced_dialog(self):
        dialog = AdvancedDialog(self.config, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            self._save_config()

    def _on_calculate(self):
        # 1. 收集输入
        payload = InputPayload(
            mass=self.mass_input.value(),
            velocity=self.velocity_input.value(),
            mode=self.mode_combo.currentText()
        )

        # 2. 同步计算（无线程，直接调用）
        result = Calculator.compute(payload, self.config)

        # 3. 刷新界面
        self.summary_label.setText(result.text_summary)
        self._render_formulas(result.latex_items)
        self.details_edit.setHtml(result.html_details)

        # 4. 保存输入（供下次启动恢复）
        self._save_inputs()

    def _render_formulas(self, latex_list):
        """动态生成 QLabel 图片，替换旧内容"""
        # 清空旧控件
        while self.formula_layout.count():
            item = self.formula_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for latex_str in latex_list:
            try:
                pixmap = latex_to_pixmap(latex_str, fontsize=16)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setStyleSheet("background: white; padding: 4px;")
                self.formula_layout.addWidget(label)
            except Exception as e:
                # 渲染失败时回退为纯文本
                fallback = QLabel(f"[公式渲染失败] {latex_str}")
                fallback.setStyleSheet("color: red;")
                self.formula_layout.addWidget(fallback)

        self.formula_layout.addStretch()

    # ---------- 持久化 ----------

    def _save_config(self):
        self.settings.setValue("config/precision", self.config.precision)
        self.settings.setValue("config/unit", self.config.unit_system)
        self.settings.setValue("config/correction", self.config.correction_factor)

    def _load_config(self):
        self.config.precision = int(self.settings.value("config/precision", 4))
        self.config.unit_system = self.settings.value("config/unit", "SI")
        self.config.correction_factor = float(self.settings.value("config/correction", 1.0))

    def _save_inputs(self):
        self.settings.setValue("input/mass", self.mass_input.value())
        self.settings.setValue("input/velocity", self.velocity_input.value())
        self.settings.setValue("input/mode", self.mode_combo.currentText())

    def _restore_inputs(self):
        self.mass_input.setValue(float(self.settings.value("input/mass", 10.0)))
        self.velocity_input.setValue(float(self.settings.value("input/velocity", 5.0)))
        self.mode_combo.setCurrentText(self.settings.value("input/mode", "动能"))
