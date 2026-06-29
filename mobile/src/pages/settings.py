import flet as ft
from db.local_db import save_setting, get_setting

class SettingsPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.expand = True
        self.bgcolor = "#0a0a14"
        self.padding = 20
        self.page = page
        
        # Load current
        current_api = get_setting("api_url", "http://127.0.0.1:8000")
        current_ble = get_setting("ble_name", "AquaMonitor")
        current_virtual = get_setting("use_virtual_ble", "1")
        
        self.api_input = ft.TextField(label="FastAPI Backend URL", value=current_api, width=300)
        self.ble_input = ft.TextField(label="BLE Device Name", value=current_ble, width=300)
        self.virtual_toggle = ft.Switch(label="Use Virtual BLE (Testing)", value=(current_virtual == "1"))
        
        self.status_text = ft.Text("")

        self.content = ft.Column([
            ft.Text("App Settings", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self.api_input,
            self.ble_input,
            ft.Container(height=10),
            self.virtual_toggle,
            ft.Container(height=20),
            ft.ElevatedButton("Save Settings", on_click=self.on_save, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
            ft.Container(height=10),
            self.status_text
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def on_save(self, e):
        save_setting("api_url", self.api_input.value)
        save_setting("ble_name", self.ble_input.value)
        save_setting("use_virtual_ble", "1" if self.virtual_toggle.value else "0")
        
        self.status_text.value = "Settings saved! Please restart app to apply BLE changes."
        self.status_text.color = ft.colors.GREEN
        self.update()
