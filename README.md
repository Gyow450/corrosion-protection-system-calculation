# Qt 骨架项目 —— 表单收集 + 后台计算 + 结果展示

## 项目结构

```
qt_skeleton/
├── main.py              # 程序入口
├── core/
│   ├── __init__.py
│   ├── models.py        # 数据模型（dataclass）
│   └── calculator.py    # 纯计算逻辑（无 Qt 依赖）
└── ui/
    ├── __init__.py
    ├── main_window.py   # 主窗口（布局 + 事件协调）
    ├── dialogs.py       # 高级参数子对话框（QDialog）
    └── latex_renderer.py # LaTeX → QPixmap 渲染器
```

## 依赖安装

```bash
pip install PySide6 matplotlib
```

## 运行

```bash
cd qt_skeleton
python main.py
```

## 设计要点说明

1. **同步计算**：单次计算在 UI 线程直接执行，无 QThread/Worker 开销。
2. **模态对话框**：`AdvancedDialog` 继承 `QDialog`，`setModal(True)` 阻塞主窗口，OK/Cancel 标准按钮。
3. **LaTeX 渲染**：使用 `matplotlib` Agg 后端将公式渲染为图片，贴到 `QLabel` 上。纯离线，无需网络。
4. **配置持久化**：`QSettings` 自动处理跨平台存储（Windows 注册表 / macOS plist / Linux ini）。仅保存高级参数和上次输入。
5. **分层解耦**：`core/` 完全不导入 Qt，可单独测试；`ui/` 只负责展示和事件转发。

## 替换业务逻辑

修改 `core/calculator.py` 中的 `Calculator.compute()` 方法即可接入你的实际公式。
