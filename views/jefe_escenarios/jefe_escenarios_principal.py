import flet as ft

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def jefe_escenarios_principal_view(page: ft.Page):
    return ft.View(
        "/jefe_escenarios/home",
        [
            ft.AppBar(title=ft.Text("Panel Principal - Jefe de Escenarios"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[COLOR1_HEX, COLOR2_HEX]
                ),
                content=ft.Column([
                    ft.Image(src=LOGO_PATH, width=150, height=80),
                    ft.Text("Bienvenido al panel de Jefe de Escenarios", size=20, weight="bold"),
                    ft.Divider(),
                    ft.ListTile(
                        title=ft.Text("🏟️ Gestión de Escenarios y Reservas"),
                        subtitle=ft.Text("Administrar escenarios, sus partes y el calendario de reservas"),
                        on_click=lambda _: page.go("/jefe_escenarios/gestion")
                    ),
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )
