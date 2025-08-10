import flet as ft
import sqlite3
import json

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def audit_log_view(page: ft.Page, tenant_id: int):

    log_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha/Hora")),
            ft.DataColumn(ft.Text("Usuario Actor")),
            ft.DataColumn(ft.Text("Acción")),
            ft.DataColumn(ft.Text("Detalles")),
        ],
        rows=[]
    )

    def load_logs(filter_text=""):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()

            base_query = """
                SELECT a.timestamp, u.nombre_completo, a.accion, a.detalles
                FROM audit_log a
                LEFT JOIN usuarios u ON a.usuario_id_actor = u.id
                WHERE a.inquilino_id = ?
            """
            params = [tenant_id]

            if filter_text:
                base_query += " AND (u.nombre_completo LIKE ? OR a.accion LIKE ?)"
                params.extend([f"%{filter_text}%", f"%{filter_text}%"])

            base_query += " ORDER BY a.timestamp DESC LIMIT 100" # Limit to recent 100 logs

            cursor.execute(base_query, tuple(params))
            logs = cursor.fetchall()
            conn.close()

            log_table.rows = []
            for timestamp, actor, action, details in logs:
                try:
                    # Format the details JSON for readability
                    details_formatted = json.dumps(json.loads(details), indent=2, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    details_formatted = details or ""

                log_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(timestamp)),
                        ft.DataCell(ft.Text(actor or "Sistema")),
                        ft.DataCell(ft.Text(action)),
                        ft.DataCell(ft.Text(details_formatted, font_family="monospace")),
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error loading audit log: {e}")

    def on_filter_change(e):
        load_logs(e.control.value)

    filter_input = ft.TextField(
        label="Filtrar por usuario o acción...",
        on_change=on_filter_change,
        width=400
    )

    # Initial load
    load_logs()

    return ft.View(
        "/admin/audit_log",
        [
            ft.AppBar(title=ft.Text("Registro de Auditoría"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Registro de Auditoría del Sistema", size=22, weight="bold"),
                    filter_input,
                    ft.Divider(),
                    ft.Container(content=log_table, expand=True)
                ], scroll=ft.ScrollMode.ALWAYS) # Ensure the main column scrolls
            )
        ]
    )
