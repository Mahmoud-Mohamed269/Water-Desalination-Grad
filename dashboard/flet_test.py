import flet as ft
from flet import AppView

def main(page: ft.Page):
    page.title = "Flet Test"
    page.bgcolor = "#0F0F1A"
    page.add(
        ft.Column([
            ft.Text("✅ Flet is working!", size=40, color="green", weight=ft.FontWeight.BOLD),
            ft.Text("If you see this, Flet web mode is functional.", size=18, color="white"),
            ft.ElevatedButton("Click Me!", on_click=lambda e: page.add(ft.Text("Button clicked!", color="cyan"))),
        ])
    )

ft.app(target=main, view=AppView.WEB_BROWSER)
