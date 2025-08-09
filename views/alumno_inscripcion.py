import flet as ft
import sqlite3
from datetime import datetime

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def alumno_inscripcion(page: ft.Page, alumno_id: int):
    clases_disponibles = ft.Dropdown(label="Selecciona una clase para inscribirte", value=None)
    mensaje = ft.Text(value="")

    def cargar_clases():
        clases_disponibles.options = []
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Cargar clases en las que el alumno NO está inscrito
            # Esta consulta asume que las inscripciones son por clase.
            # El modelo de datos puede ser más complejo (inscripción a proceso).
            cursor.execute("""
                SELECT id, nombre_clase FROM clases
                WHERE id NOT IN (SELECT clase_id FROM inscripciones WHERE alumno_id = ?)
            """, (alumno_id,))
            clases = cursor.fetchall()

            if not clases:
                mensaje.value = "No hay nuevas clases disponibles para inscripción."

            clases_disponibles.options = [
                ft.dropdown.Option(str(c[0]), text=f"{c[1]}") for c in clases
            ]
        except Exception as e:
            mensaje.value = f"Error al cargar clases: {e}"
        finally:
            if conn:
                conn.close()
            page.update()

    def inscribirse(e):
        clase_id = clases_disponibles.value
        if clase_id is None:
            mensaje.value = "Por favor selecciona una clase."
            mensaje.color = "red"
        else:
            try:
                conn = sqlite3.connect("formacion.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inscripciones (alumno_id, clase_id, fecha_inscripcion)
                    VALUES (?, ?, ?)
                """, (alumno_id, int(clase_id), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                mensaje.value = "¡Inscripción exitosa!"
                mensaje.color = "green"
                # Recargar la lista para que la clase inscrita ya no aparezca
                cargar_clases()
            except Exception as e:
                mensaje.value = f"Error durante la inscripción: {e}"
                mensaje.color = "red"
            finally:
                if conn:
                    conn.close()
                page.update()

    # Carga inicial
    cargar_clases()

    return ft.View("/alumno_inscripcion", [
        ft.AppBar(title=ft.Text("Inscripción a Clases"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                clases_disponibles,
                ft.ElevatedButton("Inscribirme", on_click=inscribirse, icon=ft.icons.CHECK),
                mensaje
            ])
        )
    ])
