from utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime
import logging
from datetime import timedelta
from utils.config_utils import get_ateliers_entre_paiements


class User:
    def __init__(self, id=None, nom="", prenom="", date_naissance=None, telephone="", email=None, adresse=None, date_creation=None, last_activity_date=None, last_payment_date=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance  # Ne pas convertir ici
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y")  # Format JJ/MM/AAAA
        self.last_activity_date = last_activity_date
        self.last_payment_date = last_payment_date

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
            date_creation=row['date_creation'],
            last_activity_date=row['last_activity_date'] if 'last_activity_date' in row.keys() else None,
            last_payment_date=row['last_payment_date'] if 'last_payment_date' in row.keys() else None
        )
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
                INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse, date_creation, last_activity_date, last_payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (self.nom, self.prenom, convert_to_db_date(self.date_naissance), self.telephone, self.email, self.adresse, self.date_creation, self.last_activity_date, None)
            db_manager.execute(query, values)
            self.id = db_manager.get_last_insert_id()
        else:
            query = """
                UPDATE users
                SET nom=?, prenom=?, date_naissance=?, telephone=?, email=?, adresse=?, date_creation=?, last_activity_date=?, last_payment_date=?
                WHERE id=?
            """
            values = (self.nom, self.prenom, convert_to_db_date(self.date_naissance), self.telephone, self.email, self.adresse, self.date_creation, self.last_activity_date, self.last_payment_date, self.id)
            db_manager.execute(query, values)

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

    @staticmethod
    def get_paginated(db_manager, offset, limit):
        query = "SELECT * FROM users ORDER BY nom, prenom LIMIT ? OFFSET ?"
        rows = db_manager.fetch_all(query, (limit, offset))
        return [User.from_db(row) for row in rows]

    def is_workshop_payment_up_to_date(self, db_manager):
        ateliers_entre_paiements = get_ateliers_entre_paiements()
        
        query = """
        WITH paid_workshops AS (
            SELECT ROW_NUMBER() OVER (ORDER BY date) as row_num, date, paid_today
            FROM workshops
            WHERE user_id = ? AND paid_today = 1
        )
        SELECT COUNT(*) as total_paid_workshops,
               (SELECT COUNT(*) FROM paid_workshops WHERE date <= ?) as paid_workshops_count,
               (SELECT COUNT(*) FROM paid_workshops WHERE row_num % ? = 1) as payments_made,
               (SELECT COUNT(*) FROM paid_workshops WHERE row_num > (SELECT MAX(row_num) FROM paid_workshops) - ?) as last_payment_check
        FROM paid_workshops
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        result = db_manager.fetch_one(query, (self.id, current_date, ateliers_entre_paiements, ateliers_entre_paiements))
        
        if result:
            total_paid_workshops = result['total_paid_workshops']
            paid_workshops_count = result['paid_workshops_count']
            payments_made = result['payments_made']
            last_payment_check = result['last_payment_check']
            
            if total_paid_workshops == 0:
                return True  # Aucun atelier payant, considéré comme à jour
            
            payments_required = (total_paid_workshops - 1) // ateliers_entre_paiements + 1
            
            return payments_made >= payments_required and last_payment_check > 0
        
        return True  # Si aucun atelier payant, considéré comme à jour

    def get_workshop_payment_status(self, db_manager):
        is_up_to_date = self.is_workshop_payment_up_to_date(db_manager)
        return "À jour" if is_up_to_date else "En retard"

    def update_last_payment_date(self, db_manager):
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = "UPDATE users SET last_payment_date = ? WHERE id = ?"
        db_manager.execute(query, (current_date, self.id))

    def update_payment_status(self, db_manager):
        self.payment_status = self.get_workshop_payment_status(db_manager)
