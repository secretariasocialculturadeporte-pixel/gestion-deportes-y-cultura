from flask import Flask, jsonify, request
from functools import wraps
import sqlite3

# --- Configuration ---
# In a real app, this would be in a config file or environment variable
API_KEY = "super_secret_api_key"
DATABASE_PATH = "../formacion.db" # The API is in a subdirectory

app = Flask(__name__)

# --- Database Connection ---
def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

# --- Authentication Decorator ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-KEY') and request.headers.get('X-API-KEY') == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized. API key is missing or invalid."}), 401
    return decorated_function

# --- API Endpoints ---
@app.route('/api/status', methods=['GET'])
def get_status():
    """A simple endpoint to check if the API is running."""
    return jsonify({"status": "ok", "message": "API is running."})

@app.route('/api/test_db', methods=['GET'])
@require_api_key
def test_db():
    """An endpoint to test database connectivity."""
    try:
        conn = get_db_connection()
        users = conn.execute('SELECT nombre_usuario, rol FROM usuarios').fetchall()
        conn.close()
        # Convert rows to list of dicts
        user_list = [dict(row) for row in users]
        return jsonify({"status": "ok", "user_count": len(user_list), "users": user_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reportes/asistencia', methods=['GET'])
@require_api_key
def get_reporte_asistencia():
    """Returns the attendance report."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                a.nombre_completo AS Alumno,
                p.nombre_proceso AS Proceso,
                c.nombre_clase AS Clase,
                ast.fecha_hora AS Fecha_Asistencia
            FROM asistencias ast
            JOIN alumnos al ON ast.alumno_id = al.id
            JOIN usuarios a ON al.usuario_id = a.id
            JOIN clases c ON ast.clase_id = c.id
            JOIN procesos_formacion p ON c.proceso_id = p.id
            ORDER BY ast.fecha_hora DESC
        """
        report_data = conn.execute(query).fetchall()
        conn.close()
        report_list = [dict(row) for row in report_data]
        return jsonify(report_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    # Running on port 5001 to avoid potential conflicts with Flet
    app.run(debug=True, port=5001)
