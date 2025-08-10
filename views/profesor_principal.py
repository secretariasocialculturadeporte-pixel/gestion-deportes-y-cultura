import flet as ft
import pandas as pd
import sqlite3
from datetime import datetime

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_principal(page: ft.Page, tenant_id: int, profesor_id: int):

    def handle_export_asistencia(e):
        try:
            conn = sqlite3.connect("formacion.db")
            query = """
                SELECT
                    u.nombre_completo AS Alumno,
                    c.nombre_clase AS Clase,
                    a.fecha_hora AS Fecha_Asistencia
                FROM asistencias a
                JOIN clases c ON a.clase_id = c.id
                JOIN usuarios u ON a.alumno_id = u.id
                WHERE c.instructor_id = ? AND a.inquilino_id = ?
                ORDER BY a.fecha_hora DESC
            """
            df = pd.read_sql_query(query, conn, params=(profesor_id, tenant_id))
            conn.close()

            if df.empty:
                page.snack_bar = ft.SnackBar(ft.Text("No tienes datos de asistencia para exportar."), bgcolor="orange")
            else:
                filename = f"reporte_asistencia_prof_{profesor_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                df.to_excel(filename, index=False)
                page.snack_bar = ft.SnackBar(ft.Text(f"Reporte descargado como {filename}"), bgcolor="green")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()

    return ft.View("/profesor_home", [
        ft.AppBar(title=ft.Text("Panel Principal del Profesor"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Bienvenido al sistema de formación cultural y deportiva", size=20, weight="bold"),
                ft.Text("Seleccione una opción para continuar", size=16),
                ft.Divider(),
                ft.ListTile(
                    title=ft.Text("👥 Mi perfil"),
                    subtitle=ft.Text("Ver y actualizar mi información"),
                    on_click=lambda _: page.go("/profesor_perfil")
                ),
                ft.ListTile(
                    title=ft.Text("📆 Gestión de eventos"),
                    subtitle=ft.Text("Crear o consultar eventos culturales o deportivos"),
                    on_click=lambda _: page.go("/profesor_eventos")
                ),
                ft.ListTile(
                    title=ft.Text("📚 Gestión de Clases"),
                    subtitle=ft.Text("Crear y gestionar tus clases"),
                    on_click=lambda _: page.go("/profesor_clases")
                ),
                ft.ListTile(
                    title=ft.Text("📊 Descargar Reporte de Asistencia"),
                    subtitle=ft.Text("Exportar un listado de todas tus asistencias a Excel"),
                    leading=ft.Icon(ft.icons.DOWNLOAD),
                    on_click=handle_export_asistencia
                ),
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
