import flet as ft
import sqlite3
from datetime import datetime
import os

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def almacenista_gestion_elementos(page: ft.Page, almacenista_id: int):
    # --- WIDGETS ---
    # Form for adding a new loan/prestamo
    codigo_input = ft.TextField(label="Código del Elemento")
    descripcion_input = ft.TextField(label="Descripción")
    observaciones_input = ft.TextField(label="Observaciones (Estado inicial)", multiline=True)
    instructores_dropdown = ft.Dropdown(label="Asignar a Instructor")
    foto_picker = ft.FilePicker()
    mensaje_estado = ft.Text()

    # Table to display current loans
    tabla_prestamos = ft.DataTable(columns=[], rows=[], expand=True)

    # --- SETUP ---
    page.overlay.append(foto_picker)

    def cargar_instructores_y_prestamos():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Cargar instructores
        try:
            cursor.execute("SELECT id, nombre || ' ' || apellido FROM profesores")
            instructores_dropdown.options = [ft.dropdown.Option(str(row[0]), row[1]) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading instructors: {e}")

        # Cargar prestamos activos
        try:
            tabla_prestamos.columns = [
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Instructor")),
                ft.DataColumn(ft.Text("Fecha Préstamo")),
                ft.DataColumn(ft.Text("Estado")),
            ]
            cursor.execute("""
                SELECT e.codigo, e.descripcion, p.nombre, pr.fecha_prestamo, pr.estado
                FROM prestamos pr
                JOIN elementos e ON pr.elemento_id = e.id
                JOIN profesores p ON pr.instructor_id = p.id
                WHERE pr.estado = 'En uso'
            """)
            tabla_prestamos.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"Error loading loans: {e}")

        conn.close()
        page.update()

    def guardar_prestamo(e):
        if not all([codigo_input.value, descripcion_input.value, instructores_dropdown.value, foto_picker.result]):
            mensaje_estado.value = "Todos los campos y la foto son obligatorios."
            mensaje_estado.color = "red"
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            # Step 1: Create the element if it doesn't exist, or find it.
            cursor.execute("SELECT id FROM elementos WHERE codigo = ?", (codigo_input.value,))
            elemento = cursor.fetchone()
            if elemento:
                elemento_id = elemento[0]
            else:
                cursor.execute("INSERT INTO elementos (codigo, descripcion) VALUES (?, ?)",
                               (codigo_input.value, descripcion_input.value))
                elemento_id = cursor.lastrowid

            # Step 2: Create the loan record (prestamo)
            foto_path = foto_picker.result.files[0].path # Simplified path
            cursor.execute("""
                INSERT INTO prestamos (elemento_id, instructor_id, almacenista_id, fecha_prestamo, observaciones_prestamo, foto_prestamo, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'En uso')
            """, (
                elemento_id, int(instructores_dropdown.value), almacenista_id,
                datetime.now().strftime('%Y-%m-%d'), observaciones_input.value, foto_path
            ))
            conn.commit()
            mensaje_estado.value = "Préstamo registrado exitosamente."
            mensaje_estado.color = "green"

            # Clear form and reload table
            codigo_input.value = ""
            descripcion_input.value = ""
            observaciones_input.value = ""
            instructores_dropdown.value = None
            cargar_instructores_y_prestamos()

        except Exception as ex:
            mensaje_estado.value = f"Error al guardar: {ex}"
            mensaje_estado.color = "red"
        finally:
            conn.close()
            page.update()

    # --- INITIAL LOAD ---
    cargar_instructores_y_prestamos()

    # --- VIEW LAYOUT ---
    return ft.View("/almacenista/elementos", [
        ft.AppBar(title=ft.Text("Gestión de Préstamo de Elementos"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=140, height=70),
                ft.Text("Registrar Nuevo Préstamo", size=18, weight="bold"),
                codigo_input,
                descripcion_input,
                observaciones_input,
                instructores_dropdown,
                ft.ElevatedButton("Subir Foto del Elemento", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: foto_picker.pick_files(allow_multiple=False)),
                ft.ElevatedButton("Guardar Préstamo", icon=ft.icons.SAVE, on_click=guardar_prestamo),
                mensaje_estado,
                ft.Divider(height=20),
                ft.Text("Préstamos Activos", size=18, weight="bold"),
                ft.Container(content=tabla_prestamos, expand=True)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
