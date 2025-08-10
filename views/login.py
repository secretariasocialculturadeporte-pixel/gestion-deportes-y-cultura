import flet as ft
import sqlite3
from utils.audit_logger import log_action

# Dummy hash function for now. In a real app, use something like bcrypt.
def hash_password(password):
    return f"hashed_{password}"

def login_view(page: ft.Page, google_provider, microsoft_provider):

    def handle_login(e):
        # (This logic remains the same for now)
        usuario = usuario_input.value
        password = password_input.value
        if not usuario or not password:
            mensaje_login.value = "Por favor, ingrese usuario y contraseña."
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, rol, nombre_completo, inquilino_id FROM usuarios WHERE nombre_usuario = ? AND password_hash = ?",
                       (usuario, hash_password(password)))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user_id, user_role, user_name, tenant_id = user_data
            page.session.set("user_id", user_id)
            page.session.set("user_role", user_role)
            page.session.set("user_name", user_name)
            page.session.set("tenant_id", tenant_id)

            # Log the successful login action
            log_action(
                tenant_id=tenant_id,
                actor_user_id=user_id,
                action="INICIO_SESION_EXITOSO",
                details={"usuario": user_name, "metodo": "password"}
            )

            # Redirect logic (will need to be updated in the main router as well)
            if user_role == 'profesor': page.go("/profesor_home")
            elif user_role == 'alumno': page.go("/alumno_clases")
            elif user_role == 'admin_empresa': page.go("/admin_home")
            elif user_role == 'jefe_area': page.go("/jefe_area/home")
            elif user_role == 'jefe_escenarios': page.go("/jefe_escenarios/home")
            elif user_role == 'almacenista': page.go("/almacenista/elementos")
            else: page.go("/")
        else:
            mensaje_login.value = "Usuario o contraseña incorrectos."
            page.update()

    def handle_oauth_login(e, provider_name):
        if provider_name == "Google":
            page.login(google_provider)
        elif provider_name == "Microsoft":
            page.login(microsoft_provider)

    # --- UI Controls ---
    usuario_input = ft.TextField(label="Nombre de Usuario", width=350)
    password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)
    mensaje_login = ft.Text(color="red")

    # New OAuth buttons and forgot password link
    google_button = ft.ElevatedButton(
        text="Iniciar sesión con Google",
        on_click=lambda e: handle_oauth_login(e, "Google"),
        width=350,
        # You can add an icon or image here later
    )
    microsoft_button = ft.ElevatedButton(
        text="Iniciar sesión con Microsoft",
        on_click=lambda e: handle_oauth_login(e, "Microsoft"),
        width=350,
    )
    forgot_password_link = ft.TextButton(
        text="¿Olvidaste tu contraseña?",
        on_click=lambda e: page.go("/forgot_password")
    )

    return ft.View(
        "/login", # New route
        [
            ft.Column(
                [
                    ft.Text("Inicio de Sesión", size=32, weight="bold"),
                    usuario_input,
                    password_input,
                    ft.ElevatedButton("Ingresar", on_click=handle_login, width=350),
                    forgot_password_link,
                    ft.Divider(height=10, thickness=1),
                    ft.Text("o continúa con", text_align=ft.TextAlign.CENTER, width=350),
                    google_button,
                    microsoft_button,
                    mensaje_login,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
