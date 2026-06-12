import sys,json
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from dataclasses import dataclass,asdict
from scipy.interpolate import  CubicSpline
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout,QDialog,QTableWidget,QTableWidgetItem,
    QLabel, QMessageBox,QGroupBox,QLineEdit,QRadioButton,QPushButton,QTextEdit
)
from PySide6.QtGui import QAction, QKeySequence,QDoubleValidator
from PySide6.QtCore import Qt

@dataclass
class CPSC_Data:
    pip_d:float|None
    c_type:str|None
    c_rg:float|None
    c_p:float|None
    c_y:float|None
    cp_exist:str|None
    cp_value:float|None
    soil_n:float|None
    dc_stray:float|None
    ac_stray:float|None
    drainage:str|None

    def __post_init__(self):
        error_text=self.validate()
        if error_text:
            raise ValueError(error_text)

    def validate(self):
        errors = []
        if not (self.pip_d and self.c_type):
            errors.append("缺少管径,防腐层类型")
        if not (self.c_rg or self.c_p or self.c_y):
            errors.append("缺少外防腐层评价")
        if not (self.dc_stray or self.ac_stray):
            errors.append("缺少杂散电流评价")
        if not self.cp_value:
            errors.append("缺少阴极保护率")
        if not self.soil_n:
            errors.append("缺少土壤腐蚀性得分")
        if not self.cp_exist:
            errors.append("缺少是否有阴极保护")
        if not self.drainage:
            errors.append("缺少排流评价")
        return "；".join(errors)
    
    @classmethod
    def alias_name_trans(cls,reverse=False)->dict[str,str]:
        """字段名：别名构成的字典，或相反"""
        mapping_table={
            ('pip_d','管径（mm）'),
            ('c_type','防腐层类型'),
            ('c_rg','防腐层绝缘电阻率Rg值（kΩ·㎡）'),
            ('c_p','防腐层破损点密度P值（处/100m）'),
            ('c_y','防腐层电流衰减率Y值（dB/m）'),
            ('cp_value','阴极保护率'),
            ('cp_exist','是否建设有阴极保护'),
            ('dc_stray','阴保管道电位正于要求的比例或无阴保管道正于自然电位20mV的比例'),
            ('ac_stray','交流电流密度'),
            ('soil_n','土壤腐蚀性评价N值'),
            ('drainage','排流效果'),
        }
        if reverse:
            return dict(map(reversed,mapping_table))
        else:
            return dict(mapping_table)


class ResultDialog(QDialog):
    def __init__(self,score:float,R:NDArray[np.float64],data:dict[str,str|float|None],parent = None):
        super().__init__(parent)
        self.setWindowTitle("评价结果")
        self.resize(600, 700)

        layout = QVBoxLayout()
        
        
        # ===== 数据区、评价区（只读，但可鼠标选中复制）=====
        self.data_text_edit=QTextEdit()
        self.data_text_edit.setReadOnly(True)  # 禁止编辑，但保留选中
        self.result_text_edit = QTextEdit()
        self.result_text_edit.setReadOnly(True)  # 禁止编辑，但保留选中
        # 确保文本可被鼠标选中
        self.result_text_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.data_text_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.data_text_edit.setFixedHeight(100)
        self.result_text_edit.setFixedHeight(100)
        data_text=''
        for key,value in data.items():
            data_text += f"{CPSC_Data.alias_name_trans()[key]}：{value}；" if value else ''
        result_text = f"腐蚀防护系统质量评价得分为{score:.2f}，"
        if score>=90:
            result_text+='等级评价为“1”级，系统功能完好，满足设计要求，在6年的检验周期内能有效使用'
        elif score>=80:
            result_text+='等级评价为“2”级，系统基本完好但存在一些不影响防护效果的缺陷,能基本满足设计要求,3年~6年的检验周期内能使用'
        elif score>=70:
            result_text+='等级评价为“3”级，系统整体状况较差，存在缺陷，不能完全满足设计要求，在使用单位采取适当措施后，可在1年~3年检验周期内在限定的条件下使用'
        else:
            result_text+='等级评价为“4”级，系统缺陷严重,不能满足设计要求,不能有效防止金属管体腐蚀,使用单位应采取重大维修'

        self.data_text_edit.setPlainText(data_text)
        self.result_text_edit.setPlainText(result_text)
        layout.addWidget(QLabel("输入数据"))
        layout.addWidget(self.data_text_edit)
        layout.addWidget(QLabel("评价文本"))
        layout.addWidget(self.result_text_edit)
        
        #   隶属矩阵展示
        self.detail_matrix=QGroupBox('隶属矩阵')
        detail_layout=QVBoxLayout()
        rows,cols=R.shape
        headers=[
            '外防腐层状况',
            '阴极保护有效性',
            '土壤腐蚀性',
            '杂散电流干扰',
            '排流效果'
            ]
        self.table=QTableWidget()
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setVerticalHeaderLabels(headers)
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(f"{R[i, j]:.3f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j,item)
        detail_layout.addWidget(self.table)

        lines = ["$\\begin{bmatrix}"]
    
        for row in R:
            line = "    " + " & ".join(f"{x:.3f}" for x in row) + " \\\\"
            lines.append(line)
        
        lines.append("\\end{bmatrix}$")

        self.latex_text = "\n".join(lines)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_copy_table = QPushButton("📊 复制表格到 Excel")
        btn_copy_latex = QPushButton("📄 复制 LaTeX")
        btn_copy_table.clicked.connect(self._copy_table)
        btn_copy_latex.clicked.connect(self._copy_latex)

        btn_row.addWidget(btn_copy_table)
        btn_row.addWidget(btn_copy_latex)
        btn_row.addStretch()
        detail_layout.addLayout(btn_row)
        self.detail_matrix.setLayout(detail_layout)
        layout.addWidget(self.detail_matrix)
        self.setLayout(layout)

    def _copy_table(self):
        """把整个表格转为制表符分隔文本，写入剪贴板"""
        table = self.table

        rows = table.rowCount()
        cols = table.columnCount()
        
        lines = []
      
        for r in range(rows):
            line = [table.item(r, c).text() for c in range(cols)]
            lines.append("\t".join(line))
        
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)

    def _copy_latex(self):
        """复制 LaTeX 公式源码到系统剪贴板"""
        text = self.latex_text
        QApplication.clipboard().setText(text)

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
        drainage_layout.addWidget(QLabel("排流效果评价（当杂散电流干扰评价为弱时有效，否则无效）"))
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
    def _vertical_calculate(x:float|int|None,v:NDArray[np.float64]|list[float|int],reverse:bool=False)->NDArray[np.float64]:
        """计算隶属向量,越大越安全的参数需最后反转"""
        if x is None:
            x = 0.0 if reverse else 10000.0
        mu:NDArray[np.float64]=np.array([0.0,0.0,0.0,0.0])
        u:NDArray[np.float64]=np.array([
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
    def _compare(*vs:NDArray[np.float64])->NDArray[np.float64]:
        """比较隶属向量，返回最小值"""
        min_v:NDArray[np.float64]=np.array([1.0,0.0,0.0,0.0])
        for v in vs:
            for i in range(4):
                if v[i]<min_v[i]:
                    min_v=v
                    break
                elif v[i]>min_v[i]:
                    break
        return min_v
    
    @staticmethod
    def _interpolate(y:pd.Series,x:NDArray[np.float64]|list[float],x_new:float)->float:
        """插值计算"""
        # 创建三次样条插值对象
        cs = CubicSpline(np.array(x), y.to_numpy())
        # 计算新的y值
        y_new = cs(x_new)
        return y_new

    def on_calculate(self):
        
       
        #   防腐层隶属向量计算
        d=float(self.d_input.text()) if self.d_input.text() else None
        y_input=float(self.y_input.text()) if self.y_input.text() else None
        p_input=float(self.p_input.text()) if self.p_input.text() else None
        rg_input=float(self.rg_input.text()) if self.rg_input.text() else None
        
        c_type="PE防腐层" if self.coat.isChecked() else "沥青防腐层"
        if not self.coat.isChecked() and not self.coat_0.isChecked():
            c_type = None
        
        #   阴极保护隶属向量计算
        cp_input=float(self.cp_input.text()) if self.cp_input.text() else None
        # v_cp=MainWindow._vertical_calculate(cp_input,data["阴极保护区间"],True)
        
        #   土壤腐蚀性隶属向量计算
        soil_input=float(self.soil_input.text()) if self.soil_input.text() else None
        # v_soil=MainWindow._vertical_calculate(soil_input,data["土壤腐蚀性区间"])

        #   杂散电流隶属向量计算
        cp_exist='有阴保' if self.cp.isChecked()  else '无阴保'
        if not self.cp.isChecked() and not self.cp_0.isChecked():
            cp_exist=None
        stray_input=float(self.stray_input.text()) if self.stray_input.text() else None
        stray_input_ac=float(self.ac_input.text()) if self.ac_input.text() else None
   

        #   排流隶属向量
        # v_dra = np.array([1.0,0.0,0.0,0.0] if self.drainage.isChecked() else [0.0,0.0,0.0,1.0]) 
        drainage_eff='有效' if self.drainage.isChecked() else '无效'
        if not self.drainage.isChecked() and not self.drainage_0.isChecked():
            drainage_eff=None
        
        try:
            data0 = CPSC_Data(
                pip_d=d,
                c_rg=rg_input,
                c_p=p_input,
                c_y=y_input,
                c_type=c_type,
                cp_exist=cp_exist,
                cp_value=cp_input,
                dc_stray=stray_input,
                ac_stray=stray_input_ac,
                soil_n=soil_input,
                drainage=drainage_eff
            )
            result=self.calculate(data=data0)
            self.show_result(R=result[0],final_score=result[1],data=result[2])
        except ValueError as e:
            QMessageBox.warning(self, "输入验证失败", str(e))
    
    @classmethod
    def calculate(cls,data:CPSC_Data)->tuple[NDArray[np.float64],float]:
        """根据参数计算隶属矩阵和评分"""
        with open("19285-2026.json",encoding="UTF-8") as f:
            CONFIG=json.load(f)
        
        #   防腐层隶属向量计算
        d = data.pip_d
        y_input = data.c_y if data.c_y else 0.0
        p_input = data.c_p if data.c_p else 0.0
        rg_input = data.c_rg if data.c_rg else 150.0
        
        c_type = data.c_type
        
        coating_rg=MainWindow._vertical_calculate(rg_input,CONFIG[f"{c_type}Rg值区间"],True) 
        coating_p=MainWindow._vertical_calculate(p_input,CONFIG[f"{c_type}P值区间"])
        
        df=pd.DataFrame(CONFIG[f"{c_type}Y值区间"])
        col=df.columns.to_list()
        d_x=[float(t) for t in col]

        if d<=min(d_x):
            coating_y=MainWindow._vertical_calculate(y_input,CONFIG[f"{c_type}Y值区间"][str(int(min(d_x)))]) 
        elif d>=max(d_x):
            coating_y=MainWindow._vertical_calculate(y_input,CONFIG[f"{c_type}Y值区间"][str(int(max(d_x)))]) 
        else:
            df["inter"]=df.apply(MainWindow._interpolate,axis=1,x=d_x,x_new=d)
            coating_y=MainWindow._vertical_calculate(y_input,df["inter"]) 

        v_coat=MainWindow._compare(coating_rg,coating_p,coating_y)
        
        #   阴极保护隶属向量计算
        cp_input=0.01*data.cp_value
        v_cp=MainWindow._vertical_calculate(cp_input,CONFIG["阴极保护区间"],True)
        
        #   土壤腐蚀性隶属向量计算
        soil_input=data.soil_n
        v_soil=MainWindow._vertical_calculate(soil_input,CONFIG["土壤腐蚀性区间"])

        #   杂散电流隶属向量计算
        cp_exist=data.cp_exist
        stray_input=0.01*data.dc_stray if data.dc_stray else 0.0
        stray_input_ac=data.ac_stray if data.ac_stray else 0.0
        v_dc=MainWindow._vertical_calculate(stray_input,CONFIG[f"直流干扰区间-{cp_exist}"])
        v_ac=MainWindow._vertical_calculate(stray_input_ac,CONFIG["交流干扰区间"])
        v_stray=MainWindow._compare(v_dc,v_ac)

        #   排流隶属向量
        v_dra = np.array([1.0,0.0,0.0,0.0] if data.drainage == '有效' else [0.0,0.0,0.0,1.0]) 

        v_w:NDArray[np.float64]=np.array([0.402,0.269,0.099,0.066,0.163])
        R_matrix=np.array(
            [
                v_coat,
                v_cp,
                v_soil,
                v_stray,
                v_dra
            ]
        )
        R_matrix:NDArray[np.float64]=np.where(np.abs(R_matrix)<1e-5,0.0,R_matrix)
        v_a=v_w@R_matrix
        c_h=np.array([100,89,79,69])
        c_m=np.array([95,85,75,65])
        c_l=np.array([90,80,70,60])
        s_h=np.sum(v_a*c_h)/np.sum(v_a)
        s_m=np.sum(v_a*c_m)/np.sum(v_a)
        s_l=np.sum(v_a*c_l)/np.sum(v_a)
        s_=(s_h+s_m+s_l)/3.00

        return (R_matrix,s_,asdict(data))



    def show_result(self,R,final_score,data):
        dialog=ResultDialog(parent=self,R=R,score=final_score,data=data)
        dialog.exec()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())