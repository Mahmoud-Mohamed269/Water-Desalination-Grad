import flet as ft
import requests
from db.local_db import get_latest_reading, get_setting

# ML label colour mapping
_QUALITY_COLORS = {
    "good":       "#22c55e",
    "acceptable": "#84cc16",
    "poor":       "#f97316",
    "bad":        "#ef4444",
}
_MEMBRANE_COLORS = {
    "good":     "#22c55e",
    "warning":  "#f97316",
    "critical": "#ef4444",
    "fouled":   "#ef4444",
}


class DashboardPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand  = True
        self.bgcolor = "#0a0a14"

        # ── Connection / pump ────────────────────────────────────
        self.conn_status = ft.Text(
            "Connecting to BLE…", color=ft.colors.GREY_500, size=12
        )
        self.pump_status = ft.Text(
            "—", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN
        )

        # ── Sensor value text controls ───────────────────────────
        self.ph_val    = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.tds_val   = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.turb_val  = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.temp_val  = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.press_val = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.flow_val  = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.rec_val   = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)
        self.rej_val   = ft.Text("—", size=20, weight=ft.FontWeight.BOLD)

        # ── ML Prediction controls ───────────────────────────────
        self.wq_label    = ft.Text("—", size=18, weight=ft.FontWeight.BOLD,
                                   color=ft.colors.GREY_400)
        self.wq_conf     = ft.Text("",  size=12, color=ft.colors.GREY_500)
        self.mem_label   = ft.Text("—", size=18, weight=ft.FontWeight.BOLD,
                                   color=ft.colors.GREY_400)
        self.mem_conf    = ft.Text("",  size=12, color=ft.colors.GREY_500)
        self.pred_status = ft.Text("Tap ↻ to run ML analysis",
                                   size=11, color=ft.colors.GREY_600)

        self.content = ft.Column(
            [
                # ── Header ──────────────────────────────────────
                ft.Row(
                    [
                        ft.Image(src="TVI Logo.jpg", height=40),
                        ft.Text("AquaMonitor", size=20,
                                weight=ft.FontWeight.BOLD, color="#00d2fc"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),

                # ── Status card ──────────────────────────────────
                ft.Container(
                    content=ft.Column(
                        [
                            self.conn_status,
                            ft.Text("Pump Status", size=14,
                                    color=ft.colors.GREY_400),
                            self.pump_status,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#1a1a2e", border_radius=16,
                    padding=20, alignment=ft.alignment.center,
                ),

                ft.Container(height=10),
                ft.Text("Live KPI", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.stat_box("Recovery",  self.rec_val, "%"),
                    self.stat_box("Rejection", self.rej_val, "%"),
                ]),

                ft.Container(height=10),
                ft.Text("Live Sensors", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.stat_box("pH Feed",     self.ph_val,    ""),
                    self.stat_box("TDS Feed",    self.tds_val,   "ppm"),
                ]),
                ft.Row([
                    self.stat_box("Turbidity",   self.turb_val,  "NTU"),
                    self.stat_box("Pressure",    self.press_val, "bar"),
                ]),
                ft.Row([
                    self.stat_box("Temperature", self.temp_val,  "°C"),
                    self.stat_box("Flow",        self.flow_val,  "L/min"),
                ]),

                ft.Container(height=10),

                # ── ML Predictions section ───────────────────────
                ft.Row(
                    [
                        ft.Text("ML Analysis", size=16,
                                weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            icon_color="#00d2fc",
                            tooltip="Run ML prediction",
                            on_click=lambda _: self._run_prediction(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row([
                    self._pred_card("Water Quality", self.wq_label,
                                    self.wq_conf,   ft.icons.WATER_DROP),
                    self._pred_card("Membrane",      self.mem_label,
                                    self.mem_conf,  ft.icons.FILTER_ALT),
                ]),
                self.pred_status,
                ft.Container(height=10),
            ],
            expand=True, spacing=10, scroll=ft.ScrollMode.AUTO,
        )

    # ─────────────────────────────────────────────────────────
    def stat_box(self, label, text_ctrl, unit):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, color=ft.colors.GREY_400, size=12),
                ft.Row(
                    [text_ctrl, ft.Text(unit, color=ft.colors.GREY_500,
                                        size=12)],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ]),
            bgcolor="#12121f", border_radius=12, padding=16, expand=1,
        )

    def _pred_card(self, title, label_ctrl, conf_ctrl, icon):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Icon(icon, color=ft.colors.GREY_500, size=16),
                        ft.Text(title, color=ft.colors.GREY_400, size=12),
                    ], spacing=4),
                    label_ctrl,
                    conf_ctrl,
                ],
                spacing=4,
            ),
            bgcolor="#12121f", border_radius=12, padding=16, expand=1,
        )

    # ─────────────────────────────────────────────────────────
    def _run_prediction(self):
        """Fetch /predict/run from backend and update ML cards."""
        api_url = get_setting("api_url", "http://127.0.0.1:8000").rstrip("/")
        self.pred_status.value = "Running ML prediction…"
        self.pred_status.color = ft.colors.GREY_500
        try:
            self.update()
        except Exception:
            pass

        try:
            res = requests.get(f"{api_url}/api/v1/predict/run", timeout=6)
            if res.status_code == 200:
                preds = res.json().get("predictions", {})

                wq = preds.get("water_quality", {})
                wq_lbl  = wq.get("label", "—").capitalize()
                wq_pct  = wq.get("confidence", 0)
                wq_col  = _QUALITY_COLORS.get(wq.get("label", ""), "#00d2fc")
                self.wq_label.value = wq_lbl
                self.wq_label.color = wq_col
                self.wq_conf.value  = f"{wq_pct}% confidence"

                mem = preds.get("membrane_status", {})
                mem_lbl = mem.get("label", "—").capitalize()
                mem_pct = mem.get("confidence", 0)
                mem_col = _MEMBRANE_COLORS.get(mem.get("label", ""), "#00d2fc")
                self.mem_label.value = mem_lbl
                self.mem_label.color = mem_col
                self.mem_conf.value  = f"{mem_pct}% confidence"

                self.pred_status.value = "✓ Prediction complete"
                self.pred_status.color = ft.colors.GREEN_400
            else:
                self.pred_status.value = f"Backend error {res.status_code}"
                self.pred_status.color = ft.colors.ORANGE_400
        except Exception as exc:
            self.pred_status.value = f"Offline — {exc}"
            self.pred_status.color = ft.colors.RED_400

        try:
            self.update()
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────
    def update_data(self, is_online=False):
        latest = get_latest_reading()
        if latest:
            self.ph_val.value    = str(latest.get("ph_feed",
                                        latest.get("ph", "—")))
            self.tds_val.value   = str(latest.get("tds_feed",
                                        latest.get("tds", "—")))
            self.turb_val.value  = str(latest.get("turbidity_feed",
                                        latest.get("turbidity", "—")))
            self.temp_val.value  = str(latest.get("temperature_feed", "—"))
            self.press_val.value = str(latest.get("pressure_feed",
                                        latest.get("pressure", "—")))
            self.flow_val.value  = str(latest.get("flow_rate_feed",
                                        latest.get("flow_rate", "—")))
            self.rec_val.value   = str(latest.get("recovery_rate", "—"))
            self.rej_val.value   = str(latest.get("rejection_rate", "—"))

            pump = latest.get("pump_status", "stopped")
            self.pump_status.value = pump.upper()
            self.pump_status.color = (
                ft.colors.GREEN if pump == "running" else ft.colors.RED
            )

            if is_online:
                self.conn_status.value = "● SYNCED (Online & BLE connected)"
                self.conn_status.color = ft.colors.GREEN
            else:
                self.conn_status.value = "● OFFLINE (Saving locally via BLE)"
                self.conn_status.color = ft.colors.ORANGE

        self.update()
