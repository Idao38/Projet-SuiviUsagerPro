from datetime import datetime
from utils.csv_export import CSVExporter
from utils.date_utils import convert_to_db_date, convert_from_db_date


class RGPDManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_inactive_users(self, inactivity_period):
        cutoff_date = datetime.now() - inactivity_period
        query = """
        SELECT u.*, MAX(DATE(w.date)) as last_activity_date FROM users u
        LEFT JOIN workshops w ON u.id = w.user_id
        GROUP BY u.id
        HAVING last_activity_date < ? OR last_activity_date IS NULL
        """
        return self.db_manager.fetch_all(query, (convert_to_db_date(cutoff_date.strftime("%d/%m/%Y")),))

    def delete_inactive_user(self, user):
        # Supprimer d'abord les ateliers associés à l'utilisateur
        self.db_manager.execute("DELETE FROM workshops WHERE user_id = ?", (user.id,))
        # Ensuite, supprimer l'utilisateur
        self.db_manager.execute("DELETE FROM users WHERE id = ?", (user.id,))

    def delete_all_inactive_users(self, inactivity_period):
        inactive_users = self.get_inactive_users(inactivity_period)
        for user in inactive_users:
            self.delete_inactive_user(user)

    def export_inactive_users(self, inactivity_period, filename):
        inactive_users = self.get_inactive_users(inactivity_period)
        CSVExporter.export_users(inactive_users, filename)