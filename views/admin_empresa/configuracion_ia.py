import flet as ft
import sqlite3

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def configuracion_ia_view(page: ft.Page, tenant_id: int):

    google_api_key_input = ft.TextField(
        label="Tu API Key de Google AI Studio",
        password=True,
        can_reveal_password=True,
        width=500
    )
    mensaje = ft.Text()

    def load_key():
        """Load the existing key to show it's saved (optional, could be a security risk)."""
        # For better security, we don't display the key. We just show a placeholder.
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT google_api_key FROM inquilinos WHERE id = ?", (tenant_id,))
        key = cursor.fetchone()[0]
        conn.close()
        if key:
            google_api_key_input.value = "******************" # Placeholder
            mensaje.value = "Ya tienes una API key guardada."
        else:
            mensaje.value = "No se ha configurado una API key."
        page.update()

    def save_key(e):
        new_key = google_api_key_input.value
        if not new_key or new_key == "******************":
            mensaje.value = "Por favor, introduce una nueva clave."
            mensaje.color = "red"
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inquilinos SET google_api_key = ? WHERE id = ?",
                (new_key, tenant_id)
            )
            conn.commit()
            conn.close()
            mensaje.value = "API Key guardada con éxito."
            mensaje.color = "green"
            google_api_key_input.value = "******************"
        except Exception as ex:
            mensaje.value = f"Error al guardar la clave: {ex}"
            mensaje.color = "red"

        page.update()

    # Initial load
    load_key()

    return ft.View(
        "/admin/configuracion_ia",
        [
            ft.AppBar(title=ft.Text("Configuración de IA"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Configuración de Inteligencia Artificial", size=22, weight="bold"),
                    ft.Text("Introduce tu clave de API de Google AI Studio para habilitar las funciones avanzadas del agente de IA."),
                    google_api_key_input,
                    ft.ElevatedButton("Guardar Clave", icon=ft.icons.SAVE, on_click=save_key),
                    mensaje
                ])
            )
        ]
    )
