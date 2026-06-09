import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout,
    QLabel, QMessageBox,QGroupBox,QLineEdit,QRadioButton
)
from PySide6.QtGui import QAction, QKeySequence,QDoubleValidator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("完整菜单验证")
        self.resize(400, 300)

        central=QWidget()
        
        main=QVBoxLayout()

        #   防腐层参数
        c_coat=QGroupBox("防腐层参数")
        c_coat_layout=QHBoxLayout()
        rg_value=QHBoxLayout()
        rg_value.addWidget(QLabel("Rg值（kΩ·m²）"))
        self.rg_input=QLineEdit()
        self.rg_input.setValidator(QDoubleValidator(0.1, 10000.0, 0))  # 设置输入范围和小数位数
        self.rg_input.setPlaceholderText("请输入0.1-10000的数值")
        rg_value.addWidget(self.rg_input)
        # rg_value.addWidget(QLabel("kΩ·m²"))
        c_coat_layout.addLayout(rg_value)

        y_value=QHBoxLayout()
        y_value.addWidget(QLabel("Y值（dB/m）"))
        self.y_input=QLineEdit()
        self.y_input.setValidator(QDoubleValidator(0.001, 0.5, 3))  # 设置输入范围和小数位数
        self.y_input.setPlaceholderText("请输入0.001-0.5的数值")
        y_value.addWidget(self.y_input)
        # y_value.addWidget(QLabel("dB/m"))
        c_coat_layout.addLayout(y_value)
        
        p_value=QHBoxLayout()
        p_value.addWidget(QLabel("P值（处/100m）"))
        self.p_input=QLineEdit()
        self.p_input.setValidator(QDoubleValidator(0.1, 5.0, 1))  # 设置输入范围和小数位数
        self.p_input.setPlaceholderText("请输入0.1-5.0的数值")
        p_value.addWidget(self.p_input)
        # p_value.addWidget(QLabel("处/100m"))
        c_coat_layout.addLayout(p_value)

        c_coat.setLayout(c_coat_layout)

        #   阴极保护
        cp=QGroupBox("阴极保护参数")
        cp_value=QHBoxLayout()
        cp_value.addWidget(QLabel("保护率（%）"))
        self.cp_input=QLineEdit()
        self.cp_input.setValidator(QDoubleValidator(0.1, 100.0, 1))  # 设置输入范围和小数位数
        self.cp_input.setPlaceholderText("请输入0.1-100.0的数值")
        cp_value.addWidget(self.cp_input)
        # cp_value.addWidget(QLabel("%"))
        cp.setLayout(cp_value)

        #   土壤腐蚀性
        soil_corrosion=QGroupBox("土壤腐蚀性")
        soil_layout=QHBoxLayout()
        soil_layout.addWidget(QLabel("土壤腐蚀性N值"))
        self.soil_input=QLineEdit()
        self.soil_input.setValidator(QDoubleValidator(0.1, 35.0, 1))  # 设置输入范围和小数位数
        self.soil_input.setPlaceholderText("请输入0.1-35.0的数值")
        soil_layout.addWidget(self.soil_input)
        soil_corrosion.setLayout(soil_layout)

        #   杂散电流干扰
        stray_current=QGroupBox("杂散电流干扰")
        stray_layout=QHBoxLayout()
        stray_layout.addWidget(QLabel("电位正于阴保要求的占比%"))
        self.stray_input=QLineEdit()
        self.stray_input.setValidator(QDoubleValidator(0.1, 100.0, 1))  # 设置输入范围和小数位数
        self.stray_input.setPlaceholderText("请输入0.1-100.0的数值")
        stray_layout.addWidget(self.stray_input)
        stray_current.setLayout(stray_layout)

        #   排流效果
        drainage=QGroupBox("排流效果")
        drainage_layout=QHBoxLayout()
        drainage_layout.addWidget(QLabel("排流效果评价（仅当杂散电流干扰评价为弱以上时进行）"))
        self.drainage=QRadioButton("有效")
        self.drainage_0=QRadioButton("无效")
        drainage_layout.addWidget(self.drainage)
        drainage_layout.addWidget(self.drainage_0)
        drainage.setLayout(drainage_layout)

        main.addWidget(c_coat)
        main.addWidget(cp)
        main.addWidget(soil_corrosion)
        main.addWidget(stray_current)
        main.addWidget(drainage)
        central.setLayout(main)
        self.setCentralWidget(central)
        
        menubar = self.menuBar()
        
        # --- 文件菜单 ---
        file_menu = menubar.addMenu("文件(&F)")  # &F 表示 Alt+F 快捷键
        
        # 新建：带图标、快捷键、状态栏提示
        action_new = QAction("新建(&N)", self)
        action_new.setShortcut(QKeySequence("Ctrl+N"))  # 快捷键
        action_new.setStatusTip("创建新文件")            # 状态栏提示
        action_new.triggered.connect(self.on_new)
        file_menu.addAction(action_new)
        
        file_menu.addSeparator()
        
        # 退出
        action_exit = QAction("退出(&Q)", self)
        action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # --- 编辑菜单（带子菜单） ---
        edit_menu = menubar.addMenu("编辑(&E)")
        
        # 子菜单：格式
        format_menu = edit_menu.addMenu("格式")  # 注意是 addMenu，不是 addAction
        format_menu.addAction("字体")
        format_menu.addAction("颜色")
        
        edit_menu.addSeparator()
        edit_menu.addAction("撤销")
        
        # 状态栏
        self.statusBar().showMessage("就绪")

    def on_new(self):
        self.label.setText("Ctrl+N 或 菜单→新建 被触发")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())