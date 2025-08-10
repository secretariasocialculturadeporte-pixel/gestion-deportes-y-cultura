import flet as ft
import sqlite3
from datetime import datetime

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_clases(page: ft.Page, tenant_id: int, profesor_id: int):
    # --- WIDGETS ---
    nombre_clase = ft.TextField(label="Nombre de la Clase/Tema", width=400)
    proceso_dropdown = ft.Dropdown(label="Proceso Formativo", width=400)
    escenario_dropdown = ft.Dropdown(label="Escenario", width=400)
    # Espacio could be a TextField or a Dropdown loaded based on scenario
    espacio_input = ft.TextField(label="Espacio / Salón", width=400)
    grupo_dropdown = ft.Dropdown(label="Nivel del Grupo", width=400, options=[
        ft.dropdown.Option("Iniciación"),
        ft.dropdown.Option("Intermedio"),
        ft.dropdown.Option("Avanzado"),
        ft.dropdown.Option("Alto Rendimiento")
    ])
    fecha = ft.TextField(label="Fecha", width=200, hint_text="YYYY-MM-DD")
    hora_inicio = ft.TextField(label="Hora Inicio", width=200, hint_text="HH:MM")
    hora_fin = ft.TextField(label="Hora Fin", width=200, hint_text="HH:MM")
    novedad = ft.TextField(label="Descripción / Novedad", multiline=True, width=400)

    mensaje = ft.Text()

    # --- DATABASE INTERACTIONS ---
    def cargar_dependencias():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Cargar procesos formativos del tenant
        cursor.execute("SELECT id, nombre_proceso FROM procesos_formacion WHERE inquilino_id = ?", (tenant_id,))
        proceso_dropdown.options = [ft.dropdown.Option(str(row[0]), row[1]) for row in cursor.fetchall()]

        # Cargar escenarios del tenant
        cursor.execute("SELECT id, nombre FROM escenarios WHERE inquilino_id = ?", (tenant_id,))
        escenario_dropdown.options = [ft.dropdown.Option(str(row[0]), row[1]) for row in cursor.fetchall()]

        conn.close()
        page.update()

    def guardar_clase(e):
        try:
            # Basic validation
            if not all([proceso_dropdown.value, fecha.value, hora_inicio.value, hora_fin.value, escenario_dropdown.value]):
                mensaje.value = "Error: Faltan campos obligatorios."
                mensaje.color = "red"
                page.update()
                return

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clases (inquilino_id, nombre_clase, proceso_id, instructor_id, fecha, hora_inicio, hora_fin, escenario_id, espacio, grupo, novedad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant_id, nombre_clase.value, int(proceso_dropdown.value), profesor_id, fecha.value,
                hora_inicio.value, hora_fin.value, int(escenario_dropdown.value),
                espacio_input.value, grupo_dropdown.value, novedad.value
            ))
            conn.commit()
            mensaje.value = "Clase guardada exitosamente."
            mensaje.color = "green"

            # Clear fields
            nombre_clase.value = ""
            proceso_dropdown.value = None
            escenario_dropdown.value = None
            espacio_input.value = ""
            grupo_dropdown.value = None
            fecha.value = ""
            hora_inicio.value = ""
            hora_fin.value = ""
            novedad.value = ""

        except Exception as ex:
            mensaje.value = f"Error al guardar la clase: {str(ex)}"
            mensaje.color = "red"
        finally:
            if conn:
                conn.close()
            page.update()

    # --- INITIAL LOAD ---
    try:
        cargar_dependencias()
    except Exception as e:
        print(f"Error cargando dependencias para la vista de clases: {e}")
        mensaje.value = "Error al cargar datos iniciales. Asegúrese de que la BD esté configurada."
        mensaje.color = "red"

    # --- VIEW LAYOUT ---
    return ft.View("/profesor_clases", [
        ft.AppBar(title=ft.Text("Gestión y Planeación de Clases"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=140, height=70),
                nombre_clase,
                proceso_dropdown,
                escenario_dropdown,
                espacio_input,
                grupo_dropdown,
                ft.Row([fecha, hora_inicio, hora_fin]),
                novedad,
                ft.ElevatedButton("Guardar Clase", on_click=guardar_clase, icon=ft.icons.SAVE),
                mensaje
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
