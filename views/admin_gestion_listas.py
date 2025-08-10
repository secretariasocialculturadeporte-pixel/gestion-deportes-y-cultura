import flet as ft
import sqlite3

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

# Mapping UI names to DB table names
LISTA_TABLES = {
    "Géneros": "generos",
    "Grupos Etarios": "grupos_etarios",
    "Tipos de Documento": "tipos_documento",
    "Escolaridades": "escolaridades",
    "Discapacidades": "discapacidades",
    "Grupos Poblacionales": "grupos_poblacionales",
    "Barrios": "barrios",
    "Veredas": "veredas",
    "Resguardos": "resguardos",
    "Tipos de Escenario": "tipos_escenario",
}

def admin_gestion_listas(page: ft.Page, tenant_id: int):

    def get_current_table():
        return LISTA_TABLES.get(lista_selector.value)

    def cargar_opciones(e=None):
        table_name = get_current_table()
        if not table_name:
            tabla_opciones.rows = []
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, nombre FROM {table_name} WHERE inquilino_id = ? ORDER BY nombre", (tenant_id,))
            opciones = cursor.fetchall()
            conn.close()

            tabla_opciones.rows = []
            for opt_id, nombre in opciones:
                tabla_opciones.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(nombre)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, i=opt_id: eliminar_opcion(i)),
                            # Edit button can be added here
                        ]))
                    ])
                )
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error cargando opciones: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def agregar_opcion(e):
        table_name = get_current_table()
        new_value = nuevo_valor_input.value.strip()

        if not table_name or not new_value:
            page.snack_bar = ft.SnackBar(ft.Text("Seleccione una lista y escriba un valor."), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} (inquilino_id, nombre) VALUES (?, ?)", (tenant_id, new_value))
            conn.commit()
            conn.close()

            nuevo_valor_input.value = ""
            cargar_opciones() # Refresh table
        except sqlite3.IntegrityError:
            page.snack_bar = ft.SnackBar(ft.Text(f"El valor '{new_value}' ya existe en esta lista."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error guardando opción: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def eliminar_opcion(option_id):
        table_name = get_current_table()
        if not table_name:
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Ensure we only delete from the correct tenant
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ? AND inquilino_id = ?", (option_id, tenant_id))
            conn.commit()
            conn.close()
            cargar_opciones() # Refresh table
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error eliminando opción: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # --- WIDGETS ---
    lista_selector = ft.Dropdown(
        label="Seleccionar Lista para Administrar",
        options=[ft.dropdown.Option(name) for name in LISTA_TABLES.keys()],
        on_change=cargar_opciones
    )
    nuevo_valor_input = ft.TextField(label="Nuevo Valor", expand=True)
    agregar_btn = ft.ElevatedButton("Agregar", icon=ft.icons.ADD, on_click=agregar_opcion)

    tabla_opciones = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Valor Actual")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    return ft.View(
        "/admin/gestion_listas",
        [
            ft.AppBar(title=ft.Text("Gestión de Listas Desplegables"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
                content=ft.Column([
                    ft.Text("Administrar Opciones de Formularios", size=22, weight="bold"),
                    lista_selector,
                    ft.Row([nuevo_valor_input, agregar_btn]),
                    ft.Divider(),
                    ft.Container(content=tabla_opciones, expand=True)
                ], scroll=ft.ScrollMode.AUTO, expand=True)
            )
        ]
    )
