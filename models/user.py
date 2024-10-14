from utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime
import logging
from datetime import timedelta

class User:
    def __init__(self, id=None, nom="", prenom="", date_naissance=None, telephone="", email=None, adresse=None, date_creation=None, last_activity_date=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance  # Ne pas convertir ici
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y")  # Format JJ/MM/AAAA
        self.last_activity_date = last_activity_date

    @classmethod
    def from_db(cls, row):
        user = cls(
            id=row['id'],
            nom=row['nom'],
            prenom=row['prenom'],
            date_naissance=row['date_naissance'],
            telephone=row['telephone'],
            email=row['email'],
            adresse=row['adresse'],
            date_creation=row['date_creation']
        )
        user.last_activity_date = row['last_activity_date'] if 'last_activity_date' in row.keys() else None
        return user

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
        if self.id is None:
            query = """
                INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse, date_creation, last_activity_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.date_creation, self.last_activity_date)
        else:
            query = """
                UPDATE users
                SET nom=?, prenom=?, date_naissance=?, telephone=?, email=?, adresse=?, last_activity_date=?
                WHERE id=?
            """
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.last_activity_date, self.id)

        cursor = db_manager.execute(query, params)
        if self.id is None:
            self.id = cursor.lastrowid
        return self.id

    @staticmethod
    def get_all(db_manager):
        query = "SELECT id, nom, prenom, date_naissance, telephone, email, adresse, date_creation, last_activity_date FROM users"
        rows = db_manager.fetch_all(query)
        return [User.from_db(row) for row in rows]

    @classmethod
    def get_by_id(cls, db_manager, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        user_row = db_manager.fetch_one(query, (user_id,))
        if user_row:
            user_dict = dict(user_row)
            if user_dict['date_naissance']:
                user_dict['date_naissance'] = convert_from_db_date(user_dict['date_naissance'])
            return cls(**user_dict)
        return None

    @classmethod
    def get_inactive_users(cls, db_manager, inactivity_days):
        cutoff_date = datetime.now() - timedelta(days=inactivity_days)
        query = """
        SELECT u.*, MAX(COALESCE(w.date, u.date_creation)) as last_activity_date FROM users u
        LEFT JOIN workshops w ON u.id = w.user_id
        GROUP BY u.id
        HAVING last_activity_date < ? OR last_activity_date IS NULL
        """
        rows = db_manager.fetch_all(query, (cutoff_date.strftime("%Y-%m-%d"),))
        return [cls.from_db(row) for row in rows]

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
        if not hasattr(self, '_last_activity_date'):
            self._last_activity_date = None
        return self._last_activity_date

    @last_activity_date.setter
    def last_activity_date(self, value):
        self._last_activity_date = value

    def get_last_activity_date(self, db_manager):
        query = "SELECT MAX(date) as last_activity FROM workshops WHERE user_id = ?"
        result = db_manager.fetch_one(query, (self.id,))
        last_activity = result['last_activity'] if result and result['last_activity'] else None
        self.last_activity_date = last_activity
        return self.last_activity_date

    @classmethod
    def delete(cls, db_manager, user_id):
        # Mettre à jour les ateliers associés pour définir user_id à NULL
        db_manager.execute("UPDATE workshops SET user_id = NULL WHERE user_id = ?", (user_id,))
        # Ensuite, supprimez l'utilisateur
        db_manager.execute("DELETE FROM users WHERE id = ?", (user_id,))
