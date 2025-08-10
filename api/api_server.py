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

def get_sales_reply(query: str) -> str:
    """
    A simple NLU for the sales agent.
    """
    query = query.lower()
    if "precio" in query or "planes" in query or "cuesta" in query:
        return "Ofrecemos un plan gratuito de 60 días para que pruebes todo. Después, el Plan Pro cuesta $100 al mes o $1000 al año, ¡lo que te ahorra dos meses! Incluye usuarios ilimitados y soporte prioritario."
    elif "funcionalidades" in query or "hace" in query:
        return "Nuestra plataforma te permite gestionar roles de usuario, jerarquías de personal, escenarios deportivos y culturales (con subdivisiones y calendario de reservas), inventario, clases, asistencias, ¡y mucho más!"
    elif "reservas" in query or "escenarios" in query:
        return "Sí, nuestro módulo de escenarios es muy potente. Puedes crear un escenario principal, como un polideportivo, y subdividirlo en 'partes' como 'Cancha A' o 'Salón de Conferencias'. Luego, puedes reservar cada parte por separado, evitando conflictos de horario."
    else:
        return "Gracias por tu pregunta. Nuestro sistema es una solución completa para la gestión de centros formativos. ¿Te gustaría saber sobre nuestros precios, funcionalidades o cómo funciona el sistema de reservas?"

@app.route('/api/sales_agent', methods=['POST'])
def handle_sales_query():
    """Handles questions for the sales agent."""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query in request body"}), 400

    query = data['query']
    reply = get_sales_reply(query)

    return jsonify({"reply": reply})

@app.route('/api/register_tenant', methods=['POST'])
def register_tenant():
    """Handles new tenant and admin user registration."""
    data = request.get_json()
    required_fields = ['nombre_empresa', 'nombre_admin', 'correo_admin', 'usuario_admin', 'password_admin']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan datos en la solicitud."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check for existing company or user
        empresa_existente = cursor.execute('SELECT id FROM inquilinos WHERE nombre_empresa = ?', (data['nombre_empresa'],)).fetchone()
        if empresa_existente:
            return jsonify({"error": "Ya existe una empresa con ese nombre."}), 409

        usuario_existente = cursor.execute('SELECT id FROM usuarios WHERE nombre_usuario = ?', (data['usuario_admin'],)).fetchone()
        if usuario_existente:
            return jsonify({"error": "El nombre de usuario del administrador ya está en uso."}), 409

        # Generate a new API key (simple version)
        import secrets
        new_api_key = secrets.token_hex(16)

        # Create the new tenant
        cursor.execute("INSERT INTO inquilinos (nombre_empresa, fecha_suscripcion, plan, api_key) VALUES (?, ?, ?, ?)",
                       (data['nombre_empresa'], sqlite3.datetime.now(), 'gratis_60', new_api_key))
        tenant_id = cursor.lastrowid

        # Create the admin user for the new tenant
        from views.login import hash_password
        cursor.execute("""
            INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo)
            VALUES (?, ?, ?, 'admin_empresa', ?, ?)
        """, (
            tenant_id, data['usuario_admin'], hash_password(data['password_admin']),
            data['nombre_admin'], data['correo_admin']
        ))

        conn.commit()
        return jsonify({"message": "Registro exitoso!", "empresa": data['nombre_empresa']}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Ocurrió un error en el servidor.", "details": str(e)}), 500
    finally:
        conn.close()

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees).
    """
    from math import radians, cos, sin, asin, sqrt
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers.
    return c * r

@app.route('/api/empresas_cercanas', methods=['GET'])
def get_nearby_tenants():
    """
    Finds tenants near the user's provided location.
    Expects 'lat' and 'lon' as query parameters.
    """
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)

    if user_lat is None or user_lon is None:
        return jsonify({"error": "Parámetros 'lat' y 'lon' son requeridos."}), 400

    try:
        conn = get_db_connection()
        # Get all tenants that have latitude and longitude set
        tenants_with_location = conn.execute(
            'SELECT id, nombre_empresa, direccion, municipio, latitud, longitud FROM inquilinos WHERE latitud IS NOT NULL AND longitud IS NOT NULL AND activo = 1'
        ).fetchall()
        conn.close()

        nearby_tenants = []
        for tenant in tenants_with_location:
            tenant_dict = dict(tenant)
            distance = haversine(user_lat, user_lon, tenant_dict['latitud'], tenant_dict['longitud'])
            tenant_dict['distancia_km'] = round(distance, 2)
            nearby_tenants.append(tenant_dict)

        # Sort tenants by distance, closest first, and return top 10
        sorted_tenants = sorted(nearby_tenants, key=lambda x: x['distancia_km'])

        return jsonify(sorted_tenants[:10])

    except Exception as e:
        return jsonify({"error": "Ocurrió un error en el servidor.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
