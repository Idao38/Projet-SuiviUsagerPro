import random
from datetime import datetime, timedelta
from faker import Faker
from database.db_manager import DatabaseManager
from models.user import User
from models.workshop import Workshop
from config import get_conseillers

fake = Faker('fr_FR')  # Utilise le locale français

db_manager = DatabaseManager('data/suivi_usager.db')
db_manager.initialize()

conseillers = get_conseillers()

def generate_users(num_users):
    for _ in range(num_users):
        user = User(
            nom=fake.last_name(),
            prenom=fake.first_name(),
            date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y"),
            telephone=fake.phone_number(),
            email=fake.email(),
            adresse=fake.address().replace('\n', ', ')
        )
        user.save(db_manager)

def generate_workshops(num_workshops):
    users = User.get_all(db_manager)
    categories = ["Atelier numérique", "Démarche administrative"]
    
    for _ in range(num_workshops):
        user = random.choice(users)
        workshop = Workshop(
            user_id=user.id,
            description=fake.sentence(),
            categorie=random.choice(categories),
            payant=random.choice([True, False]),
            date=fake.date_between(start_date='-2y', end_date='today').strftime("%d/%m/%Y"),
            conseiller=random.choice(conseillers)
        )
        workshop.save(db_manager)

if __name__ == "__main__":
    num_users = 250  # Nombre d'utilisateurs à générer
    num_workshops = 1000  # Nombre d'ateliers à générer

    print("Génération des utilisateurs...")
    generate_users(num_users)
    print(f"{num_users} utilisateurs générés.")

    print("Génération des ateliers...")
    generate_workshops(num_workshops)
    print(f"{num_workshops} ateliers générés.")

    print("Génération des données de test terminée.")