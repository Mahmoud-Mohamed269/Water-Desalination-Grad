import flet as ft
import requests
from db.local_db import get_setting


SEVERITY_COLORS = {
    "critical": "#ef4444",
    "warning":  "#f97316",
    "info":     "#3b82f6",
}
SEVERITY_BG = {
    "critical": "#2d0a0a",
    "warning":  "#2d1500",
    "info":     "#0a1a2d",
}
SEVERITY_ICONS = {
    "critical": ft.icons.ERROR,
    "warning":  ft.icons.WARNING_AMBER,
    "info":     ft.icons.INFO,
}


class AlertsPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand   = True
        self.bgcolor  = "#0a0a14"
        self.padding  = 20

        self._alerts  = []

        self.status_text = ft.Text(
            "Pull alerts from backend…",
            color=ft.colors.GREY_500, size=12,
        )
        self.refresh_btn = ft.IconButton(
            icon=ft.icons.REFRESH,
            icon_color="#00d2fc",
            tooltip="Refresh alerts",
            on_click=lambda _: self._do_refresh(),
        )

        self.alert_list = ft.ListView(expand=True, spacing=8)

        self.content = ft.Column(
            [
                # ── header row ──────────────────────────────────────
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Alerts", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color="#00d2fc"),
                                self.status_text,
                            ],
                            spacing=2, expand=True,
                        ),
                        self.refresh_btn,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=12),
                self.alert_list,
            ],
            expand=True, spacing=4,
        )

    # ──────────────────────────────────────────────────────────
    def _do_refresh(self):
        """Synchronous HTTP fetch — runs fine inside Flet's thread pool."""
        api_url = get_setting("api_url", "http://127.0.0.1:8000").rstrip("/")
        try:
            res = requests.get(f"{api_url}/api/v1/alerts/history",
                               timeout=5)
            if res.status_code == 200:
                body = res.json()
                self._alerts = body.get("alerts", [])
                # Sort newest first by timestamp
                self._alerts.sort(
                    key=lambda a: a.get("timestamp", ""), reverse=True
                )
                self.status_text.value = (
                    f"{len(self._alerts)} alert(s) — "
                    f"updated just now"
                )
                self.status_text.color = ft.colors.GREEN_400
            else:
                self.status_text.value = f"Server error {res.status_code}"
                self.status_text.color = ft.colors.ORANGE_400
        except Exception as exc:
            self.status_text.value = f"Offline — {exc}"
            self.status_text.color = ft.colors.RED_400

        self._rebuild_list()
        try:
            self.update()
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────
    def _rebuild_list(self):
        self.alert_list.controls.clear()

        if not self._alerts:
            self.alert_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE,
                                    color=ft.colors.GREEN_400, size=48),
                            ft.Text("No alerts — system is healthy!",
                                    color=ft.colors.GREY_400,
                                    text_align=ft.TextAlign.CENTER,
                                    size=14),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
            return

        for alert in self._alerts:
            sev     = alert.get("severity", "info")
            color   = SEVERITY_COLORS.get(sev, "#3b82f6")
            bg      = SEVERITY_BG.get(sev, "#0a1a2d")
            icon    = SEVERITY_ICONS.get(sev, ft.icons.INFO)
            sensor  = alert.get("sensor", "Unknown")
            message = alert.get("message", "")
            ts_raw  = alert.get("timestamp", "")

            # Format timestamp
            if "T" in ts_raw:
                date_part, time_part = ts_raw.split("T", 1)
                ts_display = f"{date_part}  {time_part[:8]}"
            else:
                ts_display = ts_raw

            self.alert_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            # severity icon
                            ft.Container(
                                content=ft.Icon(icon, color=color, size=28),
                                padding=ft.padding.only(right=12),
                            ),
                            # text block
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    sev.upper(),
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=color,
                                                ),
                                                bgcolor=ft.colors.with_opacity(
                                                    0.15, color
                                                ),
                                                border_radius=4,
                                                padding=ft.padding.symmetric(
                                                    horizontal=6, vertical=2
                                                ),
                                            ),
                                            ft.Text(
                                                sensor,
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.WHITE,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Text(message,
                                            size=12,
                                            color=ft.colors.GREY_300),
                                    ft.Text(ts_display,
                                            size=10,
                                            color=ft.colors.GREY_600),
                                ],
                                spacing=3, expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    bgcolor=bg,
                    border=ft.border.all(1, ft.colors.with_opacity(0.3, color)),
                    border_radius=12,
                    padding=14,
                )
            )

    # ──────────────────────────────────────────────────────────
    def update_data(self):
        """Called by nav switch — triggers a refresh."""
        self._do_refresh()
