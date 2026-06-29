# dashboard/src/pages/sensors.py
import flet as ft
from utils.constants import *
from services.api_client import get_live_sensors

def SensorsPage(page: ft.Page):
    title = ft.Text("Live Sensor Data", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.colors.BLACK)
    
    node1_container = ft.Column()
    node2_container = ft.Column()

    def create_sensor_card(label, value, unit=""):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=14, color=ft.colors.GREY_400),
                ft.Text(f"{value} {unit}", size=24, weight=ft.FontWeight.BOLD)
            ]),
            padding=20,
            bgcolor=CARD_DARK if page.theme_mode == ft.ThemeMode.DARK else CARD_LIGHT,
            border_radius=10,
            width=200,
        )

    def refresh_data(e=None):
        sensors = get_live_sensors()
        node1_container.controls.clear()
        node2_container.controls.clear()
        
        if sensors:
            # Node 1: Water Quality
            row1 = ft.Row(wrap=True, spacing=20)
            row1.controls.append(create_sensor_card("pH Feed", sensors.get('ph_feed', 'N/A')))
            row1.controls.append(create_sensor_card("pH Permeate", sensors.get('ph_permeate', 'N/A')))
            row1.controls.append(create_sensor_card("TDS Feed", sensors.get('tds_feed', 'N/A'), "ppm"))
            row1.controls.append(create_sensor_card("TDS Permeate", sensors.get('tds_permeate', 'N/A'), "ppm"))
            row1.controls.append(create_sensor_card("Turbidity Feed", sensors.get('turbidity_feed', 'N/A'), "NTU"))
            row1.controls.append(create_sensor_card("Pressure Feed", sensors.get('pressure_feed', 'N/A'), "bar"))
            row1.controls.append(create_sensor_card("Flow Feed", sensors.get('flow_rate_feed', 'N/A'), "L/min"))
            row1.controls.append(create_sensor_card("Flow Permeate", sensors.get('flow_rate_permeate', 'N/A'), "L/min"))
            node1_container.controls.append(row1)
            
            # Node 2: Environment
            row2 = ft.Row(wrap=True, spacing=20)
            row2.controls.append(create_sensor_card("Ambient Temp", sensors.get('ambient_temp', 'N/A'), "°C"))
            row2.controls.append(create_sensor_card("Gas Levels", sensors.get('gas_1_ppm', 'N/A'), "ppm"))
            node2_container.controls.append(row2)
        else:
            node1_container.controls.append(ft.Text("No data available from Node 1.", color=DANGER_COLOR))
            node2_container.controls.append(ft.Text("No data available from Node 2.", color=DANGER_COLOR))
        
        if e is not None:
            page.update()

    refresh_data(None)
    
    return ft.Column(
        [
            title,
            ft.Divider(),
            ft.ElevatedButton("Refresh Sensors", on_click=lambda e: refresh_data(e)),
            ft.Text("Node 1: Water Quality", size=24, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
            node1_container,
            ft.Container(height=20),
            ft.Text("Node 2: Environment", size=24, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
            node2_container,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
