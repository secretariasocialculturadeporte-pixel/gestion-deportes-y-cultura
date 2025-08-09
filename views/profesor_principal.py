import flet as ft

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_principal(page: ft.Page):
    return ft.View("/profesor_home", [
        ft.AppBar(title=ft.Text("Panel Principal del Profesor"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Bienvenido al sistema de formación cultural y deportiva", size=20, weight="bold"),
                ft.Text("Seleccione una opción para continuar", size=16),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("👥 Mi perfil"),
                    subtitle=ft.Text("Ver y actualizar mi información"),
                    on_click=lambda _: page.go("/profesor_perfil")
                ),
                ft.ListTile(
                    title=ft.Text("📆 Gestión de eventos"),
                    subtitle=ft.Text("Crear o consultar eventos culturales o deportivos"),
                    on_click=lambda _: page.go("/profesor_eventos")
                ),
                ft.ListTile(
                    title=ft.Text("📚 Procesos de formación"),
                    subtitle=ft.Text("Crear y gestionar procesos de formación"),
                    on_click=lambda _: page.go("/profesor_procesos_formacion")
                ),
                ft.ListTile(
                    title=ft.Text("📊 Reportes"),
                    subtitle=ft.Text("Ver reportes y descargar listados"),
                    on_click=lambda _: page.go("/profesor_reportes")
                ),
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
