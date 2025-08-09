import flet as ft
import sqlite3
import pandas as pd
from datetime import datetime
import os

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def admin_reporte_demografico(page: ft.Page):
    # --- WIDGETS ---
    categoria_dropdown = ft.Dropdown(
        label="Seleccionar categoría de reporte",
        options=[
            ft.dropdown.Option("genero", text="Género"),
            ft.dropdown.Option("grupo_etario", text="Grupo Etario"),
            ft.dropdown.Option("tipo_documento", text="Tipo Documento"),
            ft.dropdown.Option("escolaridad", text="Escolaridad"),
            ft.dropdown.Option("discapacidad", text="Discapacidad"),
            ft.dropdown.Option("grupo_poblacional", text="Grupo Poblacional"),
            ft.dropdown.Option("zona_geografica", text="Zona Geográfica (Barrio/Vereda)"),
        ],
        on_change=lambda e: mostrar_reporte(e.control.value)
    )

    tabla_reporte = ft.DataTable(columns=[], rows=[], expand=True)
    boton_descargar = ft.ElevatedButton(
        "Descargar Excel",
        icon=ft.icons.DOWNLOAD,
        on_click=lambda e: descargar_excel(),
        visible=False
    )
    mensaje = ft.Text()

    def obtener_reporte(categoria):
        # A simple mapping to handle different column names if needed
        columna_db = categoria
        if categoria == "zona_geografica":
             # This is a simplification. A real implementation might need to query multiple columns.
            columna_db = "barrio"

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        query = f"SELECT {columna_db}, COUNT(*) FROM alumnos GROUP BY {columna_db} ORDER BY COUNT(*) DESC"
        try:
            cursor.execute(query)
            datos = cursor.fetchall()
            # Store data for download
            page.client_storage.set("reporte_actual.datos", datos)
            page.client_storage.set("reporte_actual.categoria", categoria)
            return datos
        except Exception as e:
            mensaje.value = f"Error al generar reporte: {e}"
            return []
        finally:
            conn.close()

    def mostrar_reporte(categoria):
        if not categoria:
            return

        datos = obtener_reporte(categoria)

        if datos:
            tabla_reporte.columns = [
                ft.DataColumn(ft.Text(categoria.replace("_", " ").title())),
                ft.DataColumn(ft.Text("Cantidad de Alumnos")),
            ]
            tabla_reporte.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                for row in datos
            ]
            boton_descargar.visible = True
        else:
            tabla_reporte.columns = []
            tabla_reporte.rows = []
            boton_descargar.visible = False

        page.update()

    def descargar_excel():
        datos = page.client_storage.get("reporte_actual.datos")
        categoria = page.client_storage.get("reporte_actual.categoria")
        if datos and categoria:
            df = pd.DataFrame(datos, columns=[categoria.title(), "Cantidad"])
            # In a real app, this would use Flet's file download feature
            # For now, we save it to a predefined path in the sandbox
            ruta_descarga = f"reporte_{categoria}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(ruta_descarga, index=False)
            mensaje.value = f"Reporte descargado en: {ruta_descarga}"
            page.update()

    # --- VIEW LAYOUT ---
    return ft.View("/admin/reporte_demografico", [
        ft.AppBar(title=ft.Text("Reportes Demográficos de Alumnos"), bgcolor=COLOR2_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(colors=[COLOR2_HEX, COLOR1_HEX]),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                categoria_dropdown,
                boton_descargar,
                mensaje,
                ft.Divider(),
                ft.Container(content=tabla_reporte, expand=True)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
