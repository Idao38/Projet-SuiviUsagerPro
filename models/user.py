from utils.date_utils import get_current_date, convert_to_db_date, convert_from_db_date
from datetime import datetime

class User:
    def __init__(self, id=None, nom=None, prenom=None, date_naissance=None, telephone=None, email=None, adresse=None, date_creation=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_creation = date_creation or datetime.now().strftime('%Y-%m-%d')

    @classmethod
    def from_db(cls, row):
        return cls(*row)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'date_creation': self.date_creation
        }

    def save(self, db_manager):
        if self.id:
            query = """UPDATE users SET nom=?, prenom=?, date_naissance=?, telephone=?, email=?, adresse=?
                       WHERE id=?"""
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.id)
        else:
            query = """INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse, date_creation)
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.date_creation)

        cursor = db_manager.execute_query(query, params)
        if not self.id:
            self.id = db_manager.get_last_insert_id()  # Utilisez une méthode de db_manager pour obtenir le dernier ID inséré

    @staticmethod
    def get_all(db_manager):
        query = "SELECT * FROM users"
        rows = db_manager.fetch_all(query)
        return [User.from_db(row) for row in rows]

    @classmethod
    def get_by_id(cls, db_manager, user_id):
        query = "SELECT id, nom, prenom, date_naissance, telephone, email, adresse, date_creation FROM users WHERE id = ?"
        result = db_manager.fetch_one(query, (user_id,))
        if result:
            return cls(*result)
        return None

    @staticmethod
    def get_inactive_users(db_manager, inactive_period):
        cutoff_date = (datetime.now() - inactive_period).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        SELECT u.* FROM users u
        LEFT JOIN workshops w ON u.id = w.user_id
        GROUP BY u.id
        HAVING MAX(w.date) < ? OR MAX(w.date) IS NULL
        """
        rows = db_manager.fetch_all(query, (cutoff_date,))
        return [User.from_db(row) for row in rows]

    def delete(self, db_manager):
        query = "DELETE FROM users WHERE id = ?"
        db_manager.execute_query(query, (self.id,))

    @staticmethod
    def delete_inactive_users(db_manager, inactive_period):
        cutoff_date = (datetime.now() - inactive_period).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        DELETE FROM users
        WHERE id IN (
            SELECT u.id FROM users u
            LEFT JOIN workshops w ON u.id = w.user_id
            GROUP BY u.id
            HAVING MAX(w.date) < ? OR MAX(w.date) IS NULL
        )
        """
        db_manager.execute_query(query, (cutoff_date,))

    @property
    def last_activity_date(self):
        # Cette méthode devrait être implémentée pour retourner la date de la dernière activité de l'utilisateur
        # Elle pourrait nécessiter une requête à la base de données pour obtenir la date du dernier atelier
        pass

    @classmethod
    def delete(cls, db_manager, user_id):
        # Supprimer d'abord les ateliers associés
        db_manager.execute_query("DELETE FROM workshops WHERE user_id = ?", (user_id,))
        # Puis supprimer l'utilisateur
        db_manager.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
