from utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime
import logging
from models.user import User

class Workshop:
    def __init__(self, id=None, user_id=None, description=None, categorie=None, payant=False, paid=False, date=None, conseiller=None):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.categorie = categorie
        self.payant = payant
        self.paid = paid 
        self.date = date
        self.conseiller = conseiller

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row['id'],
            user_id=row['user_id'] if row['user_id'] is not None else None,
            description=row['description'],
            categorie=row['categorie'],
            payant=row['payant'],
            paid=row['paid'],  
            date=row['date'],
            conseiller=row['conseiller']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'categorie': self.categorie,
            'payant': self.payant,
            'paid': self.paid, 
            'date': self.date,
            'conseiller': self.conseiller
        }

    def save(self, db_manager):
        if self.id is None:
            query = """
            INSERT INTO workshops (user_id, description, categorie, payant, paid, date, conseiller)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.paid, self.date, self.conseiller)
        else:
            query = """
            UPDATE workshops
            SET user_id=?, description=?, categorie=?, payant=?, paid=?, date=?, conseiller=?
            WHERE id=?
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.paid, self.date, self.conseiller, self.id)

        db_manager.execute(query, params)
        if self.id is None:
            self.id = db_manager.get_last_insert_id()
        
        # Mise à jour de la date de dernière activité de l'utilisateur
        if self.user_id:
            user = User.get_by_id(db_manager, self.user_id)
            if user:
                user.last_activity_date = self.date
                user.save(db_manager)
        
        return self.id

    @staticmethod
    def get_all(db_manager):
        query = "SELECT * FROM workshops"
        return db_manager.fetch_all(query)

    @staticmethod
    def get_by_id(db_manager, workshop_id):
        query = "SELECT * FROM workshops WHERE id = ?"
        row = db_manager.fetch_one(query, (workshop_id,))
        if row:
            workshop = Workshop.from_db(row)
            if workshop.user_id is None:
                workshop.user_id = None
            return workshop
        return None

    @staticmethod
    def get_by_user(db_manager, user_id):
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date DESC"
        rows = db_manager.fetch_all(query, (user_id,))
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def delete(cls, db_manager, workshop_id):
        query = "DELETE FROM workshops WHERE id = ?"
        db_manager.execute(query, (workshop_id,))

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
            logging.debug(f"Fetched results: {results}")
            workshops = []
            for row in results:
                logging.debug(f"Processing row: {row}")
                workshop = cls(
                    id=row['id'],
                    user_id=row['user_id'],
                    description=row['description'],
                    categorie=row['categorie'],
                    payant=row['payant'],
                    paid=row['paid'], 
                    date=convert_from_db_date(row['date']),  # Convertir la date du format DB au format DD/MM/YYYY
                    conseiller=row['conseiller']
                )
                workshop.user_nom = row['nom']
                workshop.user_prenom = row['prenom']
                workshops.append(workshop)
            return workshops
        except Exception as e:
            logging.error(f"Error fetching workshops with users: {e}")
            logging.exception("Detailed error:")
            return []

    @staticmethod
    def get_orphan_workshops(db_manager):
        query = "SELECT * FROM workshops WHERE user_id IS NULL"
        rows = db_manager.fetch_all(query)
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def get_paginated_with_users(cls, db_manager, offset, limit):
        query = """
        SELECT w.*, u.nom, u.prenom
        FROM workshops w
        JOIN users u ON w.user_id = u.id
        ORDER BY w.date DESC, w.id DESC
        LIMIT ? OFFSET ?
        """
        results = db_manager.fetch_all(query, (limit, offset))
        return [cls.from_db_with_user(row) for row in results]

    @classmethod
    def from_db_with_user(cls, row):
        workshop = cls.from_db(row)
        workshop.user_nom = row['nom']
        workshop.user_prenom = row['prenom']
        return workshop

    @staticmethod
    def get_user_workshops(db_manager, user_id):
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date"
        rows = db_manager.fetch_all(query, (user_id,))
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row['id'],
            user_id=row['user_id'] if row['user_id'] is not None else None,
            description=row['description'],
            categorie=row['categorie'],
            payant=row['payant'],
            paid=row['paid'],  
            date=row['date'],
            conseiller=row['conseiller']
        )
