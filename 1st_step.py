import sys,json
import numpy as np
import pandas as pd
from scipy.interpolate import  CubicSpline
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
        stray_layout.addWidget(QLabel("动态直流干扰-电位正于阴保要求（或正于自然电位20mV）的占比%"))
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
    def _vertical_calculate(x:float|int,v:np.ndarray|list[float|int],reverse:bool=False)->np.ndarray:
        """计算隶属向量,越大越安全的参数需最后反转"""
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
                elif v[i]>min_v[i]:
                    break
        return min_v
    
    @staticmethod
    def _interpolate(y:pd.Series,x:np.ndarray|list,x_new:float)->float:
        """插值计算"""
        # 创建三次样条插值对象
        cs = CubicSpline(np.array(x), y.to_numpy())
        # 计算新的y值
        y_new = cs(x_new)
        return y_new

    def on_calculate(self):
        # coating_rg:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        # coating_y:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        # coating_p:np.ndarray=np.array([1.0,0.0,0.0,0.0])
        with open("19285-2026.json",encoding="UTF-8") as f:
            data=json.load(f)

        #   防腐层隶属向量计算
        d=float(self.d_input.text()) if self.d_input.text() else 0.0
        y_input=float(self.y_input.text()) if self.y_input.text() else 1.0
        p_input=float(self.p_input.text()) if self.p_input.text() else 3.0
        rg_input=float(self.rg_input.text()) if self.rg_input.text() else 0.0
        c_type="PE防腐层" if self.coat.isChecked() else "沥青防腐层"
        coating_rg=MainWindow._vertical_calculate(rg_input,data[f"{c_type}Rg值区间"],True) 
        coating_p=MainWindow._vertical_calculate(p_input,data[f"{c_type}P值区间"])
        
        df=pd.DataFrame(data[f"{c_type}Y值区间"])
        col=df.columns.to_list()
        d_x=[float(t) for t in col]

        if d<=min(d_x):
            coating_y=MainWindow._vertical_calculate(y_input,data[f"{c_type}Y值区间"][str(int(min(d_x)))]) 
        elif d>=max(d_x):
            coating_y=MainWindow._vertical_calculate(y_input,data[f"{c_type}Y值区间"][str(int(max(d_x)))]) 
        else:
            df["inter"]=df.apply(MainWindow._interpolate,axis=1,x=d_x,x_new=d)
            coating_y=MainWindow._vertical_calculate(y_input,df["inter"]) 

        v_coat=MainWindow._compare(coating_rg,coating_p,coating_y)
        
        #   阴极保护隶属向量计算
        cp_input=0.01*float(self.cp_input.text())
        v_cp=MainWindow._vertical_calculate(cp_input,data["阴极保护区间"],True)
        
        #   土壤腐蚀性隶属向量计算
        soil_input=float(self.soil_input.text())
        v_soil=MainWindow._vertical_calculate(soil_input,data["土壤腐蚀性区间"])

        #   杂散电流隶属向量计算
        cp_exist='有阴保' if self.cp.isChecked else '无阴保'
        stray_input=0.01*float(self.stray_input.text()) if self.stray_input.text() else 1.0
        stray_input_ac=float(self.ac_input.text()) if self.ac_input.text() else 200
        v_dc=MainWindow._vertical_calculate(stray_input,data[f"直流干扰区间-{cp_exist}"])
        v_ac=MainWindow._vertical_calculate(stray_input_ac,data["交流干扰区间"])
        v_stray=MainWindow._compare(v_dc,v_ac)

        #   排流隶属向量
        v_dra = np.array([1.0,0.0,0.0,0.0] if self.drainage.isChecked() else [0.0,0.0,0.0,1.0]) 

        v_w=np.array([0.402,0.269,0.099,0.066,0.163])
        R_matrix=np.array(
            [
                v_coat,
                v_cp,
                v_soil,
                v_stray,
                v_dra
            ]
        )
        v_a=v_w@R_matrix
        c_h=np.array([100,89,79,69])
        c_m=np.array([95,85,75,65])
        c_l=np.array([90,80,70,60])
        s_h=np.sum(v_a*c_h)/np.sum(v_a)
        s_m=np.sum(v_a*c_m)/np.sum(v_a)
        s_l=np.sum(v_a*c_l)/np.sum(v_a)
        s_=(s_h+s_m+s_l)/3.00
        QMessageBox.information(self, "计算结果", f"评价得分为{s_:.2f}")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())