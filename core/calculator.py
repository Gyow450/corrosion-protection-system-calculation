from core.models import InputPayload, ResultPayload, AppConfig

class Calculator:
    """纯业务逻辑，无 Qt 依赖，可直接单元测试"""

    @staticmethod
    def compute(data: InputPayload, config: AppConfig) -> ResultPayload:
        m = data.mass
        v = data.velocity
        c = config.correction_factor
        p = config.precision

        if data.mode == "动能":
            raw = 0.5 * m * (v ** 2) * c
            formula = r"E_k = \frac{1}{2} m v^2 \cdot c"
            text = f"动能 = {raw:.{p}f} J"
            html = (
                f"<p>质量: <b>{m}</b> kg &nbsp;|&nbsp; 速度: <b>{v}</b> m/s</p>"
                f"<p>修正系数: <b>{c}</b></p>"
                f"<p>结果: <span style='color:#1565C0;font-size:18px;font-weight:bold;'>{raw:.{p}f}</span> J</p>"
            )
        else:
            raw = m * v * c
            formula = r"p = m v \cdot c"
            text = f"动量 = {raw:.{p}f} kg·m/s"
            html = (
                f"<p>质量: <b>{m}</b> kg &nbsp;|&nbsp; 速度: <b>{v}</b> m/s</p>"
                f"<p>修正系数: <b>{c}</b></p>"
                f"<p>结果: <span style='color:#1565C0;font-size:18px;font-weight:bold;'>{raw:.{p}f}</span> kg·m/s</p>"
            )

        return ResultPayload(
            text_summary=text,
            latex_items=[formula, f"\text{{计算值}} = {raw:.{p}f}"],
            html_details=html
        )
