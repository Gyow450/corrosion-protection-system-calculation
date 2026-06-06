import matplotlib
matplotlib.use("Agg")  # 无头后端，不依赖显示服务器

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PySide6.QtGui import QImage, QPixmap


def latex_to_pixmap(latex_str: str, fontsize: int = 16, dpi: int = 150) -> QPixmap:
    """将 LaTeX 字符串渲染为 QPixmap，供 QLabel 直接显示"""
    # 使用极小的 figsize，让文本自动决定画布大小
    fig = Figure(figsize=(0.01, 0.01))
    canvas = FigureCanvasAgg(fig)

    # 在画布中心渲染公式，使用数学模式 $...$
    fig.text(0.5, 0.5, f"${latex_str}$", fontsize=fontsize, ha="center", va="center")
    canvas.draw()

    # 从 Agg 画布提取 RGBA 缓冲区
    buf = canvas.buffer_rgba()
    w, h = canvas.get_width_height()

    # 构造 QImage（注意字节对齐）
    image = QImage(buf, w, h, QImage.Format_ARGB32)
    return QPixmap.fromImage(image)
