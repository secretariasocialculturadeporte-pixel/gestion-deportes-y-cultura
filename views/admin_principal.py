import flet as ft
import json
from agent.agent_service import process_command_langchain

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def admin_principal(page: ft.Page, tenant_id: int): # Now needs tenant_id

    def handle_command(e):
        command = command_input.value
        if not command:
            return

        # Show a "thinking" message
        result_text.value = "El agente está pensando..."
        page.update()

        # In a real app, you'd run this in a thread to avoid blocking the UI
        result = process_command_langchain(command, tenant_id, page.pubsub)

        # The PubSub system will handle UI updates for successful tool calls.
        # This text area will show the final friendly response from the agent.
        if "error" in result:
            result_text.value = f"Error: {result['error']}\nDetalles: {result.get('details', '')}"
        else:
            result_text.value = result.get("agent_response", "No se recibió respuesta del agente.")

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
                ft.ListTile(
                    title=ft.Text("🏛️ Gestión de Áreas"),
                    subtitle=ft.Text("Asignar jefes a las áreas de Cultura y Deportes"),
                    on_click=lambda _: page.go("/admin/areas")
                ),
                ft.ListTile(
                    title=ft.Text("🤖 Configuración de IA"),
                    subtitle=ft.Text("Configura tu API Key de Google AI Studio"),
                    on_click=lambda _: page.go("/admin/configuracion_ia")
                ),
                ft.ListTile(
                    title=ft.Text("🛡️ Registro de Auditoría"),
                    subtitle=ft.Text("Ver el registro de acciones importantes en el sistema"),
                    on_click=lambda _: page.go("/admin/audit_log")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.CREDIT_CARD),
                    title=ft.Text("Suscripción y Facturación"),
                    subtitle=ft.Text("Ver el estado de tu plan y tu historial de pagos"),
                    on_click=lambda _: page.go("/admin/suscripcion")
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
