import sqlite3

def setup_database():
    """Crea todas las tablas necesarias para la aplicación en la base de datos formacion.db."""
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    # --- 0. Tabla de Inquilinos (Tenants) ---
    # La tabla principal para el modelo SaaS. Cada empresa cliente es un inquilino.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquilinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_empresa TEXT NOT NULL,
        fecha_suscripcion TEXT,
        plan TEXT, -- 'gratis', 'mensual', 'anual'
        api_key TEXT UNIQUE,
        activo INTEGER DEFAULT 1
    );
    """)

    # --- 1. Gestión de Usuarios y Roles (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_usuario TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin_empresa', 'admin_general', 'jefe_area', 'coordinador', 'profesor', 'alumno', 'almacenista', 'jefe_almacen', 'jefe_escenarios')),
        nombre_completo TEXT,
        correo TEXT,
        reporta_a_usuario_id INTEGER, -- For hierarchy
        reset_token TEXT,
        reset_token_expires TEXT,
        activo INTEGER DEFAULT 1,
        UNIQUE(inquilino_id, nombre_usuario),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (reporta_a_usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 2. Tablas Específicas por Rol (Ahora con inquilino_id) ---
    # Nota: El inquilino_id se puede obtener a través de la tabla de usuarios,
    # pero añadirlo aquí simplifica las consultas y el aislamiento de datos.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area TEXT,
        telefono TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_area (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area_responsabilidad TEXT, -- 'Cultura' o 'Deporte'
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS coordinadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        jefe_area_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (jefe_area_id) REFERENCES jefes_area(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_almacen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_escenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        tipo_documento TEXT,
        documento TEXT,
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
        UNIQUE(inquilino_id, documento),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS almacenistas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area_almacen TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    # --- 3. Tablas de Gestión Académica (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procesos_formacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_proceso TEXT NOT NULL,
        tipo_proceso TEXT,
        descripcion TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        ubicacion TEXT,
        capacidad INTEGER,
        tipo TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS escenario_partes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        escenario_id INTEGER NOT NULL,
        nombre_parte TEXT NOT NULL, -- e.g., "Cancha Principal", "Salón A"
        descripcion TEXT,
        capacidad INTEGER,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (escenario_id) REFERENCES escenarios(id)
    );

    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        escenario_parte_id INTEGER NOT NULL,
        usuario_id_reserva INTEGER NOT NULL,
        proposito TEXT, -- "Clase", "Evento", "Reunión", etc.
        descripcion_proposito TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        estado TEXT DEFAULT 'Confirmada', -- "Confirmada", "Cancelada"
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (escenario_parte_id) REFERENCES escenario_partes(id),
        FOREIGN KEY (usuario_id_reserva) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
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
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (proceso_id) REFERENCES procesos_formacion(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (escenario_id) REFERENCES escenarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_inscripcion TEXT,
        nivel_formacion TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_hora TEXT,
        evidencia_path TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    # --- 4. Tablas de Gestión de Inventario (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        codigo TEXT NOT NULL,
        descripcion TEXT,
        UNIQUE(inquilino_id, codigo),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
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
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (elemento_id) REFERENCES elementos(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (almacenista_id) REFERENCES almacenistas(id)
    );
    """)

    # --- 5. Tablas para Listas Desplegables (Pueden ser por inquilino o globales) ---
    # Por ahora, las haremos por inquilino para máxima flexibilidad.
    dropdown_tables = [
        "generos", "grupos_etarios", "tipos_documento", "escolaridades",
        "discapacidades", "grupos_poblacionales", "barrios", "veredas", "resguardos",
        "tipos_escenario"
    ]
    for table_name in dropdown_tables:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inquilino_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            UNIQUE(inquilino_id, nombre),
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
        );
        """)

    # --- Tablas adicionales (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre TEXT,
        tipo TEXT,
        fecha TEXT,
        descripcion TEXT,
        creado_por_id INTEGER,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (creado_por_id) REFERENCES profesores(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notificaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        usuario_id INTEGER,
        mensaje TEXT,
        fecha_hora TEXT,
        leido INTEGER DEFAULT 0,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    conn.commit()
    conn.close()
    print("Base de datos y tablas actualizadas para el modelo multi-inquilino.")

if __name__ == "__main__":
    setup_database()
