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

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Formación"

    def route_change(route):
        page.views.clear()

        user_id = page.session.get("user_id")
        user_role = page.session.get("user_role")

        # --- unprotected routes ---
        if page.route == '/':
            page.views.append(login_view(page))
        # --- protected routes ---
        elif user_id is None:
            # If user is not logged in, redirect to login
            page.views.append(login_view(page))
            page.go('/')
        else:
            # --- Role-based routing ---
            if page.route == '/profesor_home':
                if user_role == 'profesor':
                    page.views.append(profesor_principal(page))
                else:
                    page.go('/') # Or an access denied view

            elif page.route == '/profesor_perfil':
                if user_role == 'profesor':
                    page.views.append(profesor_perfil(page, user_id))
                else:
                    page.go('/')

            elif page.route == '/profesor_clases':
                 if user_role == 'profesor':
                    page.views.append(profesor_clases(page, user_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_escenarios':
                 if user_role == 'profesor':
                    page.views.append(profesor_escenarios(page))
                 else:
                    page.go('/')

            elif page.route == '/profesor_eventos':
                 if user_role == 'profesor':
                    page.views.append(profesor_eventos(page, user_id))
                 else:
                    page.go('/')

            elif page.route == '/profesor_horarios':
                 if user_role == 'profesor':
                    page.views.append(profesor_horarios(page))
                 else:
                    page.go('/')

            elif page.route == '/profesor_procesos_formacion':
                 if user_role == 'profesor':
                    page.views.append(profesor_procesos_formacion(page))
                 else:
                    page.go('/')

            elif page.route == '/instructor/elementos':
                 if user_role == 'profesor':
                    page.views.append(instructor_gestion_elementos(page, user_id))
                 else:
                    page.go('/')

            elif page.route == '/alumno_clases':
                if user_role == 'alumno':
                    page.views.append(alumno_clases(page, user_id))
                else:
                    page.go('/')

            elif page.route == '/almacenista/elementos':
                if user_role == 'almacenista':
                    page.views.append(almacenista_gestion_elementos(page, user_id))
                else:
                    page.go('/')

            elif page.route == '/admin/reporte_demografico':
                if user_role == 'admin':
                    page.views.append(admin_reporte_demografico(page))
                else:
                    page.go('/')

            elif page.route == '/admin/reporte_asistencia':
                if user_role == 'admin':
                    page.views.append(admin_reporte_asistencia(page))
                else:
                    page.go('/')

            elif page.route == '/admin_home':
                if user_role == 'admin':
                    page.views.append(admin_principal(page))
                else:
                    page.go('/')

            elif page.route == '/admin/gestion_listas':
                if user_role == 'admin':
                    page.views.append(admin_gestion_listas(page))
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
    # To test, we can add a dummy user
    import sqlite3
    def add_dummy_user(username, password, role, name):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            from views.login import hash_password
            # Check if user already exists
            cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (username,))
            if cursor.fetchone():
                print(f"Usuario de prueba '{username}' ya existe.")
                return

            # Create user
            cursor.execute("INSERT INTO usuarios (nombre_usuario, password_hash, rol, nombre_completo, correo) VALUES (?, ?, ?, ?, ?)",
                           (username, hash_password(password), role, name, f"{username}@test.com"))
            user_id = cursor.lastrowid

            # Create role-specific record
            if role == 'profesor':
                cursor.execute("INSERT INTO profesores (usuario_id, area) VALUES (?, ?)", (user_id, 'Deportes'))
            elif role == 'alumno':
                # Add some dummy demographic data
                cursor.execute("""
                    INSERT INTO alumnos (usuario_id, tipo_documento, documento, genero, escolaridad)
                    VALUES (?, 'C.C.', ?, 'Masculino', 'Universitario')
                    """, (user_id, f"12345{user_id}"))
            elif role == 'almacenista':
                cursor.execute("INSERT INTO almacenistas (usuario_id, area_almacen) VALUES (?, ?)", (user_id, 'General'))

            conn.commit()
            print(f"Usuario de prueba '{username}' (ID: {user_id}) creado con su rol específico.")

        except Exception as e:
            print(f"Error creando usuario de prueba '{username}': {e}")
            conn.rollback()
        finally:
            conn.close()

    # Add users for testing each role
    add_dummy_user("profe", "123", "profesor", "Profesor Demo")
    add_dummy_user("alumno", "123", "alumno", "Alumno Demo")
    add_dummy_user("admin", "123", "admin", "Admin Demo")
    add_dummy_user("almacen", "123", "almacenista", "Almacenista Demo")

    ft.app(target=main, assets_dir="assets")
