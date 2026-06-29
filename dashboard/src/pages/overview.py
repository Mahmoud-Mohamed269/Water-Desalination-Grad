# dashboard/src/pages/overview.py
import flet as ft
from utils.constants import *
from services.api_client import get_live_sensors, get_predictions

def OverviewPage(page: ft.Page):
    
    def fetch_data():
        sensors = get_live_sensors()
        preds = get_predictions()
        return sensors, preds

    # We will build a simple UI that shows some cards
    # Since this is synchronous, let's just create the layout first
    
    title = ft.Text("System Overview", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.colors.BLACK)
    
    data_container = ft.Column()
    
    def refresh_data(e=None):
        sensors, preds = fetch_data()
        data_container.controls.clear()
        
        if sensors:
            data_container.controls.append(ft.Text("Live Status: ONLINE", color=SUCCESS_COLOR))
            # Just simple text for overview
            data_container.controls.append(ft.Text(f"Recovery Rate: {sensors.get('recovery_rate', 72.0)}%"))
        else:
            data_container.controls.append(ft.Text("Live Status: OFFLINE", color=DANGER_COLOR))
            
        if preds and preds.get('status') == 'ok':
            p_data = preds.get('predictions', {})
            wq = p_data.get('water_quality', {}).get('label', 'Unknown')
            ms = p_data.get('membrane_status', {}).get('label', 'Unknown')
            data_container.controls.append(ft.Text(f"Water Quality: {wq}", size=20, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR if wq == 'Excellent' else WARNING_COLOR))
            data_container.controls.append(ft.Text(f"Membrane Status: {ms}", size=20, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR if ms == 'Healthy' else WARNING_COLOR))
        
        if e is not None:
            page.update()

    # Initial load
    refresh_data(None)
    
    return ft.Column(
        [
            title,
            ft.Divider(),
            ft.ElevatedButton("Refresh Data", on_click=lambda e: refresh_data(e)),
            data_container
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
