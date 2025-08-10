import flet as ft
from database.database_setup import setup_database

# --- Import all views ---
from views.login import login_view
from views.profesor_principal import profesor_principal
from views.profesor_perfil import profesor_perfil
from views.profesor_clases import profesor_clases
from views.profesor_escenarios import profesor_escenarios
from views.profesor_eventos import profesor_eventos
from views.profesor_horarios import profesor_horarios
from views.profesor_procesos_formacion import profesor_procesos_formacion
from views.instructor_gestion_elementos import instructor_gestion_elementos

from views.alumno_clases import alumno_clases
from views.alumno_inscripcion import alumno_inscripcion

from views.almacenista_gestion_elementos import almacenista_gestion_elementos

from views.admin_reporte_asistencia import admin_reporte_asistencia
from views.admin_reporte_demografico import admin_reporte_demografico
from views.admin_gestion_listas import admin_gestion_listas
from views.admin_principal import admin_principal
from views.admin_empresa.gestion_personal import gestion_personal_view
from views.jefe_area.jefe_area_principal import jefe_area_principal_view
from views.jefe_area.gestion_equipo import gestion_equipo_view
from views.jefe_area.analisis_datos import analisis_datos_view
from views.admin_empresa.gestion_areas import gestion_areas_view
from views.admin_empresa.audit_log_view import audit_log_view
from views.jefe_escenarios.jefe_escenarios_principal import jefe_escenarios_principal_view
from views.jefe_escenarios.gestion_escenarios import gestion_escenarios_avanzado_view
from views.jefe_escenarios.gestion_reservas import gestion_reservas_view
from views.admin_empresa.configuracion_ia import configuracion_ia_view
from views.splash import splash_view
from views.forgot_password import forgot_password_view
from views.reset_password import reset_password_view

import os

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Formación"

    # --- OAuth Providers Configuration ---
    # The user must replace these with their own credentials from Google/Microsoft Developer Consoles.
    # It's best to use environment variables for this.
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
    microsoft_client_id = os.getenv("MICROSOFT_CLIENT_ID", "YOUR_MICROSOFT_CLIENT_ID")
    microsoft_client_secret = os.getenv("MICROSOFT_CLIENT_SECRET", "YOUR_MICROSOFT_CLIENT_SECRET")

    def on_oauth_login(e: ft.LoginEvent):
        if e.error:
            # Handle login error
            print(f"Error de OAuth: {e.error_description}")
            # You could show a snackbar here
        else:
            # This is a successful login.
            # For B2B SaaS, we assume the user must already exist in the system,
            # created by a tenant admin. We find the user by email.
            user_info = e.user
            email = user_info['email']

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, rol, nombre_completo, inquilino_id FROM usuarios WHERE correo = ?", (email,))
            db_user = cursor.fetchone()
            conn.close()

            if db_user:
                # User exists, log them in
                user_id, user_role, user_name, tenant_id = db_user
                page.session.set("user_id", user_id)
                page.session.set("user_role", user_role)
                page.session.set("user_name", user_name)
                page.session.set("tenant_id", tenant_id)
                print(f"Usuario OAuth '{email}' encontrado. Iniciando sesión para el inquilino {tenant_id}.")
                # Redirect to their correct home page
                if user_role == 'profesor': page.go("/profesor_home")
                elif user_role == 'alumno': page.go("/alumno_clases")
                elif user_role == 'admin_empresa': page.go("/admin_home")
                else: page.go("/") # Fallback
            else:
                # User not found in DB. They cannot log in.
                print(f"Usuario OAuth '{email}' no encontrado en la base de datos. Acceso denegado.")
                # Optionally, show an error on the login page
                page.go("/login?error=oauth_user_not_found")


    google_provider = ft.GoogleOAuthProvider(
        client_id=google_client_id,
        redirect_url=page.get_url(), # Flet handles the redirect URL
        on_login=on_oauth_login,
    )

    microsoft_provider = ft.MicrosoftOAuthProvider(
        client_id=microsoft_client_id,
        client_secret=microsoft_client_secret,
        redirect_url=page.get_url(),
        on_login=on_oauth_login,
    )


    def route_change(route):
        page.views.clear()

        user_id = page.session.get("user_id")
        user_role = page.session.get("user_role")
        tenant_id = page.session.get("tenant_id")

        # --- Public / Unprotected Routes ---
        if page.route == "/":
            page.views.append(splash_view(page))
        elif page.route == "/login":
            page.views.append(login_view(page, google_provider, microsoft_provider))
        elif page.route == "/forgot_password":
            page.views.append(forgot_password_view(page))
        elif page.route.startswith("/reset_password"):
            token = page.route.split("/")[-1]
            page.views.append(reset_password_view(page, token))

        # --- Protected Routes ---
        elif user_id is None or tenant_id is None:
            # If user is not authenticated and tries to access a protected route, redirect to login
            page.go("/login")

        else:
            # --- Role-based routing for authenticated users ---
            if page.route == '/profesor_home':
                if user_role == 'profesor':
                    page.views.append(profesor_principal(page))
                else:
                    page.go('/') # Or an access denied view

            elif page.route == '/profesor_perfil':
                if user_role == 'profesor':
                    page.views.append(profesor_perfil(page, user_id, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/profesor_clases':
                 if user_role == 'profesor':
                    # This view needs the professor's own ID from the 'profesores' table
                    # This logic should be improved later, but for now we pass the user_id
                    page.views.append(profesor_clases(page, tenant_id, user_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_escenarios':
                 if user_role == 'profesor':
                    page.views.append(profesor_escenarios(page, tenant_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_eventos':
                 if user_role == 'profesor':
                    page.views.append(profesor_eventos(page, tenant_id, user_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_horarios':
                 if user_role == 'profesor':
                    page.views.append(profesor_horarios(page, tenant_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_procesos_formacion':
                 if user_role == 'profesor':
                    page.views.append(profesor_procesos_formacion(page, tenant_id))
                 else:
                    page.go('/')

            elif page.route == '/instructor/elementos':
                 if user_role == 'profesor':
                    page.views.append(instructor_gestion_elementos(page, tenant_id, user_id))
                 else:
                    page.go('/')

            elif page.route == '/alumno_clases':
                if user_role == 'alumno':
                    page.views.append(alumno_clases(page, tenant_id, user_id))
                else:
                    page.go('/')

            elif page.route == '/almacenista/elementos':
                if user_role == 'almacenista':
                    page.views.append(almacenista_gestion_elementos(page, tenant_id, user_id))
                else:
                    page.go('/')

            elif page.route == '/admin_home':
                if user_role == 'admin_empresa':
                    page.views.append(admin_principal(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/reporte_demografico':
                if user_role == 'admin_empresa':
                    page.views.append(admin_reporte_demografico(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/reporte_asistencia':
                if user_role == 'admin_empresa':
                    page.views.append(admin_reporte_asistencia(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/gestion_listas':
                if user_role == 'admin_empresa':
                    page.views.append(admin_gestion_listas(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/personal':
                if user_role == 'admin_empresa':
                    page.views.append(gestion_personal_view(page, tenant_id, user_id))
                else:
                    page.go('/')

            elif page.route == '/admin/areas':
                if user_role == 'admin_empresa':
                    page.views.append(gestion_areas_view(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/configuracion_ia':
                if user_role == 'admin_empresa':
                    page.views.append(configuracion_ia_view(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/admin/audit_log':
                if user_role == 'admin_empresa':
                    page.views.append(audit_log_view(page, tenant_id))
                else:
                    page.go('/')

            elif page.route == '/jefe_area/home':
                if user_role == 'jefe_area':
                    page.views.append(jefe_area_principal_view(page))
                else:
                    page.go('/')

            elif page.route == '/jefe_area/equipo':
                if user_role == 'jefe_area':
                    page.views.append(gestion_equipo_view(page, tenant_id, user_id))
                else:
                    page.go('/')

            elif page.route == '/jefe_area/analisis':
                if user_role == 'jefe_area':
                    page.views.append(analisis_datos_view(page, tenant_id, user_id))
                else:
                    page.go('/')

            elif page.route == '/jefe_escenarios/home':
                if user_role == 'jefe_escenarios':
                    page.views.append(jefe_escenarios_principal_view(page))
                else:
                    page.go('/')

            elif page.route == '/jefe_escenarios/gestion':
                if user_role == 'jefe_escenarios':
                    page.views.append(gestion_escenarios_avanzado_view(page, tenant_id, user_id))
                else:
                    page.go('/')

            # Dynamic route for reservations
            elif page.route.startswith('/jefe_escenarios/reservas/'):
                if user_role == 'jefe_escenarios':
                    try:
                        parte_id = int(page.route.split('/')[-1])
                        page.views.append(gestion_reservas_view(page, tenant_id, parte_id))
                    except (ValueError, IndexError):
                        page.go('/jefe_escenarios/home') # Go home if ID is invalid
                else:
                    page.go('/')

            else:
                # If route doesn't exist, go to a default page based on role
                if user_role == 'profesor':
                    page.go('/profesor_home')
                elif user_role == 'alumno':
                    page.go('/alumno_clases')
                else:
                    page.go('/') # Fallback

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    # Ensure the database and its tables are created before the app runs
    setup_database()

    # --- Multi-Tenant Dummy Data Setup ---
    import sqlite3
    from datetime import datetime
    from views.login import hash_password

    def setup_dummy_data():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        try:
            # 1. Create a Test Tenant if it doesn't exist
            cursor.execute("SELECT id FROM inquilinos WHERE nombre_empresa = 'Empresa Demo'")
            tenant = cursor.fetchone()
            if not tenant:
                # In a real app, the API key should be securely generated (e.g., using secrets module)
                dummy_api_key = "inquilino_demo_key"
                cursor.execute("""
                    INSERT INTO inquilinos (nombre_empresa, fecha_suscripcion, plan, api_key, direccion, municipio, pais, latitud, longitud)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        'Empresa Demo', datetime.now().isoformat(), 'anual', dummy_api_key,
                        'Calle Falsa 123', 'Springfield', 'EEUU', 40.7128, -74.0060
                    )
                )
                tenant_id = cursor.lastrowid
                print(f"Inquilino de prueba 'Empresa Demo' (ID: {tenant_id}) creado con ubicación y API Key.")
            else:
                tenant_id = tenant[0]
                print(f"Inquilino de prueba 'Empresa Demo' (ID: {tenant_id}) ya existe.")

            # 2. Function to add users for this tenant
            def add_dummy_user(username, password, role, name):
                # Check if user already exists for this tenant
                cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ? AND inquilino_id = ?", (username, tenant_id))
                if cursor.fetchone():
                    print(f"Usuario '{username}' para el inquilino {tenant_id} ya existe.")
                    return

                # Create user associated with the tenant
                cursor.execute("INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo) VALUES (?, ?, ?, ?, ?, ?)",
                               (tenant_id, username, hash_password(password), role, name, f"{username}@demo.com"))
                user_id = cursor.lastrowid

                # Create role-specific record
                if role == 'profesor':
                    cursor.execute("INSERT INTO profesores (usuario_id, inquilino_id, area) VALUES (?, ?, ?)", (user_id, tenant_id, 'Deportes'))
                elif role == 'alumno':
                    cursor.execute("INSERT INTO alumnos (usuario_id, inquilino_id, documento) VALUES (?, ?, ?)", (user_id, tenant_id, f"12345{user_id}"))
                elif role == 'almacenista':
                    cursor.execute("INSERT INTO almacenistas (usuario_id, inquilino_id, area_almacen) VALUES (?, ?, ?)", (user_id, tenant_id, 'General'))

                print(f"Usuario de prueba '{username}' (ID: {user_id}) creado para el inquilino {tenant_id}.")

            # 3. Add users for the test tenant in a hierarchy
            # Note: The 'add_dummy_user' function needs to be updated to handle the hierarchy
            def add_dummy_user(username, password, role, name, reports_to_id=None):
                # Check if user already exists for this tenant
                cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ? AND inquilino_id = ?", (username, tenant_id))
                if cursor.fetchone():
                    print(f"Usuario '{username}' para el inquilino {tenant_id} ya existe.")
                    # Return existing user's ID for hierarchy
                    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ? AND inquilino_id = ?", (username, tenant_id))
                    return cursor.fetchone()[0]

                # Create user associated with the tenant
                cursor.execute("""
                    INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, reporta_a_usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (tenant_id, username, hash_password(password), role, name, f"{username}@demo.com", reports_to_id))
                user_id = cursor.lastrowid

                # Create role-specific record
                if role == 'jefe_area':
                     # We can pre-assign an area here for dummy data purposes
                     area = "Deportes" if "deportes" in username else "Cultura" if "cultura" in username else None
                     cursor.execute("INSERT INTO jefes_area (usuario_id, inquilino_id, area_responsabilidad) VALUES (?, ?, ?)", (user_id, tenant_id, area))
                elif role == 'profesor':
                    # This needs to be smarter, getting the area from its manager
                    cursor.execute("INSERT INTO profesores (usuario_id, inquilino_id, area) VALUES (?, ?, 'Deportes')", (user_id, tenant_id)) # Simplified
                elif role == 'jefe_almacen':
                     cursor.execute("INSERT INTO jefes_almacen (usuario_id, inquilino_id) VALUES (?, ?)", (user_id, tenant_id))
                elif role == 'jefe_escenarios':
                     cursor.execute("INSERT INTO jefes_escenarios (usuario_id, inquilino_id) VALUES (?, ?)", (user_id, tenant_id))
                elif role == 'alumno':
                    cursor.execute("INSERT INTO alumnos (usuario_id, inquilino_id, documento) VALUES (?, ?, ?)", (user_id, tenant_id, f"12345{user_id}"))
                elif role == 'almacenista':
                    cursor.execute("INSERT INTO almacenistas (usuario_id, inquilino_id, area_almacen) VALUES (?, ?, ?)", (user_id, tenant_id, 'General'))

                print(f"Usuario de prueba '{username}' (ID: {user_id}) creado para el inquilino {tenant_id}.")
                return user_id

            # Create the hierarchy
            admin_id = add_dummy_user("admin_empresa", "123", "admin_empresa", "Admin Empresa Demo")

            jefe_deportes_id = add_dummy_user("jefe_deportes", "123", "jefe_area", "Jefe de Deportes", reports_to_id=admin_id)
            add_dummy_user("profe_futbol", "123", "profesor", "Profesor de Fútbol", reports_to_id=jefe_deportes_id)
            add_dummy_user("almacen_deportes", "123", "jefe_almacen", "Jefe Almacén de Deportes", reports_to_id=jefe_deportes_id)

            jefe_cultura_id = add_dummy_user("jefe_cultura", "123", "jefe_area", "Jefe de Cultura", reports_to_id=admin_id)
            add_dummy_user("profe_musica", "123", "profesor", "Profesor de Música", reports_to_id=jefe_cultura_id)

            add_dummy_user("alumno", "123", "alumno", "Alumno Demo")

            # 4. Add dummy scenarios and parts
            cursor.execute("SELECT id FROM escenarios WHERE nombre = 'Estadio Municipal' AND inquilino_id = ?", (tenant_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO scenarios (inquilino_id, nombre, ubicacion) VALUES (?, ?, ?)",
                               (tenant_id, 'Estadio Municipal', 'Calle Falsa 123'))
                escenario_id = cursor.lastrowid
                cursor.execute("INSERT INTO escenario_partes (inquilino_id, escenario_id, nombre_parte) VALUES (?, ?, ?)",
                               (tenant_id, escenario_id, 'Cancha Principal'))
                print("Escenario de prueba creado.")

            conn.commit()

        except Exception as e:
            print(f"Error creando datos de prueba: {e}")
            conn.rollback()
        finally:
            conn.close()

    setup_dummy_data()

    # PWA Manifest Configuration
    manifest = ft.PwaManifest(
        name="Gestión-App de Formación",
        short_name="GestiónApp",
        description="Una aplicación para gestionar centros de formación cultural y deportiva.",
        theme_color=COLOR2_HEX,
        bgcolor=COLOR1_HEX,
        icons=[
            ft.PwaIcon(src="assets/icons/icon-192.png", sizes="192x192"),
            ft.PwaIcon(src="assets/icons/icon-512.png", sizes="512x512"),
        ],
    )

    ft.app(target=main, assets_dir="assets", pwa_manifest=manifest)
