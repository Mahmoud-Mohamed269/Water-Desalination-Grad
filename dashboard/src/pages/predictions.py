# dashboard/src/pages/predictions.py
import flet as ft
from utils.constants import *
from services.api_client import get_predictions

def PredictionsPage(page: ft.Page):
    title = ft.Text("ML Predictions & Analytics", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.colors.BLACK)
    
    content = ft.Column()
    
    def refresh_data(e=None):
        preds = get_predictions()
        content.controls.clear()
        
        if preds and preds.get('status') == 'ok':
            p_data = preds.get('predictions', {})
            wq = p_data.get('water_quality', {})
            ms = p_data.get('membrane_status', {})
            
            content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Water Quality Prediction", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Status: {wq.get('label', 'Unknown')}", size=20, color=SUCCESS_COLOR if wq.get('label') == 'Excellent' else WARNING_COLOR),
                        ft.Text(f"Confidence: {wq.get('confidence', 0)}%"),
                    ]),
                    padding=20,
                    bgcolor=CARD_DARK if page.theme_mode == ft.ThemeMode.DARK else CARD_LIGHT,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                )
            )
            
            content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Membrane Fouling Risk", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Status: {ms.get('label', 'Unknown')}", size=20, color=SUCCESS_COLOR if ms.get('label') == 'Healthy' else DANGER_COLOR),
                        ft.Text(f"Confidence: {ms.get('confidence', 0)}%"),
                    ]),
                    padding=20,
                    bgcolor=CARD_DARK if page.theme_mode == ft.ThemeMode.DARK else CARD_LIGHT,
                    border_radius=10
                )
            )
        else:
            content.controls.append(ft.Text("Unable to fetch ML predictions at this time.", color=DANGER_COLOR))
            
        if e is not None:
            page.update()

    refresh_data(None)

    return ft.Column(
        [
            title,
            ft.Divider(),
            ft.ElevatedButton("Run ML Inference", on_click=lambda e: refresh_data(e)),
            content
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
