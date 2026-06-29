# dashboard/src/pages/chatbot.py
import flet as ft
from utils.constants import *
from services.api_client import send_chat_message

def ChatbotPage(page: ft.Page):
    title = ft.Text("AI Desalination Assistant (Gemini)", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.colors.BLACK)
    
    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    user_input = ft.TextField(hint_text="Ask about your RO system...", expand=True, on_submit=lambda e: send_message())
    
    def add_message(sender, message, is_user=False):
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(f"{sender}: {message}", selectable=True),
                bgcolor=PRIMARY_DARK if is_user else CARD_DARK,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
                margin=ft.margin.only(bottom=10)
            )
        )
        page.update()

    def send_message(e=None):
        msg = user_input.value
        if not msg:
            return
            
        user_input.value = ""
        add_message("You", msg, is_user=True)
        
        # Add a loading indicator
        loading = ft.ProgressRing(width=20, height=20)
        chat_history.controls.append(loading)
        page.update()
        
        # Send to API
        res = send_chat_message(msg)
        
        # Remove loading indicator
        chat_history.controls.remove(loading)
        
        if res and res.get("status") == "ok":
            add_message("Gemini", res.get("reply", "No reply generated."))
        else:
            add_message("System", "Error communicating with the chatbot service.", is_user=False)
            
    send_button = ft.IconButton(icon=ft.icons.SEND, on_click=send_message)
    
    return ft.Column(
        [
            title,
            ft.Divider(),
            ft.Container(
                content=chat_history,
                expand=True,
                padding=10,
                border=ft.border.all(1, ft.colors.GREY_800),
                border_radius=10
            ),
            ft.Row([user_input, send_button])
        ],
        expand=True
    )
