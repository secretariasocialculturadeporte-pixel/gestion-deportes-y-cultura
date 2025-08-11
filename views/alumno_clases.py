import flet as ft
import sqlite3
from datetime import datetime
import os
from gamification.engine import process_gamified_action

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def alumno_clases(page: ft.Page, tenant_id: int, alumno_id: int):
    clases_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    notificaciones_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
    mensaje_estado = ft.Text()

    def registrar_asistencia(e, clase_id: int, file_picker: ft.FilePicker):
        def seleccionar_archivo(e: ft.FilePickerResultEvent):
            if not e.files:
                mensaje_estado.value = "No se seleccionó ningún archivo."
                mensaje_estado.color = "red"
                page.update()
                return

            try:
                # This is a simplified file handling for the sandbox environment.
                # In a real app, you'd move this to a secure, persistent location.
                archivo = e.files[0]
                ruta_destino = os.path.join("evidencias", os.path.basename(archivo.path))
                os.makedirs("evidencias", exist_ok=True)

                # In a real Flet app, you can't directly access the client's file system like this.
                # This part of the logic will need to be adapted to use Flet's upload capabilities.
                # For now, we'll just record the path.

                conn = sqlite3.connect("formacion.db")
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO asistencias (inquilino_id, alumno_id, clase_id, fecha_hora, evidencia_path)
                VALUES (?, ?, ?, ?, ?)
            """, (tenant_id, alumno_id, clase_id, datetime.now().isoformat(), ruta_destino))
                conn.commit()
                conn.close()

                # Log the gamified action
                process_gamified_action(tenant_id, alumno_id, 'ASISTENCIA_CLASE')

                mensaje_estado.value = "Asistencia registrada correctamente."
                mensaje_estado.color = "green"
                # Optionally, disable the button after successful registration
                e.control.disabled = True

            except Exception as ex:
                mensaje_estado.value = f"Error registrando asistencia: {ex}"
                mensaje_estado.color = "red"

            page.update()

        file_picker.on_result = seleccionar_archivo
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "pdf"])

    def cargar_datos():
        # --- Cargar Clases ---
        clases_column.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT c.id, c.fecha, c.hora_inicio, c.hora_fin, c.espacio, c.escenario_id, c.novedad, p.nombre_proceso
                FROM clases c
                JOIN procesos_formacion p ON c.proceso_id = p.id
                JOIN inscripciones ins ON ins.clase_id = c.id
                WHERE ins.alumno_id = ? AND c.inquilino_id = ?
                ORDER BY c.fecha DESC, c.hora_inicio
            """, (alumno_id, tenant_id))

            hoy = datetime.now().date()

            for row in cursor.fetchall():
                clase_id, fecha, hora_inicio, hora_fin, espacio, escenario_id, novedad, proceso = row

                fecha_clase = datetime.strptime(fecha, "%Y-%m-%d").date()
                mostrar_asistencia = fecha_clase == hoy

                asistencia_control = ft.Container()
                if mostrar_asistencia:
                    file_picker = ft.FilePicker()
                    page.overlay.append(file_picker)
                    asistencia_control = ft.ElevatedButton(
                        text="Registrar Asistencia",
                        icon=ft.icons.CAMERA_ALT,
                        on_click=lambda e, cid=clase_id, fp=file_picker: registrar_asistencia(e, cid, fp)
                    )

                clases_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Proceso: {proceso}", size=16, weight="bold"),
                                ft.Text(f"Fecha: {fecha} | Hora: {hora_inicio} - {hora_fin}"),
                                ft.Text(f"Lugar: Escenario {escenario_id}, Espacio: {espacio or 'N/A'}"),
                                ft.Text(f"Novedad: {novedad}", italic=True) if novedad else ft.Container(),
                                asistencia_control
                            ]),
                            padding=15,
                            border_radius=10
                        )
                    )
                )

            # --- Cargar Notificaciones ---
            notificaciones_column.controls.clear()
            cursor.execute("""
                SELECT mensaje, fecha_hora FROM notificaciones
                WHERE usuario_id = ? AND inquilino_id = ? ORDER BY fecha_hora DESC
            """, (alumno_id, tenant_id))

            for mensaje, fecha_hora in cursor.fetchall():
                notificaciones_column.controls.append(
                    ft.ListTile(
                        title=ft.Text(mensaje),
                        subtitle=ft.Text(f"{fecha_hora}"),
                        leading=ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=COLOR1_HEX)
                    )
                )
        except Exception as e:
            mensaje_estado.value = f"Error al cargar datos: {e}"
        finally:
            conn.close()
            page.update()

    cargar_datos()

    return ft.View("/alumno_clases", [
        ft.AppBar(title=ft.Text("Mis Clases y Notificaciones"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            expand=True,
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=140, height=70),
                mensaje_estado,
                ft.Text("Notificaciones", size=20, weight="bold"),
                ft.Container(content=notificaciones_column, height=150),
                ft.Divider(height=20, thickness=2),
                ft.Text("Clases Programadas", size=20, weight="bold"),
                clases_column,
            ])
        )
    ])
