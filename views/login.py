import flet as ft
import sqlite3

# Dummy hash function for now. In a real app, use something like bcrypt.
def hash_password(password):
    return f"hashed_{password}"

def login_view(page: ft.Page):
    usuario_input = ft.TextField(label="Nombre de Usuario", width=300)
    password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    mensaje_login = ft.Text(color="red")

    def handle_login(e):
        usuario = usuario_input.value
        password = password_input.value

        if not usuario or not password:
            mensaje_login.value = "Por favor, ingrese usuario y contraseña."
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # In a multi-tenant app, the username might not be unique across all tenants.
        # A real login would likely involve a tenant identifier.
        # For now, we assume username is unique for simplicity of login.
        cursor.execute("SELECT id, rol, nombre_completo, inquilino_id FROM usuarios WHERE nombre_usuario = ? AND password_hash = ?",
                       (usuario, hash_password(password)))
        user_data = cursor.fetchone()

        if user_data:
            user_id, user_role, user_name, tenant_id = user_data
            page.session.set("user_id", user_id)
            page.session.set("user_role", user_role)
            page.session.set("user_name", user_name)
            page.session.set("tenant_id", tenant_id)

            # Redirect based on role
            if user_role == 'profesor':
                page.go("/profesor_home")
            elif user_role == 'alumno':
                page.go("/alumno_clases")
            elif user_role == 'admin_empresa':
                page.go("/admin_home")
            elif user_role == 'jefe_area':
                page.go("/jefe_area/home")
            elif user_role == 'almacenista':
                page.go("/almacenista/elementos")
            else:
                page.go("/") # Fallback
        else:
            mensaje_login.value = "Usuario o contraseña incorrectos."

        conn.close()
        page.update()

    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Text("Inicio de Sesión", size=32, weight="bold"),
                    usuario_input,
                    password_input,
                    ft.ElevatedButton("Ingresar", on_click=handle_login),
                    mensaje_login
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
