from utils.date_utils import get_current_date, convert_to_db_date, convert_from_db_date

class Workshop:
    def __init__(self, id=None, user_id=None, description=None, categorie=None, payant=False, date=None, conseiller=None):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.categorie = categorie
        self.payant = payant
        self.date = date or get_current_date()
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
            self.id = db_manager.execute_query(query, params)
        else:
            query = """
            UPDATE workshops
            SET user_id=?, description=?, categorie=?, payant=?, date=?, conseiller=?
            WHERE id=?
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.date, self.conseiller, self.id)
            db_manager.execute_query(query, params)

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
