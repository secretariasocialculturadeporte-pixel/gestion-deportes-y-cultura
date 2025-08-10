import flet as ft
import sqlite3
from views.login import hash_password # Re-using the dummy hash function
from utils.audit_logger import log_action

LOGO_PATH = "../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def gestion_personal_view(page: ft.Page, tenant_id: int, actor_user_id: int):

    # --- DIALOG FOR CREATING USER ---
    def crear_dialogo_usuario(rol_a_crear: str):
        nombre_completo_input = ft.TextField(label="Nombre Completo")
        nombre_usuario_input = ft.TextField(label="Nombre de Usuario")
        password_input = ft.TextField(label="Contraseña Temporal", password=True, can_reveal_password=True)
        correo_input = ft.TextField(label="Correo Electrónico")

        def guardar_nuevo_usuario(e):
            # Basic Validation
            if not all([nombre_completo_input.value, nombre_usuario_input.value, password_input.value]):
                page.snack_bar = ft.SnackBar(ft.Text("Nombre, usuario y contraseña son obligatorios."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            try:
                # Insert into usuarios table
                cursor.execute("""
                    INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tenant_id,
                    nombre_usuario_input.value,
                    hash_password(password_input.value),
                    rol_a_crear,
                    nombre_completo_input.value,
                    correo_input.value
                ))
                new_user_id = cursor.lastrowid

                # Insert into role-specific table
                if rol_a_crear == 'jefe_area':
                    cursor.execute("INSERT INTO jefes_area (usuario_id, inquilino_id) VALUES (?, ?)", (new_user_id, tenant_id))
                elif rol_a_crear == 'jefe_almacen':
                    cursor.execute("INSERT INTO jefes_almacen (usuario_id, inquilino_id) VALUES (?, ?)", (new_user_id, tenant_id))
                elif rol_a_crear == 'jefe_escenarios':
                    cursor.execute("INSERT INTO jefes_escenarios (usuario_id, inquilino_id) VALUES (?, ?)", (new_user_id, tenant_id))

                conn.commit()

                # Log the action
                log_action(
                    tenant_id=tenant_id,
                    actor_user_id=actor_user_id,
                    action="CREAR_USUARIO",
                    details={"usuario_creado_id": new_user_id, "rol_asignado": rol_a_crear, "nombre": nombre_completo_input.value}
                )

                page.snack_bar = ft.SnackBar(ft.Text(f"Usuario '{nombre_completo_input.value}' creado con éxito."), bgcolor="green")
                page.dialog.open = False
                cargar_usuarios() # Refresh the user list
            except sqlite3.IntegrityError:
                page.snack_bar = ft.SnackBar(ft.Text(f"El nombre de usuario '{nombre_usuario_input.value}' ya existe."), bgcolor="red")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al crear usuario: {ex}"), bgcolor="red")
            finally:
                conn.close()
                page.snack_bar.open = True
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Crear Nuevo {rol_a_crear.replace('_', ' ').title()}"),
            content=ft.Column([
                nombre_completo_input,
                nombre_usuario_input,
                password_input,
                correo_input,
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Guardar", on_click=guardar_nuevo_usuario),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return dialog

    def handle_crear_usuario(e, rol):
        page.dialog = crear_dialogo_usuario(rol)
        page.dialog.open = True
        page.update()

    # --- MAIN VIEW WIDGETS ---
    tabla_usuarios = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre Completo")),
            ft.DataColumn(ft.Text("Nombre de Usuario")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Correo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def cargar_usuarios():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nombre_completo, nombre_usuario, rol, correo FROM usuarios WHERE inquilino_id = ?",
                (tenant_id,)
            )
            usuarios = cursor.fetchall()
            conn.close()

            tabla_usuarios.rows = []
            for u in usuarios:
                tabla_usuarios.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(u[0])),
                        ft.DataCell(ft.Text(u[1])),
                        ft.DataCell(ft.Text(u[2])),
                        ft.DataCell(ft.Text(u[3])),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.icons.EDIT, tooltip="Editar"),
                            ft.IconButton(ft.icons.DELETE, tooltip="Eliminar", icon_color="red"),
                        ]))
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")

    # Initial load
    cargar_usuarios()

    return ft.View(
        "/admin/personal",
        [
            ft.AppBar(title=ft.Text("Gestión de Personal de la Empresa"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
                expand=True,
                content=ft.Column([
                    ft.Text("Administrar Personal", size=22, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("Crear Jefe de Área", on_click=lambda e: handle_crear_usuario(e, "jefe_area"), icon=ft.icons.ADD),
                        ft.ElevatedButton("Crear Jefe de Almacén", on_click=lambda e: handle_crear_usuario(e, "jefe_almacen"), icon=ft.icons.ADD),
                        ft.ElevatedButton("Crear Jefe de Escenarios", on_click=lambda e: handle_crear_usuario(e, "jefe_escenarios"), icon=ft.icons.ADD),
                    ]),
                    ft.Divider(),
                    ft.Text("Usuarios Registrados", size=18),
                    tabla_usuarios,
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )
