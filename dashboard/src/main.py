import flet as ft
import sys
import os

# Make sure local modules are discoverable
sys.path.insert(0, os.path.dirname(__file__))

from utils.constants import *
from services.api_client import get_live_sensors, get_predictions, send_chat_message


def main(page: ft.Page):
    page.title = APP_TITLE
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR_DARK

    # ─── State ───────────────────────────────────────────────────────────────
    current_page = ft.Ref[ft.Column]()

    # ─── Theme toggle ─────────────────────────────────────────────────────────
    def toggle_theme(e):
        dark = page.theme_mode == ft.ThemeMode.LIGHT
        page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT
        page.bgcolor = BG_COLOR_DARK if dark else BG_COLOR_LIGHT
        sidebar_bg.bgcolor = PRIMARY_DARK if dark else "#E8EDF2"
        content_area.bgcolor = BG_COLOR_DARK if dark else BG_COLOR_LIGHT
        theme_switch.value = dark
        page.update()

    # ─── Helper: card ─────────────────────────────────────────────────────────
    def make_card(content, margin_bottom=16):
        return ft.Container(
            content=content,
            bgcolor=CARD_DARK,
            border_radius=12,
            padding=20,
            margin=ft.margin.only(bottom=margin_bottom),
        )

    # ─── Overview page ────────────────────────────────────────────────────────
    def build_overview():
        status_text = ft.Text("Fetching live status...", color=ft.colors.GREY_400, size=14)
        wq_text = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR)
        ms_text = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR)
        rr_text = ft.Text("—", size=28, weight=ft.FontWeight.BOLD)

        def load(e=None):
            sensors = get_live_sensors()
            preds = get_predictions()

            if sensors and sensors.get("status") == "ok":
                d = sensors.get("data", {})
                status_text.value = "System Status: ONLINE"
                status_text.color = SUCCESS_COLOR
                rr_text.value = f"{d.get('flow_rate', '—')} L/min"
            else:
                status_text.value = "System Status: OFFLINE / No Data"
                status_text.color = DANGER_COLOR

            if preds and preds.get("status") == "ok":
                p = preds.get("predictions", {})
                wq_label = p.get("water_quality", {}).get("label", "—")
                ms_label = p.get("membrane_status", {}).get("label", "—")
                wq_text.value = wq_label
                wq_text.color = SUCCESS_COLOR if wq_label == "Excellent" else WARNING_COLOR
                ms_text.value = ms_label
                ms_text.color = SUCCESS_COLOR if ms_label == "Healthy" else DANGER_COLOR
            page.update()

        load()

        return ft.Column(
            [
                ft.Text("System Overview", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                status_text,
                ft.Container(height=16),
                ft.Row(
                    [
                        make_card(ft.Column([ft.Text("Water Quality", color=ft.colors.GREY_400), wq_text])),
                        make_card(ft.Column([ft.Text("Membrane Status", color=ft.colors.GREY_400), ms_text])),
                        make_card(ft.Column([ft.Text("Flow Rate", color=ft.colors.GREY_400), rr_text])),
                    ],
                    wrap=True, spacing=16,
                ),
                ft.ElevatedButton("Refresh", icon=ft.icons.REFRESH, on_click=load),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ─── Sensors page ─────────────────────────────────────────────────────────
    def build_sensors():
        node1_row = ft.Row(wrap=True, spacing=16)
        node2_row = ft.Row(wrap=True, spacing=16)
        msg = ft.Text("", color=DANGER_COLOR)

        def sensor_card(label, value, unit=""):
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=12, color=ft.colors.GREY_400),
                    ft.Text(f"{value} {unit}".strip(), size=22, weight=ft.FontWeight.BOLD),
                ]),
                bgcolor=CARD_DARK, border_radius=12, padding=20, width=180,
            )

        def load(e=None):
            node1_row.controls.clear()
            node2_row.controls.clear()
            sensors = get_live_sensors()
            if sensors and sensors.get("status") == "ok":
                d = sensors.get("data", {})
                msg.value = ""
                node1_row.controls += [
                    sensor_card("pH", d.get("ph", "—")),
                    sensor_card("TDS", d.get("tds", "—"), "ppm"),
                    sensor_card("Turbidity", d.get("turbidity", "—"), "NTU"),
                    sensor_card("Pressure", d.get("pressure", "—"), "bar"),
                    sensor_card("Flow Rate", d.get("flow_rate", "—"), "L/min"),
                    sensor_card("Pump", "ON" if d.get("pump_status") else "OFF"),
                ]
                node2_row.controls += [
                    sensor_card("Ambient Temp", d.get("ambient_temp", "—"), "°C"),
                    sensor_card("Humidity", d.get("ambient_humidity", "—"), "%"),
                    sensor_card("Gas 1", d.get("gas_1_ppm", "—"), "ppm"),
                    sensor_card("Gas 2", d.get("gas_2_ppm", "—"), "ppm"),
                    sensor_card("Tank 1", d.get("tank1_level_cm", "—"), "cm"),
                    sensor_card("Tank 2", d.get("tank2_level_cm", "—"), "cm"),
                ]
            else:
                msg.value = "No sensor data available."
            page.update()

        load()

        return ft.Column(
            [
                ft.Text("Live Sensor Data", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Refresh", icon=ft.icons.REFRESH, on_click=load),
                msg,
                ft.Container(height=8),
                ft.Text("Node 1 — Water Quality", size=20, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
                node1_row,
                ft.Container(height=16),
                ft.Text("Node 2 — Environment", size=20, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
                node2_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ─── Predictions page ─────────────────────────────────────────────────────
    def build_predictions():
        wq_label = ft.Text("—", size=26, weight=ft.FontWeight.BOLD)
        wq_conf = ft.Text("", color=ft.colors.GREY_400)
        ms_label = ft.Text("—", size=26, weight=ft.FontWeight.BOLD)
        ms_conf = ft.Text("", color=ft.colors.GREY_400)
        msg = ft.Text("", color=DANGER_COLOR)

        def load(e=None):
            preds = get_predictions()
            if preds and preds.get("status") == "ok":
                p = preds.get("predictions", {})
                wq = p.get("water_quality", {})
                ms = p.get("membrane_status", {})
                wq_label.value = wq.get("label", "—")
                wq_label.color = SUCCESS_COLOR if wq.get("label") == "Excellent" else WARNING_COLOR
                wq_conf.value = f"Confidence: {wq.get('confidence', '—')}%"
                ms_label.value = ms.get("label", "—")
                ms_label.color = SUCCESS_COLOR if ms.get("label") == "Healthy" else DANGER_COLOR
                ms_conf.value = f"Confidence: {ms.get('confidence', '—')}%"
                msg.value = ""
            else:
                msg.value = "Could not fetch ML predictions."
            page.update()

        load()

        return ft.Column(
            [
                ft.Text("ML Predictions", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Run Inference", icon=ft.icons.ANALYTICS, on_click=load),
                msg,
                ft.Container(height=16),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Water Quality", size=16, color=ft.colors.GREY_400),
                                wq_label, wq_conf,
                            ]),
                            bgcolor=CARD_DARK, border_radius=12, padding=24, expand=1,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Membrane Fouling Risk", size=16, color=ft.colors.GREY_400),
                                ms_label, ms_conf,
                            ]),
                            bgcolor=CARD_DARK, border_radius=12, padding=24, expand=1,
                        ),
                    ],
                    spacing=16,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ─── Chatbot page ─────────────────────────────────────────────────────────
    def build_chatbot():
        messages = ft.ListView(expand=True, spacing=8, auto_scroll=True)
        input_field = ft.TextField(
            hint_text="Ask about your RO system…",
            expand=True,
            border_radius=8,
            on_submit=lambda e: send(e),
        )

        def bubble(text, is_user):
            return ft.Container(
                content=ft.Text(text, selectable=True, size=14),
                bgcolor=PRIMARY_DARK if is_user else CARD_DARK,
                border_radius=ft.border_radius.only(
                    top_left=12, top_right=12,
                    bottom_left=0 if is_user else 12,
                    bottom_right=12 if is_user else 0,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                margin=ft.margin.only(left=60 if is_user else 0, right=0 if is_user else 60),
            )

        def send(e):
            msg = input_field.value.strip()
            if not msg:
                return
            input_field.value = ""
            messages.controls.append(bubble(msg, is_user=True))
            spinner = ft.Row([ft.ProgressRing(width=16, height=16), ft.Text("Thinking…", color=ft.colors.GREY_400)])
            messages.controls.append(spinner)
            page.update()

            result = send_chat_message(msg)
            messages.controls.remove(spinner)
            reply = result.get("reply", "Error — no reply.") if result and result.get("status") == "ok" else "⚠️ Could not reach the AI service."
            messages.controls.append(bubble(reply, is_user=False))
            page.update()

        return ft.Column(
            [
                ft.Text("AI Desalination Assistant", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                ft.Container(content=messages, expand=True, border=ft.border.all(1, ft.colors.GREY_800), border_radius=12, padding=12),
                ft.Row([input_field, ft.IconButton(ft.icons.SEND_ROUNDED, on_click=send)]),
            ],
            expand=True,
        )

    # ─── Navigation ───────────────────────────────────────────────────────────
    pages = {
        0: build_overview,
        1: build_sensors,
        2: build_predictions,
        3: build_chatbot,
    }

    content_area = ft.Container(expand=True, padding=24, bgcolor=BG_COLOR_DARK)
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=220,
        bgcolor=PRIMARY_DARK,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD_ROUNDED, label="Overview"),
            ft.NavigationRailDestination(icon=ft.icons.SENSORS_OUTLINED, selected_icon=ft.icons.SENSORS, label="Sensors"),
            ft.NavigationRailDestination(icon=ft.icons.ANALYTICS_OUTLINED, selected_icon=ft.icons.ANALYTICS, label="Predictions"),
            ft.NavigationRailDestination(icon=ft.icons.SMART_TOY_OUTLINED, selected_icon=ft.icons.SMART_TOY_ROUNDED, label="Chatbot"),
        ],
        on_change=lambda e: switch_page(e.control.selected_index),
        trailing=ft.Column(
            [
                ft.Divider(color=ft.colors.GREY_800),
                ft.Text("Dark", size=11, color=ft.colors.GREY_500),
                ft.Switch(value=True, on_change=toggle_theme, width=60),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    theme_switch = nav_rail.trailing.controls[2]

    def switch_page(index):
        content_area.content = pages[index]()
        page.update()

    sidebar_bg = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=16),
                ft.Image(src="TVI Logo.jpg", height=56, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=8),
                ft.Image(src="Water Desalination.png", height=56, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=8),
                nav_rail,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=PRIMARY_DARK,
        width=140,
    )

    # Build initial page
    content_area.content = pages[0]()

    page.add(
        ft.Row(
            [sidebar_bg, content_area],
            expand=True,
            spacing=0,
        )
    )


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER)
