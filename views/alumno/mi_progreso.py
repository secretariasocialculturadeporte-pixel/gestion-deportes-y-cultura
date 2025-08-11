import flet as ft
import sqlite3

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def mi_progreso_view(page: ft.Page, tenant_id: int, user_id: int):

    # --- UI Controls ---
    nivel_text = ft.Text(size=24, weight="bold")
    puntos_text = ft.Text(size=18)
    progreso_bar = ft.ProgressBar(width=400, value=0)
    medallas_container = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.CENTER)

    def load_progreso():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()

            # Get student's progress data
            cursor.execute(
                "SELECT nivel, puntos_totales FROM alumnos WHERE usuario_id = ? AND inquilino_id = ?",
                (user_id, tenant_id)
            )
            progreso = cursor.fetchone()

            if progreso:
                nivel, puntos = progreso
                nivel_text.value = f"Nivel {nivel}"
                puntos_text.value = f"{puntos} Puntos"

                # Placeholder logic for progress bar (e.g., 1000 points per level)
                puntos_nivel_actual = (nivel - 1) * 1000
                puntos_para_siguiente_nivel = nivel * 1000
                progreso_actual = (puntos - puntos_nivel_actual) / (puntos_para_siguiente_nivel - puntos_nivel_actual)
                progreso_bar.value = progreso_actual
            else:
                nivel_text.value = "N/A"
                puntos_text.value = "0 Puntos"
                progreso_bar.value = 0

            # Medals will be loaded in this step
            cursor.execute("""
                SELECT m.nombre, m.descripcion, m.icono_path
                FROM gamificacion_medallas_obtenidas mo
                JOIN gamificacion_medallas m ON mo.medalla_key = m.medalla_key AND mo.inquilino_id = m.inquilino_id
                WHERE mo.alumno_id = (SELECT id FROM alumnos WHERE usuario_id = ?) AND mo.inquilino_id = ?
            """, (user_id, tenant_id))

            medallas = cursor.fetchall()
            medallas_container.controls.clear()
            if not medallas:
                medallas_container.controls.append(ft.Text("¡Aún no has ganado ninguna medalla, sigue participando!"))
            else:
                for nombre, desc, icon_path in medallas:
                    medallas_container.controls.append(
                        ft.Column(
                            [
                                ft.Image(src=f"../../{icon_path}", width=64, height=64),
                                ft.Text(nombre, weight="bold"),
                                ft.Text(desc, size=12, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            width=120
                        )
                    )

            conn.close()
            page.update()
        except Exception as e:
            print(f"Error loading progress: {e}")

    # Initial load
    load_progreso()

    return ft.View(
        "/alumno/progreso",
        [
            ft.AppBar(title=ft.Text("Mi Progreso (SIGA)")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Tu Aventura de Aprendizaje", size=22, weight="bold"),
                        ft.Divider(),
                        nivel_text,
                        progreso_bar,
                        puntos_text,
                        ft.Divider(height=30),
                        ft.Text("Mis Medallas", size=20, weight="bold"),
                        medallas_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO
                )
            )
        ]
    )
