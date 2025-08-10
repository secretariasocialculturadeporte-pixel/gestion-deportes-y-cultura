import flet as ft
import sqlite3

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

class GestionEscenariosView:
    def __init__(self, page: ft.Page, tenant_id: int):
        self.page = page
        self.tenant_id = tenant_id

        # --- Main UI Controls ---
        self.lista_escenarios = ft.ListView(expand=True, spacing=10)
        self.partes_escenario_column = ft.Column()
        self.selected_scenario_id = None
        self.selected_scenario_name = ft.Text(weight="bold")

        # --- Dialog for adding parts ---
        self.nombre_parte_input = ft.TextField(label="Nombre de la Parte (ej. Cancha A)")
        self.descripcion_parte_input = ft.TextField(label="Descripción")
        self.capacidad_parte_input = ft.TextField(label="Capacidad", keyboard_type=ft.KeyboardType.NUMBER)

        self.dialogo_parte = ft.AlertDialog(
            modal=True,
            title=ft.Text("Añadir Nueva Parte al Escenario"),
            content=ft.Column([
                self.nombre_parte_input,
                self.descripcion_parte_input,
                self.capacidad_parte_input
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=self.guardar_nueva_parte),
            ]
        )
        self.page.dialog = self.dialogo_parte

    def cargar_escenarios(self):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM scenarios WHERE inquilino_id = ?", (self.tenant_id,))
        escenarios = cursor.fetchall()
        conn.close()

        self.lista_escenarios.controls = []
        for esc_id, nombre in escenarios:
            self.lista_escenarios.controls.append(
                ft.ListTile(
                    title=ft.Text(nombre),
                    leading=ft.Icon(ft.icons.STADIUM),
                    on_click=self.seleccionar_escenario,
                    data=(esc_id, nombre)
                )
            )
        self.page.update()

    def seleccionar_escenario(self, e):
        self.selected_scenario_id, self.selected_scenario_name.value = e.control.data
        self.cargar_partes_escenario()

    def cargar_partes_escenario(self):
        if not self.selected_scenario_id:
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre_parte, descripcion, capacidad FROM escenario_partes WHERE escenario_id = ? AND inquilino_id = ?",
            (self.selected_scenario_id, self.tenant_id)
        )
        partes = cursor.fetchall()
        conn.close()

        rows = []
        for parte_id, nombre, desc, cap in partes:
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nombre)),
                    ft.DataCell(ft.Text(desc)),
                    ft.DataCell(ft.Text(str(cap))),
                    ft.DataCell(ft.IconButton(
                        icon=ft.icons.CALENDAR_MONTH,
                        tooltip="Ver/Gestionar Reservas",
                        on_click=lambda e, pid=parte_id: self.page.go(f"/jefe_escenarios/reservas/{pid}")
                    ))
                ])
            )

        self.partes_escenario_column.controls = [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre Parte")),
                    ft.DataColumn(ft.Text("Descripción")),
                    ft.DataColumn(ft.Text("Capacidad")),
                    ft.DataColumn(ft.Text("Reservas")),
                ],
                rows=rows
            )
        ]
        self.page.update()

    def abrir_dialogo_parte(self, e):
        self.dialogo_parte.open = True
        self.page.update()

    def cerrar_dialogo(self, e):
        self.dialogo_parte.open = False
        self.page.update()

    def guardar_nueva_parte(self, e):
        if not self.nombre_parte_input.value or not self.selected_scenario_id:
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO escenario_partes (inquilino_id, escenario_id, nombre_parte, descripcion, capacidad) VALUES (?, ?, ?, ?, ?)",
            (
                self.tenant_id, self.selected_scenario_id, self.nombre_parte_input.value,
                self.descripcion_parte_input.value, int(self.capacidad_parte_input.value or 0)
            )
        )
        conn.commit()
        conn.close()

        # Clear inputs and close dialog
        self.nombre_parte_input.value = ""
        self.descripcion_parte_input.value = ""
        self.capacidad_parte_input.value = ""
        self.cerrar_dialogo(e)
        self.cargar_partes_escenario()

    def build(self):
        self.cargar_escenarios()
        return ft.View(
            "/jefe_escenarios/gestion",
            [
                ft.AppBar(title=ft.Text("Gestión Avanzada de Escenarios"), bgcolor=COLOR2_HEX),
                ft.Row(
                    [
                        # Panel Izquierdo: Lista de Escenarios
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Escenarios", size=18, weight="bold"),
                                self.lista_escenarios
                            ]),
                            width=300,
                            padding=10,
                            border=ft.border.only(right=ft.border.BorderSide(1, "grey"))
                        ),
                        # Panel Derecho: Detalles y Partes
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    self.selected_scenario_name,
                                    ft.ElevatedButton("Añadir Parte", icon=ft.icons.ADD, on_click=self.abrir_dialogo_parte)
                                ]),
                                ft.Divider(),
                                self.partes_escenario_column
                            ]),
                            expand=True,
                            padding=10
                        )
                    ],
                    expand=True
                )
            ]
        )

# Wrapper function to be called by the router
def gestion_escenarios_avanzado_view(page: ft.Page, tenant_id: int):
    view_instance = GestionEscenariosView(page, tenant_id)
    return view_instance.build()
