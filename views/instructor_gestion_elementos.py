import flet as ft
import sqlite3
import datetime
import os

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def instructor_gestion_elementos(page: ft.Page, instructor_id: int):
    # --- WIDGETS ---
    prestamos_activos_column = ft.Column(scroll=ft.ScrollMode.AUTO)
    mensaje_general = ft.Text()

    def registrar_devolucion(prestamo_id, estado_entrega, foto_picker_result, observaciones):
        if not all([estado_entrega.value, foto_picker_result, observaciones.value]):
            mensaje_general.value = "Todos los campos de devolución son requeridos."
            mensaje_general.color = "red"
            page.update()
            return

        try:
            # Simplified file handling
            foto_path = foto_picker_result.files[0].path

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE prestamos
                SET estado = 'Devuelto',
                    foto_entrega = ?,
                    observaciones_entrega = ?,
                    fecha_entrega = ?,
                    estado_entrega = ?
                WHERE id = ?
            """, (
                foto_path,
                observaciones.value,
                datetime.date.today().isoformat(),
                estado_entrega.value,
                prestamo_id
            ))
            conn.commit()
            conn.close()

            mensaje_general.value = "Elemento devuelto correctamente."
            mensaje_general.color = "green"
            cargar_prestamos() # Refresh the list
        except Exception as e:
            mensaje_general.value = f"Error al registrar devolución: {e}"
            mensaje_general.color = "red"
        finally:
            page.update()

    def build_prestamo_card(prestamo_data):
        prestamo_id, codigo_elemento, descripcion_elemento, fecha_prestamo = prestamo_data

        estado_entrega_input = ft.TextField(label="Descripción del estado de entrega")
        observaciones_input = ft.TextField(label="Observaciones de la entrega")
        foto_picker = ft.FilePicker()
        page.overlay.append(foto_picker)

        devolucion_form = ft.Column(
            visible=False,
            controls=[
                estado_entrega_input,
                observaciones_input,
                ft.ElevatedButton("Seleccionar foto de entrega", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: foto_picker.pick_files(allow_multiple=False)),
                ft.ElevatedButton(
                    "Confirmar Devolución",
                    icon=ft.icons.CHECK_CIRCLE,
                    on_click=lambda e: registrar_devolucion(
                        prestamo_id,
                        estado_entrega_input,
                        foto_picker.result,
                        observaciones_input
                    )
                )
            ]
        )

        def toggle_form(e):
            devolucion_form.visible = not devolucion_form.visible
            page.update()

        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column([
                    ft.ListTile(
                        title=ft.Text(f"Código: {codigo_elemento}", weight="bold"),
                        subtitle=ft.Text(f"Descripción: {descripcion_elemento}\nPrestado en: {fecha_prestamo}"),
                    ),
                    ft.ElevatedButton("Registrar Devolución", on_click=toggle_form),
                    devolucion_form
                ])
            )
        )

    def cargar_prestamos():
        prestamos_activos_column.controls.clear()
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.id, e.codigo, e.descripcion, pr.fecha_prestamo
                FROM prestamos pr
                JOIN elementos e ON pr.elemento_id = e.id
                WHERE pr.instructor_id = ? AND pr.estado = 'En uso'
            """, (instructor_id,))

            prestamos = cursor.fetchall()
            if not prestamos:
                prestamos_activos_column.controls.append(ft.Text("No tienes elementos en préstamo actualmente."))
            else:
                for p_data in prestamos:
                    prestamos_activos_column.controls.append(build_prestamo_card(p_data))

            conn.close()
        except Exception as e:
            prestamos_activos_column.controls.append(ft.Text(f"Error al cargar elementos: {e}", color="red"))

        page.update()

    # --- INITIAL LOAD ---
    cargar_prestamos()

    # --- VIEW ---
    return ft.View("/instructor/elementos", [
        ft.AppBar(title=ft.Text("Mis Elementos en Préstamo"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=140, height=70),
                mensaje_general,
                ft.Text("Elementos Actualmente a mi Cargo", size=18, weight="bold"),
                prestamos_activos_column,
            ])
        )
    ])
