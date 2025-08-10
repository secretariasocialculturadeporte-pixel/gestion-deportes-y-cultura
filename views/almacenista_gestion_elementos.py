import flet as ft
import sqlite3
from datetime import datetime
import os

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def almacenista_gestion_elementos(page: ft.Page, tenant_id: int, jefe_almacen_id: int):

    # Determine the area of this almacenista's manager (jefe_area)
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ja.area_responsabilidad
        FROM usuarios u
        JOIN jefes_area ja ON u.reporta_a_usuario_id = ja.usuario_id
        WHERE u.id = ?
    """, (jefe_almacen_id,))
    result = cursor.fetchone()
    user_area = result[0] if result else None
    conn.close()

    if not user_area:
        # If user has no area, they can't manage anything. Return a disabled view.
        return ft.View("/almacenista/elementos", [ft.AppBar(title=ft.Text("Error")), ft.Text("Este usuario no está asignado a un área (Cultura o Deportes).")])

    # --- WIDGETS ---
    # Form for adding a new loan/prestamo
    codigo_input = ft.TextField(label=f"Código del Elemento ({user_area})")
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

        # Cargar instructores del area
        try:
            cursor.execute("""
                SELECT u.id, u.nombre_completo FROM usuarios u
                JOIN profesores p ON u.id = p.usuario_id
                WHERE u.inquilino_id = ? AND p.area = ?
            """, (tenant_id, user_area))
            instructores_dropdown.options = [ft.dropdown.Option(str(row[0]), row[1]) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading instructors: {e}")

        # Cargar prestamos activos del area
        try:
            tabla_prestamos.columns = [
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Instructor")),
                ft.DataColumn(ft.Text("Fecha Préstamo")),
                ft.DataColumn(ft.Text("Estado")),
            ]
            cursor.execute("""
                SELECT e.codigo, e.descripcion, u.nombre_completo, pr.fecha_prestamo, pr.estado
                FROM prestamos pr
                JOIN elementos e ON pr.elemento_id = e.id
                JOIN usuarios u ON pr.instructor_id = u.id
                WHERE pr.estado = 'En uso' AND pr.inquilino_id = ? AND pr.area = ?
            """, (tenant_id, user_area))
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
            # Step 1: Create the element if it doesn't exist for this tenant and area, or find it.
            cursor.execute("SELECT id FROM elementos WHERE codigo = ? AND inquilino_id = ? AND area = ?", (codigo_input.value, tenant_id, user_area))
            elemento = cursor.fetchone()
            if elemento:
                elemento_id = elemento[0]
            else:
                cursor.execute("INSERT INTO elementos (inquilino_id, codigo, descripcion, area) VALUES (?, ?, ?, ?)",
                               (tenant_id, codigo_input.value, descripcion_input.value, user_area))
                elemento_id = cursor.lastrowid

            # Step 2: Create the loan record (prestamo) for this tenant and area
            foto_path = foto_picker.result.files[0].path # Simplified path
            cursor.execute("""
                INSERT INTO prestamos (inquilino_id, elemento_id, instructor_id, almacenista_id, fecha_prestamo, observaciones_prestamo, foto_prestamo, estado, area)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'En uso', ?)
            """, (
                tenant_id, elemento_id, int(instructores_dropdown.value), jefe_almacen_id,
                datetime.now().strftime('%Y-%m-%d'), observaciones_input.value, foto_path, user_area
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
                ft.Container(content=tabla_prestamos, expand=True),
                ft.Divider(),
                ft.ElevatedButton(
                    "Descargar Historial de Movimientos",
                    icon=ft.icons.DOWNLOAD,
                    on_click=lambda e: handle_export_movimientos(e)
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])

    def handle_export_movimientos(e):
        try:
            conn = sqlite3.connect("formacion.db")
            query = """
                SELECT
                    e.codigo AS Codigo_Elemento,
                    e.descripcion AS Descripcion,
                    u_prof.nombre_completo AS Asignado_A,
                    pr.fecha_prestamo,
                    pr.estado,
                    pr.fecha_entrega,
                    pr.observaciones_prestamo,
                    pr.observaciones_entrega
                FROM prestamos pr
                JOIN elementos e ON pr.elemento_id = e.id
                JOIN usuarios u_prof ON pr.instructor_id = u_prof.id
                WHERE pr.inquilino_id = ? AND pr.area = ?
                ORDER BY pr.fecha_prestamo DESC
            """
            df = pd.read_sql_query(query, conn, params=(tenant_id, user_area))
            conn.close()

            if df.empty:
                page.snack_bar = ft.SnackBar(ft.Text("No hay datos de movimientos para exportar."), bgcolor="orange")
            else:
                filename = f"reporte_movimientos_{user_area}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                df.to_excel(filename, index=False)
                page.snack_bar = ft.SnackBar(ft.Text(f"Reporte descargado como {filename}"), bgcolor="green")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()
