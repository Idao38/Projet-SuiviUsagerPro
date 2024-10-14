from datetime import datetime, timedelta
from utils.csv_export import CSVExporter
from utils.date_utils import convert_to_db_date, convert_from_db_date
from models.user import User


class RGPDManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_inactive_users(self, inactivity_period_days):
        cutoff_date = datetime.now() - timedelta(days=inactivity_period_days)
        query = """
        SELECT u.*, MAX(COALESCE(w.date, u.date_creation)) as last_activity_date FROM users u
        LEFT JOIN workshops w ON u.id = w.user_id
        GROUP BY u.id
        HAVING last_activity_date < ? OR last_activity_date IS NULL
        """
        rows = self.db_manager.fetch_all(query, (convert_to_db_date(cutoff_date.strftime("%d/%m/%Y")),))
        return [User.from_db(row) for row in rows]

    def delete_inactive_user(self, user):
        # Mettre à jour les ateliers associés
        self.db_manager.execute("UPDATE workshops SET user_id = NULL WHERE user_id = ?", (user.id,))
        # Supprimer l'utilisateur
        User.delete(self.db_manager, user.id)

    def delete_all_inactive_users(self, inactivity_period_days):
        inactive_users = self.get_inactive_users(inactivity_period_days)
        for user in inactive_users:
            self.delete_inactive_user(user)
        return len(inactive_users)

    def export_inactive_users(self, inactivity_period_days, filename):
        inactive_users = self.get_inactive_users(inactivity_period_days)
        CSVExporter.export_users(inactive_users, filename)
