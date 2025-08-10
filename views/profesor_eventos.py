import flet as ft
import sqlite3
from datetime import datetime

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_eventos(page: ft.Page, tenant_id: int, profesor_id: int):
    nombre_evento = ft.TextField(label="Nombre del Evento")
    tipo_evento = ft.Dropdown(
        label="Tipo de Evento",
        options=[
            ft.dropdown.Option("Municipal"),
            ft.dropdown.Option("Nacional")
        ]
    )
    fecha_evento = ft.TextField(label="Fecha del Evento (YYYY-MM-DD)")
    descripcion_evento = ft.TextField(label="Descripción", multiline=True)

    mensaje_confirmacion = ft.Text("", color="green")

    def guardar_evento(e):
        if not all([nombre_evento.value, tipo_evento.value, fecha_evento.value]):
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, complete todos los campos obligatorios."))
            page.snack_bar.open = True
            page.update()
            return

        try:
            # Just validating the format, not using the parsed date object
            datetime.strptime(fecha_evento.value, "%Y-%m-%d")
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Formato de fecha inválido. Use YYYY-MM-DD."))
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Table 'eventos' will be created by the setup script
        cursor.execute("""
            INSERT INTO eventos (inquilino_id, nombre, tipo, fecha, descripcion, creado_por_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tenant_id, nombre_evento.value, tipo_evento.value, fecha_evento.value, descripcion_evento.value, profesor_id))
        conn.commit()
        conn.close()

        mensaje_confirmacion.value = "Evento registrado exitosamente."
        # Clear fields
        nombre_evento.value = ""
        tipo_evento.value = None
        fecha_evento.value = ""
        descripcion_evento.value = ""
        page.update()

    return ft.View("/profesor_eventos", [
        ft.AppBar(title=ft.Text("Gestión de Eventos"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                nombre_evento,
                tipo_evento,
                fecha_evento,
                descripcion_evento,
                ft.ElevatedButton("Guardar Evento", icon=ft.icons.SAVE, on_click=guardar_evento),
                mensaje_confirmacion
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
