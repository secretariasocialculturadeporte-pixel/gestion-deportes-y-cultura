import sqlite3
from datetime import datetime

class GamificationEngine:
    def __init__(self, tenant_id: int, alumno_user_id: int):
        self.tenant_id = tenant_id
        self.alumno_user_id = alumno_user_id
        # We need the alumno_id (from the alumnos table), not the usuario_id
        self.conn = sqlite3.connect("formacion.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT id FROM alumnos WHERE usuario_id = ?", (self.alumno_user_id,))
        result = self.cursor.fetchone()
        self.alumno_id = result[0] if result else None

    def log_action(self, action_key: str):
        """
        Logs an action, grants points, and checks for new rewards.
        """
        if not self.alumno_id:
            print(f"Error de gamificación: no se encontró un perfil de alumno para el usuario {self.alumno_user_id}")
            return

        # 1. Get points for the action
        self.cursor.execute(
            "SELECT puntos FROM gamificacion_acciones WHERE inquilino_id = ? AND accion_key = ?",
            (self.tenant_id, action_key)
        )
        result = self.cursor.fetchone()
        if not result:
            print(f"Advertencia de gamificación: La acción '{action_key}' no está definida.")
            return

        points_to_add = result[0]

        # 2. Log the points earned
        self.cursor.execute("""
            INSERT INTO gamificacion_puntos_log (inquilino_id, alumno_id, accion_key, puntos_ganados, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (self.tenant_id, self.alumno_id, action_key, points_to_add, datetime.now().isoformat()))

        # 3. Update the student's total points
        self.cursor.execute(
            "UPDATE alumnos SET puntos_totales = puntos_totales + ? WHERE id = ?",
            (points_to_add, self.alumno_id)
        )

        # 4. Check for new badges/levels (placeholder for now)
        self._check_for_new_medals()
        self._check_for_level_up()

        self.conn.commit()
        print(f"Acción '{action_key}' registrada para el alumno {self.alumno_id}. Puntos ganados: {points_to_add}")

    def _check_for_new_medals(self):
        """Placeholder for medal-granting logic."""
        # Example: Check for "Asistencia Perfecta"
        # This would require more complex queries.
        pass

    def _check_for_level_up(self):
        """Placeholder for level-up logic."""
        # Example: Get current points and level, check against gamificacion_niveles table
        pass

    def __del__(self):
        """Ensure the connection is closed when the object is destroyed."""
        if self.conn:
            self.conn.close()

# Main function to be called from the app
def process_gamified_action(tenant_id: int, user_id: int, action_key: str):
    engine = GamificationEngine(tenant_id, user_id)
    engine.log_action(action_key)
