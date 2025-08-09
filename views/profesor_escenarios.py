import flet as ft
import sqlite3

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_escenarios(page: ft.Page):
    # --- WIDGETS ---
    nombre_input = ft.TextField(label="Nombre del Escenario", width=400)
    descripcion_input = ft.TextField(label="Descripción", multiline=True, width=400)
    ubicacion_input = ft.TextField(label="Ubicación / Dirección", width=400)
    capacidad_input = ft.TextField(label="Capacidad", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    tipo_input = ft.Dropdown(
        label="Tipo de Escenario",
        options=[], # Will be loaded from DB
        width=400
    )

    tabla_escenarios = ft.DataTable(columns=[], rows=[], expand=True)
    mensaje = ft.Text(visible=False)

    # --- DATABASE FUNCTIONS ---
    def cargar_escenarios():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Load scenario types for the dropdown
        try:
            cursor.execute("SELECT nombre FROM tipos_escenario ORDER BY nombre")
            tipos = cursor.fetchall()
            tipo_input.options = [ft.dropdown.Option(t[0]) for t in tipos]
        except sqlite3.OperationalError:
            # Table might not exist on first run, admin needs to add options
            pass

        # Load existing scenarios into the table
        cursor.execute("SELECT nombre, descripcion, ubicacion, capacidad, tipo FROM escenarios")
        datos = cursor.fetchall()
        conn.close()

        if datos:
            tabla_escenarios.columns = [
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Ubicación")),
                ft.DataColumn(ft.Text("Capacidad")),
                ft.DataColumn(ft.Text("Tipo")),
            ]
            tabla_escenarios.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]) for row in datos
            ]
        else:
            tabla_escenarios.columns = []
            tabla_escenarios.rows = []
        page.update()

    def guardar_escenario(e):
        nombre = nombre_input.value.strip()
        descripcion = descripcion_input.value.strip()
        ubicacion = ubicacion_input.value.strip()
        capacidad = capacidad_input.value.strip()
        tipo = tipo_input.value

        if not all([nombre, ubicacion, capacidad, tipo]):
            mensaje.value = "Los campos Nombre, Ubicación, Capacidad y Tipo son obligatorios."
            mensaje.color = "red"
            mensaje.visible = True
            page.update()
            return

        try:
            capacidad_int = int(capacidad)
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO escenarios (nombre, descripcion, ubicacion, capacidad, tipo)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, ubicacion, capacidad_int, tipo))
            conn.commit()
            conn.close()

            # Limpiar campos y recargar
            nombre_input.value = ""
            descripcion_input.value = ""
            ubicacion_input.value = ""
            capacidad_input.value = ""
            tipo_input.value = None
            mensaje.value = f"Escenario '{nombre}' guardado exitosamente."
            mensaje.color = "green"
            mensaje.visible = True
            cargar_escenarios()
            page.update()

        except ValueError:
            mensaje.value = "La capacidad debe ser un número."
            mensaje.color = "red"
            mensaje.visible = True
            page.update()
        except Exception as ex:
            mensaje.value = f"Error al guardar: {str(ex)}"
            mensaje.color = "red"
            mensaje.visible = True
            page.update()

    # --- INITIAL LOAD ---
    cargar_escenarios()

    # --- VIEW LAYOUT ---
    return ft.View("/profesor_escenarios", [
        ft.AppBar(title=ft.Text("Gestión de Escenarios"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Registrar Nuevo Escenario", size=18, weight="bold"),
                nombre_input,
                descripcion_input,
                ubicacion_input,
                capacidad_input,
                tipo_input,
                ft.ElevatedButton("Guardar Escenario", icon=ft.icons.SAVE, on_click=guardar_escenario),
                mensaje,
                ft.Divider(height=20),
                ft.Text("Escenarios Registrados", size=18, weight="bold"),
                ft.Container(content=tabla_escenarios, expand=True)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
