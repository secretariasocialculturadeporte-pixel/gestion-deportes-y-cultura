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

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Formación"

    def route_change(route):
        page.views.clear()

        user_id = page.session.get("user_id")
        user_role = page.session.get("user_role")
        tenant_id = page.session.get("tenant_id")

        # --- unprotected routes ---
        if page.route == '/':
            page.views.append(login_view(page))
        # --- protected routes ---
        elif user_id is None or tenant_id is None:
            # If user is not logged in or has no tenant, redirect to login
            page.views.append(login_view(page))
            page.go('/')
        else:
            # --- Role-based routing ---
            # Every authenticated view now receives tenant_id
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
                    page.views.append(admin_principal(page))
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
                    page.views.append(gestion_personal_view(page, tenant_id))
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
                cursor.execute("INSERT INTO inquilinos (nombre_empresa, fecha_suscripcion, plan, api_key) VALUES (?, ?, ?, ?)",
                               ('Empresa Demo', datetime.now().isoformat(), 'anual', dummy_api_key))
                tenant_id = cursor.lastrowid
                print(f"Inquilino de prueba 'Empresa Demo' (ID: {tenant_id}) creado con API Key.")
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
                     cursor.execute("INSERT INTO jefes_area (usuario_id, inquilino_id) VALUES (?, ?)", (user_id, tenant_id))
                elif role == 'profesor':
                    cursor.execute("INSERT INTO profesores (usuario_id, inquilino_id) VALUES (?, ?)", (user_id, tenant_id))
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
            add_dummy_user("alumno", "123", "alumno", "Alumno Demo")
            add_dummy_user("almacen", "123", "almacenista", "Almacenista Demo")

            conn.commit()

        except Exception as e:
            print(f"Error creando datos de prueba: {e}")
            conn.rollback()
        finally:
            conn.close()

    setup_dummy_data()

    ft.app(target=main, assets_dir="assets")
