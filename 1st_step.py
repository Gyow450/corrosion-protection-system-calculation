import sys
import numpy as np
from scipy.interpolate import make_interp_spline, CubicSpline
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout,
    QLabel, QMessageBox,QGroupBox,QLineEdit,QRadioButton,QPushButton
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
        self.coat=QRadioButton("PE防腐层")
        self.coat_0=QRadioButton("沥青防腐层")
        c_coat_layout.addWidget(self.coat)
        c_coat_layout.addWidget(self.coat_0)
        rg_value.addWidget(QLabel("管径（mm）"))
        self.d_input=QLineEdit()
        self.d_input.setValidator(QDoubleValidator(25.0, 10000.0, 0))  # 设置输入范围和小数位数
        self.d_input.setPlaceholderText("请输入25-10000的数值")
        rg_value.addWidget(self.d_input)
        rg_value.addWidget(QLabel("Rg值（kΩ·m²）"))
        self.rg_input=QLineEdit()
        self.rg_input.setValidator(QDoubleValidator(0.1, 10000.0, 2))  # 设置输入范围和小数位数
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
        self.cp=QRadioButton("有阴极保护")
        self.cp_0=QRadioButton("未实施阴极保护")
        stray_layout.addWidget(self.cp)
        stray_layout.addWidget(self.cp_0)
        stray_layout.addWidget(QLabel("动态直流干扰-电位正于阴保要求的占比%"))
        self.stray_input=QLineEdit()
        self.stray_input.setValidator(QDoubleValidator(0.1, 100.0, 1))  # 设置输入范围和小数位数
        self.stray_input.setPlaceholderText("请输入0.1-100.0的数值")
        stray_layout.addWidget(self.stray_input)
        stray_layout.addWidget(QLabel("交流电流密度（A/m²）"))
        self.ac_input=QLineEdit()
        self.ac_input.setValidator(QDoubleValidator(0, 1000, 2))  # 设置输入范围和小数位数
        self.ac_input.setPlaceholderText("请输入0-1000的数值")
        stray_layout.addWidget(self.ac_input)
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

        #   控制按钮
        calculate_btn=QPushButton("计算")
        calculate_btn.clicked.connect(self.on_calculate)

        main.addWidget(c_coat)
        main.addWidget(cp)
        main.addWidget(soil_corrosion)
        main.addWidget(stray_current)
        main.addWidget(drainage)
        main.addWidget(calculate_btn)
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

    @staticmethod
    def _vertical_calculate(x:float|int,v:np.ndarray,reverse:bool=False)->np.ndarray:
        """计算隶属向量"""
        mu:np.ndarray=np.array([0.0,0.0,0.0,0.0])
        u:np.ndarray=np.array([
            (v[0]+v[1])/2,
            (v[1]+v[2])/2,
        ])
      
        if x<=v[0]:
            mu[0]=1
        elif x<=u[0] and x>v[0]:
            mu[0]=(x-u[0])/(v[0]-u[0])
        else:
            mu[0]=0

        if x>=v[0] and x<=u[0]:
            mu[1]=(x-v[0])/(u[0]-v[0])
        elif u[0]<x and x<=u[1]:
            mu[1]=(x-u[1])/(u[0]-u[1])
        else:
            mu[1]=0

        if u[0]<=x and x<=u[1]:
            mu[2]=(x-u[0])/(u[1]-u[0])
        elif u[1]<x and x<=v[2]:
            mu[2]=(x-v[2])/(u[1]-v[2])
        else:
            mu[2]=0

        if u[1]<=x and x<=v[2]:
            mu[3]=(x-u[1])/(v[2]-u[1])
        elif x>v[2]:
            mu[3]=1
        else:
            mu[3]=0
        if reverse==True:
            mu=np.flip(mu)
        return mu
    
    @staticmethod
    def _compare(*vs:np.ndarray)->np.ndarray:
        """比较隶属向量，返回最小值"""
        min_v:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        for v in vs:
            for i in range(4):
                if v[i]<min_v[i]:
                    min_v=v
                    break 
        return min_v
    
    def on_calculate(self):
        # coating_rg:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        # coating_y:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        # coating_p:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        if self.coat.isChecked() :
            coating_rg=MainWindow._vertical_calculate(float(self.rg_input.text()),np.array([5,20,100]),True) if self.rg_input.text() else np.array([1.0,0.0,0.0,0.0])
            coating_p=MainWindow._vertical_calculate(float(self.p_input.text()),np.array([0.1,0.5,1.0])) if self.p_input.text() else np.array([1.0,0.0,0.0,0.0])
        else:
            coating_rg=MainWindow._vertical_calculate(float(self.rg_input.text()),np.array([2,5,10]),True) if self.rg_input.text() else np.array([1.0,0.0,0.0,0.0])
            coating_p=MainWindow._vertical_calculate(float(self.p_input.text()),np.array([0.2,1.0,2.0])) if self.p_input.text() else np.array([1.0,0.0,0.0,0.0])
        
        v_coat=MainWindow._compare(coating_rg,coating_p)
        v_w=np.array([0.402,0.269,0.099,0.066,0.163])
        r_matrix=np.array(
            [
                
            ]
        )
        QMessageBox.information(self, "计算", "计算功能尚未实现")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())