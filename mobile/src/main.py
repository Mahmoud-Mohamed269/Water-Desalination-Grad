import flet as ft
import asyncio
import requests
from pages.dashboard import DashboardPage
from pages.history import HistoryPage
from pages.alerts import AlertsPage
from pages.wifi_setup import WifiSetupPage
from pages.settings import SettingsPage
from ble.client import VirtualBLEClient, RealBLEClient
from db.sync import sync_data_loop
from db.local_db import get_setting

def main(page: ft.Page):
    page.title = "AquaMonitor Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0a14"
    page.padding = 0

    # Simulate mobile dimensions for desktop testing
    page.window.width = 400
    page.window.height = 800

    # Start Sync Worker
    page.run_task(sync_data_loop)

    # Initialize BLE Client
    use_virtual = get_setting("use_virtual_ble", "1") == "1"
    ble_name    = get_setting("ble_name", "AquaMonitor")

    ble_client = VirtualBLEClient() if use_virtual else RealBLEClient(device_name=ble_name)
    page.run_task(ble_client.connect)

    # Instantiate Pages
    page_dashboard = DashboardPage()
    page_history   = HistoryPage()
    page_alerts    = AlertsPage()
    page_wifi      = WifiSetupPage(send_command_callback=ble_client.send_command)
    page_settings  = SettingsPage(page)

    pages = {
        0: page_dashboard,
        1: page_history,
        2: page_alerts,
        3: page_wifi,
        4: page_settings,
    }

    # Main content container
    content_area = ft.Container(content=page_dashboard, expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        content_area.content = pages[idx]

        if idx == 1:
            page_history.update_data()
        elif idx == 2:
            page_alerts.update_data()

        page.update()

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        bgcolor="#12121f",
        indicator_color=ft.colors.with_opacity(0.15, "#00d2fc"),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.icons.DASHBOARD_OUTLINED,
                selected_icon=ft.icons.DASHBOARD,
                label="Live",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.SHOW_CHART_OUTLINED,
                selected_icon=ft.icons.SHOW_CHART,
                label="History",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.icons.NOTIFICATIONS,
                label="Alerts",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.WIFI_OUTLINED,
                selected_icon=ft.icons.WIFI,
                label="WiFi",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    page.add(
        ft.Column([content_area, bottom_nav], expand=True)
    )

    # ── Background UI Update Loop ─────────────────────────────
    async def update_ui_loop():
        api_url = get_setting("api_url", "http://127.0.0.1:8000")
        if not api_url.endswith("/"): api_url += "/"

        while True:
            is_online = False
            try:
                res = requests.get(
                    f"{api_url}api/v1/sensors/live", timeout=0.5
                )
                if res.status_code == 200:
                    is_online = True
            except Exception:
                pass

            current = content_area.content
            if current is page_dashboard:
                page_dashboard.update_data(is_online=is_online)

            await asyncio.sleep(1)

    page.run_task(update_ui_loop)


if __name__ == "__main__":
    ft.app(target=main)
