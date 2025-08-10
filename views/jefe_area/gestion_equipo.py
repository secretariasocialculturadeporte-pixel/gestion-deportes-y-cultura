import flet as ft
import sqlite3
from views.login import hash_password

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def gestion_equipo_view(page: ft.Page, tenant_id: int, jefe_area_id: int):

    # --- DIALOG FOR CREATING USER ---
    def crear_dialogo_subordinado(rol_a_crear: str):
        nombre_completo_input = ft.TextField(label="Nombre Completo")
        nombre_usuario_input = ft.TextField(label="Nombre de Usuario")
        password_input = ft.TextField(label="Contraseña Temporal", password=True, can_reveal_password=True)
        correo_input = ft.TextField(label="Correo Electrónico")

        def guardar_nuevo_usuario(e):
            if not all([nombre_completo_input.value, nombre_usuario_input.value, password_input.value]):
                # Show error
                return

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            try:
                # Get the area of the current Jefe de Área
                cursor.execute("SELECT area_responsabilidad FROM jefes_area WHERE usuario_id = ?", (jefe_area_id,))
                area_jefe = cursor.fetchone()[0]
                if not area_jefe:
                    print("Error: El jefe de área no tiene un área asignada.")
                    conn.close()
                    return

                # Insert into usuarios table
                cursor.execute("""
                    INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, reporta_a_usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    tenant_id, nombre_usuario_input.value, hash_password(password_input.value),
                    rol_a_crear, nombre_completo_input.value, correo_input.value, jefe_area_id
                ))
                new_user_id = cursor.lastrowid

                # Insert into role-specific table with the correct area
                if rol_a_crear == 'coordinador':
                    cursor.execute("INSERT INTO coordinadores (usuario_id, inquilino_id, jefe_area_id) VALUES (?, ?, ?)",
                                   (new_user_id, tenant_id, jefe_area_id))
                elif rol_a_crear == 'profesor':
                     cursor.execute("INSERT INTO profesores (usuario_id, inquilino_id, area) VALUES (?, ?, ?)",
                                   (new_user_id, tenant_id, area_jefe))
                elif rol_a_crear == 'jefe_almacen':
                     cursor.execute("INSERT INTO jefes_almacen (usuario_id, inquilino_id) VALUES (?, ?)",
                                   (new_user_id, tenant_id)) # The area is implicit via the manager
                elif rol_a_crear == 'jefe_escenarios':
                     cursor.execute("INSERT INTO jefes_escenarios (usuario_id, inquilino_id) VALUES (?, ?)",
                                   (new_user_id, tenant_id))

                conn.commit()
                page.dialog.open = False
                cargar_equipo() # Refresh the user list
            except Exception as ex:
                print(f"Error creating subordinate: {ex}")
            finally:
                conn.close()
                page.update()

        return ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Crear Nuevo {rol_a_crear.replace('_', ' ').title()}"),
            content=ft.Column([
                nombre_completo_input, nombre_usuario_input, password_input, correo_input
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Guardar", on_click=guardar_nuevo_usuario),
            ]
        )

    def handle_crear_subordinado(e, rol):
        page.dialog = crear_dialogo_subordinado(rol)
        page.dialog.open = True
        page.update()

    # --- MAIN VIEW WIDGETS ---
    tabla_equipo = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre Completo")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Correo")),
        ],
        rows=[]
    )

    def cargar_equipo():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nombre_completo, rol, correo FROM usuarios WHERE inquilino_id = ? AND reporta_a_usuario_id = ?",
                (tenant_id, jefe_area_id)
            )
            equipo = cursor.fetchall()
            conn.close()

            tabla_equipo.rows = []
            for u in equipo:
                tabla_equipo.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(u[0])),
                        ft.DataCell(ft.Text(u[1])),
                        ft.DataCell(ft.Text(u[2])),
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error al cargar equipo: {e}")

    # Initial load
    cargar_equipo()

    return ft.View(
        "/jefe_area/equipo",
        [
            ft.AppBar(title=ft.Text("Gestión de mi Equipo"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
                expand=True,
                content=ft.Column([
                    ft.Text("Mi Equipo", size=22, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("Crear Coordinador", on_click=lambda e: handle_crear_subordinado(e, "coordinador"), icon=ft.icons.ADD),
                        ft.ElevatedButton("Crear Profesor", on_click=lambda e: handle_crear_subordinado(e, "profesor"), icon=ft.icons.ADD),
                        ft.ElevatedButton("Crear Jefe de Almacén de Área", on_click=lambda e: handle_crear_subordinado(e, "jefe_almacen"), icon=ft.icons.STORE),
                        ft.ElevatedButton("Crear Jefe de Escenarios de Área", on_click=lambda e: handle_crear_subordinado(e, "jefe_escenarios"), icon=ft.icons.SPORTS_SOCCER),
                    ]),
                    ft.Divider(),
                    tabla_equipo,
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )
