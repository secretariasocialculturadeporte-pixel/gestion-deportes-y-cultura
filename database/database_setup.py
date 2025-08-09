import sqlite3

def setup_database():
    """Crea todas las tablas necesarias para la aplicación en la base de datos formacion.db."""
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    # --- 1. Gestión de Usuarios y Roles ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'profesor', 'alumno', 'almacenista')),
        nombre_completo TEXT,
        correo TEXT UNIQUE,
        activo INTEGER DEFAULT 1
    );
    """)

    # --- 2. Tablas Específicas por Rol ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE,
        area TEXT,
        telefono TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE,
        tipo_documento TEXT,
        documento TEXT UNIQUE,
        fecha_nacimiento TEXT,
        genero TEXT,
        grupo_etario TEXT,
        escolaridad TEXT,
        discapacidad TEXT,
        grupo_poblacional TEXT,
        barrio TEXT,
        vereda TEXT,
        resguardo TEXT,
        zona_geografica TEXT,
        telefono TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS almacenistas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE,
        area_almacen TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 3. Tablas de Gestión Académica ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procesos_formacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_proceso TEXT NOT NULL,
        tipo_proceso TEXT,
        descripcion TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        ubicacion TEXT,
        capacidad INTEGER,
        tipo TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_clase TEXT,
        proceso_id INTEGER,
        instructor_id INTEGER,
        fecha TEXT,
        hora_inicio TEXT,
        hora_fin TEXT,
        escenario_id INTEGER,
        espacio TEXT,
        grupo TEXT,
        novedad TEXT,
        FOREIGN KEY (proceso_id) REFERENCES procesos_formacion(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (escenario_id) REFERENCES escenarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_inscripcion TEXT,
        nivel_formacion TEXT,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_hora TEXT,
        evidencia_path TEXT,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    # --- 4. Tablas de Gestión de Inventario ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        descripcion TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elemento_id INTEGER,
        instructor_id INTEGER,
        almacenista_id INTEGER,
        fecha_prestamo TEXT,
        observaciones_prestamo TEXT,
        foto_prestamo TEXT,
        estado TEXT,
        fecha_entrega TEXT,
        observaciones_entrega TEXT,
        foto_entrega TEXT,
        estado_entrega TEXT,
        FOREIGN KEY (elemento_id) REFERENCES elementos(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (almacenista_id) REFERENCES almacenistas(id)
    );
    """)

    # --- 5. Tablas para Listas Desplegables Dinámicas ---
    dropdown_tables = [
        "generos", "grupos_etarios", "tipos_documento", "escolaridades",
        "discapacidades", "grupos_poblacionales", "barrios", "veredas", "resguardos",
        "tipos_escenario"
    ]
    for table_name in dropdown_tables:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );
        """)

    # --- Tablas adicionales (eventos, notificaciones) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        tipo TEXT,
        fecha TEXT,
        descripcion TEXT,
        creado_por_id INTEGER,
        FOREIGN KEY (creado_por_id) REFERENCES profesores(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notificaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        mensaje TEXT,
        fecha_hora TEXT,
        leido INTEGER DEFAULT 0,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    conn.commit()
    conn.close()
    print("Base de datos y tablas creadas exitosamente.")

if __name__ == "__main__":
    setup_database()
