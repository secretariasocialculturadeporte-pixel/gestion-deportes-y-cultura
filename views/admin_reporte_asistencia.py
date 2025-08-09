import flet as ft
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

# --- PDF Generation Class ---
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte de Asistencia", ln=True, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align='C')

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def create_table(self, data, headers):
        self.set_font("Arial", "B", 10)
        col_width = self.w / (len(headers) + 1)
        for header in headers:
            self.cell(col_width, 10, header, 1, 0, 'C')
        self.ln()

        self.set_font("Arial", "", 10)
        for row in data:
            for item in row:
                self.cell(col_width, 10, str(item), 1)
            self.ln()

def admin_reporte_asistencia(page: ft.Page):

    def handle_pubsub_message(message):
        if message.get("topic") == "update_attendance_report":
            print("Received attendance report update via PubSub.")
            data = message.get("data", [])
            # Assuming data is a list of dicts
            columnas = list(data[0].keys()) if data else []
            tabla_asistencia.columns = [ft.DataColumn(ft.Text(col)) for col in columnas]
            tabla_asistencia.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(row[col]))) for col in columnas])
                for row in data
            ]
            page.update()

    page.pubsub.subscribe(handle_pubsub_message)

    # --- WIDGETS ---
    tabla_asistencia = ft.DataTable(columns=[], rows=[], expand=True)
    mensaje = ft.Text()

    def cargar_y_mostrar_reporte():
        # This function can still be used for initial loading
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            query = """
                SELECT
                    a.nombre || ' ' || a.apellido AS Alumno,
                    p.nombre_proceso AS Proceso,
                    c.nombre_clase AS Clase,
                    ast.fecha_hora AS Fecha_Asistencia,
                    ast.evidencia_path AS Evidencia
                FROM asistencias ast
                JOIN alumnos a ON ast.alumno_id = a.id
                JOIN clases c ON ast.clase_id = c.id
                JOIN procesos_formacion p ON c.proceso_id = p.id
                ORDER BY ast.fecha_hora DESC
            """
            cursor.execute(query)
            datos = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]

            page.client_storage.set("reporte_asistencia.datos", datos)
            page.client_storage.set("reporte_asistencia.columnas", columnas)

            tabla_asistencia.columns = [ft.DataColumn(ft.Text(col)) for col in columnas]
            tabla_asistencia.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                for row in datos
            ]
        except Exception as e:
            mensaje.value = f"Error al cargar reporte: {e}"
        finally:
            conn.close()
            page.update()

    def descargar_reporte(formato: str):
        datos = page.client_storage.get("reporte_asistencia.datos")
        columnas = page.client_storage.get("reporte_asistencia.columnas")
        if not datos or not columnas:
            mensaje.value = "No hay datos para descargar."
            page.update()
            return

        timestamp = datetime.now().strftime('%Y%m%d')
        ruta_base = f"reporte_asistencia_{timestamp}"

        if formato == "excel":
            df = pd.DataFrame(datos, columns=columnas)
            ruta_descarga = f"{ruta_base}.xlsx"
            df.to_excel(ruta_descarga, index=False)
            mensaje.value = f"Reporte descargado en: {ruta_descarga}"

        elif formato == "pdf":
            pdf = PDF()
            pdf.add_page()
            pdf.chapter_title("Reporte Detallado de Asistencias")
            pdf.create_table(datos, columnas)
            ruta_descarga = f"{ruta_base}.pdf"
            pdf.output(ruta_descarga)
            mensaje.value = f"Reporte descargado en: {ruta_descarga}"

        page.update()

    # --- INITIAL LOAD ---
    cargar_y_mostrar_reporte()

    # --- VIEW LAYOUT ---
    return ft.View("/admin/reporte_asistencia", [
        ft.AppBar(title=ft.Text("Reporte de Asistencia de Alumnos"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Row([
                    ft.ElevatedButton("Descargar Excel", icon=ft.icons.TABLE_CHART, on_click=lambda e: descargar_reporte("excel")),
                    ft.ElevatedButton("Descargar PDF", icon=ft.icons.PICTURE_AS_PDF, on_click=lambda e: descargar_reporte("pdf")),
                ]),
                mensaje,
                ft.Divider(),
                ft.Container(content=tabla_asistencia, expand=True)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
