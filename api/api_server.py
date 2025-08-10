from flask import Flask, jsonify, request, g
from functools import wraps
import sqlite3

# --- Configuration ---
DATABASE_PATH = "../formacion.db"

app = Flask(__name__)

# --- Database Connection ---
def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication Decorator ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({"error": "Unauthorized. API key is missing."}), 401

        # Look up the tenant associated with the API key
        conn = get_db_connection()
        tenant = conn.execute('SELECT id FROM inquilinos WHERE api_key = ? AND activo = 1', (api_key,)).fetchone()
        conn.close()

        if tenant:
            # Store tenant_id in Flask's application context `g` for this request
            g.tenant_id = tenant['id']
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized. API key is invalid or tenant is inactive."}), 401

    return decorated_function

# --- API Endpoints ---
@app.route('/api/status', methods=['GET'])
def get_status():
    """A simple endpoint to check if the API is running."""
    return jsonify({"status": "ok", "message": "API is running."})

@app.route('/api/reportes/asistencia', methods=['GET'])
@require_api_key
def get_reporte_asistencia():
    """Returns the attendance report for the authenticated tenant."""
    tenant_id = g.tenant_id # Get tenant_id from the application context
    try:
        conn = get_db_connection()
        query = """
            SELECT
                u.nombre_completo AS Alumno,
                p.nombre_proceso AS Proceso,
                c.nombre_clase AS Clase,
                ast.fecha_hora AS Fecha_Asistencia
            FROM asistencias ast
            JOIN alumnos al ON ast.alumno_id = al.id
            JOIN usuarios u ON al.usuario_id = u.id
            JOIN clases c ON ast.clase_id = c.id
            JOIN procesos_formacion p ON c.proceso_id = p.id
            WHERE ast.inquilino_id = ?
            ORDER BY ast.fecha_hora DESC
        """
        report_data = conn.execute(query, (tenant_id,)).fetchall()
        conn.close()
        report_list = [dict(row) for row in report_data]
        return jsonify(report_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
