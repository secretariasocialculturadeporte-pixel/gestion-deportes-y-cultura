import flet as ft

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def jefe_area_principal_view(page: ft.Page):
    return ft.View("/jefe_area/home", [
        ft.AppBar(title=ft.Text("Panel Principal - Jefe de Área"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Bienvenido al panel de Jefe de Área", size=20, weight="bold"),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("👥 Gestión de mi Equipo"),
                    subtitle=ft.Text("Crear y administrar coordinadores y profesores"),
                    on_click=lambda _: page.go("/jefe_area/equipo")
                ),
                ft.ListTile(
                    title=ft.Text("📈 Panel de Análisis"),
                    subtitle=ft.Text("Ver análisis y reportes de datos de tu área"),
                    on_click=lambda _: page.go("/jefe_area/analisis")
                ),
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
