from utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime
import logging

class Workshop:
    def __init__(self, id=None, user_id=None, description=None, categorie=None, payant=False, date=None, conseiller=None):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.categorie = categorie
        self.payant = payant
        self.date = convert_to_db_date(date) if date else datetime.now().strftime("%Y-%m-%d")
        self.conseiller = conseiller

    @classmethod
    def from_db(cls, row):
        return cls(*row)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'categorie': self.categorie,
            'payant': self.payant,
            'date': self.date,
            'conseiller': self.conseiller
        }

    def save(self, db_manager):
        if self.id is None:
            query = """
            INSERT INTO workshops (user_id, description, categorie, payant, date, conseiller)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.date, self.conseiller)
        else:
            query = """
            UPDATE workshops
            SET user_id=?, description=?, categorie=?, payant=?, date=?, conseiller=?
            WHERE id=?
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.date, self.conseiller, self.id)

        try:
            cursor = db_manager.execute(query, params)
            if self.id is None:
                self.id = cursor.lastrowid
            return self.id
        except Exception as e:
            logging.error(f"Error saving workshop: {e}")
            raise

    @staticmethod
    def get_all(db_manager):
        query = "SELECT * FROM workshops"
        rows = db_manager.fetch_all(query)
        return [Workshop.from_db(row) for row in rows]

    @staticmethod
    def get_by_id(db_manager, workshop_id):
        query = "SELECT * FROM workshops WHERE id = ?"
        row = db_manager.fetch_one(query, (workshop_id,))
        return Workshop.from_db(row) if row else None

    @staticmethod
    def get_by_user(db_manager, user_id):
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date DESC"
        rows = db_manager.fetch_all(query, (user_id,))
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def delete(cls, db_manager, workshop_id):
        query = "DELETE FROM workshops WHERE id = ?"
        db_manager.execute_query(query, (workshop_id,))

    @classmethod
    def get_all_with_users(cls, db_manager):
        query = """
        SELECT w.*, u.nom, u.prenom
        FROM workshops w
        JOIN users u ON w.user_id = u.id
        ORDER BY w.date DESC
        LIMIT 50
        """
        try:
            results = db_manager.fetch_all(query)
            logging.debug(f"Fetched results: {results}")  # Ajoutez cette ligne
            workshops = []
            for row in results:
                logging.debug(f"Processing row: {row}")  # Ajoutez cette ligne
                workshop = cls(
                    id=row['id'],
                    user_id=row['user_id'],
                    description=row['description'],
                    categorie=row['categorie'],
                    payant=row['payant'],
                    date=row['date'],
                    conseiller=row['conseiller']
                )
                workshop.user_nom = row['nom']
                workshop.user_prenom = row['prenom']
                workshops.append(workshop)
            return workshops
        except Exception as e:
            logging.error(f"Error fetching workshops with users: {e}")
            logging.exception("Detailed error:")  # Ajoutez cette ligne pour voir la trace complète
            return []
