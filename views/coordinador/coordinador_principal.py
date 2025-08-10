import flet as ft
import sqlite3
import pandas as pd
from datetime import datetime

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def coordinador_principal_view(page: ft.Page, tenant_id: int, coordinador_id: int):

    def handle_export_excel(e):
        try:
            conn = sqlite3.connect("formacion.db")
            # This query gets all professors managed by this coordinator
            # and then aggregates their class and attendance data.
            query = """
                SELECT
                    u_prof.nombre_completo AS Profesor,
                    p.area AS Area,
                    COUNT(DISTINCT c.id) AS Total_Clases,
                    SUM(strftime('%s', c.hora_fin) - strftime('%s', c.hora_inicio)) / 3600.0 AS Horas_Totales,
                    COUNT(a.id) AS Total_Asistencias
                FROM usuarios u_coord
                JOIN usuarios u_prof ON u_prof.reporta_a_usuario_id = u_coord.id
                JOIN profesores p ON u_prof.id = p.usuario_id
                LEFT JOIN clases c ON c.instructor_id = p.usuario_id AND c.inquilino_id = u_coord.inquilino_id
                LEFT JOIN asistencias a ON a.clase_id = c.id AND a.inquilino_id = u_coord.inquilino_id
                WHERE u_coord.id = ? AND u_coord.inquilino_id = ? AND u_prof.rol = 'profesor'
                GROUP BY u_prof.nombre_completo, p.area
            """
            df = pd.read_sql_query(query, conn, params=(coordinador_id, tenant_id))
            conn.close()

            if df.empty:
                page.snack_bar = ft.SnackBar(ft.Text("No hay datos para exportar."), bgcolor="orange")
            else:
                filename = f"reporte_coordinador_{coordinador_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                df.to_excel(filename, index=False)
                page.snack_bar = ft.SnackBar(ft.Text(f"Reporte descargado como {filename}"), bgcolor="green")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()

    return ft.View(
        "/coordinador/home",
        [
            ft.AppBar(title=ft.Text("Panel Principal - Coordinador"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                expand=True,
                gradient=ft.LinearGradient(colors=[COLOR1_HEX, COLOR2_HEX]),
                content=ft.Column([
                    ft.Image(src=LOGO_PATH, width=150, height=80),
                    ft.Text("Bienvenido al panel de Coordinador", size=20, weight="bold"),
                    ft.Divider(),
                    ft.ElevatedButton(
                        "Descargar Reporte de Profesores",
                        icon=ft.icons.DOWNLOAD,
                        on_click=handle_export_excel
                    ),
                    # Other coordinator-specific controls can be added here
                ])
            )
        ]
    )
