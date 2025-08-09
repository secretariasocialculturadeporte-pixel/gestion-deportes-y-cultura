import flet as ft
import sqlite3

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_perfil(page: ft.Page, profesor_id: int):
    nombre = ft.TextField(label="Nombre")
    apellido = ft.TextField(label="Apellido")
    correo = ft.TextField(label="Correo Electrónico")
    telefono = ft.TextField(label="Teléfono")

    def cargar_datos():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, apellido, correo, telefono FROM profesores WHERE id = ?", (profesor_id,))
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            nombre.value, apellido.value, correo.value, telefono.value = resultado

    def guardar_datos(e):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profesores
            SET nombre = ?, apellido = ?, correo = ?, telefono = ?
            WHERE id = ?
        """, (nombre.value, apellido.value, correo.value, telefono.value, profesor_id))
        conn.commit()
        conn.close()
        page.snack_bar = ft.SnackBar(ft.Text("Perfil actualizado correctamente"))
        page.snack_bar.open = True
        page.update()

    cargar_datos()

    return ft.View("/profesor_perfil", [
        ft.AppBar(title=ft.Text("Mi Perfil"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Información Personal", size=20, weight="bold"),
                nombre,
                apellido,
                correo,
                telefono,
                ft.ElevatedButton("Guardar Cambios", icon=ft.icons.SAVE, on_click=guardar_datos)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
