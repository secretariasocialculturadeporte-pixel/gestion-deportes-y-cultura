import flet as ft
import json
from agent.agent_service import process_command

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def admin_principal(page: ft.Page):

    def handle_command(e):
        command = command_input.value
        if not command:
            return

        # This is a blocking call. In a real app, you might run this in a separate thread.
        # Also, the API call inside process_command will fail if the API server isn't running.
        # We are assuming it would be running for this test.
        result = process_command(command, page.pubsub)

        # Display the raw result for debugging
        result_text.value = json.dumps(result, indent=2, ensure_ascii=False)
        page.update()

    command_input = ft.TextField(label="Escriba un comando para el agente AI...", expand=True)
    submit_button = ft.ElevatedButton("Enviar", on_click=handle_command, icon=ft.icons.SEND)
    result_text = ft.Text(value="La respuesta del agente aparecerá aquí.", selectable=True)

    return ft.View("/admin_home", [
        ft.AppBar(title=ft.Text("Panel Principal del Administrador"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Bienvenido al panel de administración", size=20, weight="bold"),
                ft.Text("Seleccione una opción para continuar o use el agente AI:", size=16),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("📊 Reporte Demográfico"),
                    subtitle=ft.Text("Ver estadísticas de alumnos por categoría"),
                    on_click=lambda _: page.go("/admin/reporte_demografico")
                ),
                ft.ListTile(
                    title=ft.Text("📋 Reporte de Asistencia"),
                    subtitle=ft.Text("Ver y exportar el historial de asistencias"),
                    on_click=lambda _: page.go("/admin/reporte_asistencia")
                ),
                ft.ListTile(
                    title=ft.Text("✍️ Gestionar Listas"),
                    subtitle=ft.Text("Administrar opciones de los formularios (género, etc.)"),
                    on_click=lambda _: page.go("/admin/gestion_listas")
                ),
                ft.ListTile(
                    title=ft.Text("👥 Gestión de Personal"),
                    subtitle=ft.Text("Crear y administrar usuarios de la empresa"),
                    on_click=lambda _: page.go("/admin/personal")
                ),
                ft.Divider(height=20),
                ft.Text("Asistente de IA", size=18, weight="bold"),
                ft.Row([command_input, submit_button]),
                ft.Container(
                    content=ft.Column([result_text]),
                    padding=10,
                    border=ft.border.all(1, "white"),
                    border_radius=5
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
