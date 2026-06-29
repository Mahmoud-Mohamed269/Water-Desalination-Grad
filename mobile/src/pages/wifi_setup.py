import flet as ft

class WifiSetupPage(ft.Container):
    def __init__(self, send_command_callback):
        super().__init__()
        self.expand = True
        self.bgcolor = "#0a0a14"
        self.padding = 20
        self.send_cmd = send_command_callback
        
        self.ssid_input = ft.TextField(label="WiFi SSID", width=300)
        self.pass_input = ft.TextField(label="WiFi Password", password=True, can_reveal_password=True, width=300)
        self.status_text = ft.Text("")

        self.content = ft.Column([
            ft.Text("Hardware WiFi Setup", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Enter credentials to connect the Main Hub to your local network.", color=ft.colors.GREY_400),
            ft.Container(height=30),
            self.ssid_input,
            self.pass_input,
            ft.Container(height=20),
            ft.ElevatedButton("Send via BLE", on_click=self.on_submit, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
            ft.Container(height=20),
            self.status_text
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    async def on_submit(self, e):
        ssid = self.ssid_input.value
        pwd = self.pass_input.value
        
        if not ssid:
            self.status_text.value = "SSID is required."
            self.status_text.color = ft.colors.RED
            self.update()
            return
            
        self.status_text.value = "Sending command via BLE..."
        self.status_text.color = ft.colors.GREY_400
        self.update()
        
        cmd = {
            "cmd": "set_wifi",
            "ssid": ssid,
            "pass": pwd
        }
        
        success = await self.send_cmd(cmd)
        if success:
            self.status_text.value = "Credentials sent successfully! Hub is restarting WiFi."
            self.status_text.color = ft.colors.GREEN
        else:
            self.status_text.value = "Failed to send. Is BLE connected?"
            self.status_text.color = ft.colors.RED
        self.update()
