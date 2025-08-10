import flet as ft
import sqlite3
import secrets

def ccos_main_view(page: ft.Page):

    # --- UI Controls for Stats ---
    stats_total_tenants = ft.Text("...", size=24, weight="bold")
    stats_total_users = ft.Text("...", size=24, weight="bold")
    stats_plan_distribution = ft.Text("...", size=16)

    # --- Backend Logic for Actions ---
    def update_tenant_status(tenant_id: int, new_status: int):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE inquilinos SET activo = ? WHERE id = ?", (new_status, tenant_id))
            conn.commit()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text(f"Estado del inquilino {tenant_id} actualizado."), bgcolor="green")
            load_tenants() # Refresh the table
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar estado: {e}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()

    def regenerate_api_key(tenant_id: int):
        try:
            new_key = secrets.token_hex(16)
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE inquilinos SET api_key = ? WHERE id = ?", (new_key, tenant_id))
            conn.commit()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text(f"Nueva API Key generada para el inquilino {tenant_id}."), bgcolor="green")
            load_tenants() # Refresh the table
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al regenerar la clave: {e}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()


    # --- UI Definition ---
    tenants_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre Empresa")),
            ft.DataColumn(ft.Text("Plan")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("API Key")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def load_global_stats(cursor):
        """Helper to load and display global stats."""
        # Total Active Tenants
        cursor.execute("SELECT COUNT(*) FROM inquilinos WHERE activo = 1")
        stats_total_tenants.value = str(cursor.fetchone()[0])
        # Total Users
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        stats_total_users.value = str(cursor.fetchone()[0])
        # Plan Distribution
        cursor.execute("SELECT plan, COUNT(*) FROM inquilinos GROUP BY plan")
        dist = cursor.fetchall()
        stats_plan_distribution.value = "\n".join([f"{row[0]}: {row[1]}" for row in dist])

    def load_tenants():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Load stats
            load_global_stats(cursor)
            cursor.execute("SELECT id, nombre_empresa, plan, activo, api_key FROM inquilinos ORDER BY id")
            tenants = cursor.fetchall()
            conn.close()

            tenants_table.rows = []
            for t in tenants:
                tenant_id, nombre, plan, activo, api_key = t
                status_text = "Activo" if activo else "Inactivo"
                status_color = "green" if activo else "red"

                actions = ft.Row([
                    ft.IconButton(
                        icon=ft.icons.PLAY_ARROW, tooltip="Activar", icon_color="green",
                        on_click=lambda e, tid=tenant_id: update_tenant_status(tid, 1),
                        disabled=activo
                    ),
                    ft.IconButton(
                        icon=ft.icons.PAUSE, tooltip="Desactivar", icon_color="orange",
                        on_click=lambda e, tid=tenant_id: update_tenant_status(tid, 0),
                        disabled=not activo
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH, tooltip="Regenerar API Key",
                        on_click=lambda e, tid=tenant_id: regenerate_api_key(tid)
                    ),
                ])

                tenants_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(tenant_id))),
                        ft.DataCell(ft.Text(nombre)),
                        ft.DataCell(ft.Text(plan)),
                        ft.DataCell(ft.Text(status_text, color=status_color)),
                        ft.DataCell(ft.Text(api_key, font_family="monospace", selectable=True)),
                        ft.DataCell(actions),
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error loading tenants: {e}")

    # Initial load
    load_tenants()

    dashboard_row = ft.Row(
        controls=[
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Empresas Activas"), stats_total_tenants]))),
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Usuarios Totales"), stats_total_users]))),
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Distribución de Planes"), stats_plan_distribution]))),
        ]
    )

    return ft.View(
        "/ccos/home",
        [
            ft.AppBar(title=ft.Text("Centro de Control de Operaciones y Suscripciones (CCOS)")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Dashboard Global", size=22, weight="bold"),
                    dashboard_row,
                    ft.Divider(height=30),
                    ft.Text("Gestión de Inquilinos", size=22, weight="bold"),
                    ft.Container(content=tenants_table, expand=True, border=ft.border.all(1, "grey"), border_radius=5),
                ], scroll=ft.ScrollMode.ALWAYS)
            )
        ]
    )
