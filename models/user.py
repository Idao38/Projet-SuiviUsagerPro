from datetime import datetime, timedelta

class User:
    def __init__(self, id=None, nom=None, prenom=None, date_naissance=None, telephone=None, email=None, adresse=None, date_creation=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_creation = date_creation or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        if self.id is None:
            query = """
            INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.date_creation)
        else:
            query = """
            UPDATE users
            SET nom=?, prenom=?, date_naissance=?, telephone=?, email=?, adresse=?
            WHERE id=?
            """
            params = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.id)
        
        db_manager.execute_query(query, params)

    @staticmethod
    def get_all(db_manager):
        query = "SELECT * FROM users"
        rows = db_manager.fetch_all(query)
        return [User.from_db(row) for row in rows]

    @staticmethod
    def get_by_id(db_manager, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        row = db_manager.fetch_one(query, (user_id,))
        return User.from_db(row) if row else None

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
