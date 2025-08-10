import flet as ft
import sqlite3

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_perfil(page: ft.Page, usuario_id: int, tenant_id: int):
    # We now use usuario_id and tenant_id for consistency
    nombre_completo = ft.TextField(label="Nombre Completo")
    correo = ft.TextField(label="Correo Electrónico")
    telefono = ft.TextField(label="Teléfono")
    area = ft.TextField(label="Área Asignada")

    def cargar_datos():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Query both usuarios and profesores table
        cursor.execute("""
            SELECT u.nombre_completo, u.correo, p.telefono, p.area
            FROM usuarios u
            JOIN profesores p ON u.id = p.usuario_id
            WHERE u.id = ? AND u.inquilino_id = ?
        """, (usuario_id, tenant_id))
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            nombre_completo.value, correo.value, telefono.value, area.value = resultado

    def guardar_datos(e):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Update both tables in a transaction
        try:
            cursor.execute("""
                UPDATE usuarios SET nombre_completo = ?, correo = ?
                WHERE id = ? AND inquilino_id = ?
            """, (nombre_completo.value, correo.value, usuario_id, tenant_id))

            cursor.execute("""
                UPDATE profesores SET telefono = ?, area = ?
                WHERE usuario_id = ? AND inquilino_id = ?
            """, (telefono.value, area.value, usuario_id, tenant_id))

            conn.commit()
            page.snack_bar = ft.SnackBar(ft.Text("Perfil actualizado correctamente"), bgcolor="green")
        except Exception as ex:
            conn.rollback()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor="red")
        finally:
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
