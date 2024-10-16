import random
from datetime import datetime, timedelta
from faker import Faker
from database.db_manager import DatabaseManager
from models.user import User
from models.workshop import Workshop
from utils.config_utils import get_conseillers, get_ateliers_entre_paiements, get_default_paid_workshops


fake = Faker('fr_FR')  # Utilise le locale français

db_manager = DatabaseManager('data/suivi_usager.db')
db_manager.initialize()

conseillers = get_conseillers()
ateliers_entre_paiements = get_ateliers_entre_paiements()

default_paid_workshops = get_default_paid_workshops()

def generate_users(num_users):
    for _ in range(num_users):
        user = User(
            nom=fake.last_name(),
            prenom=fake.first_name(),
            date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y"),
            telephone=fake.phone_number(),
            email=fake.email(),
            adresse=fake.address().replace('\n', ', '),
            last_payment_date=fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d")
        )
        user.save(db_manager)

def generate_workshops(num_workshops):
    users = User.get_all(db_manager)
    categories = ["Atelier numérique", "Démarche administrative"]
    
    for _ in range(num_workshops):
        user = random.choice(users)
        workshop_date = fake.date_between(start_date='-2y', end_date='today')
        categorie = random.choice(categories)
        is_payant = categorie in default_paid_workshops
        paid_today = is_payant and random.choice([True, False])
        
        workshop = Workshop(
            user_id=user.id,
            description=fake.sentence(),
            categorie=categorie,
            payant=is_payant,
            paid_today=paid_today,
            date=workshop_date.strftime("%d/%m/%Y"),
            conseiller=random.choice(conseillers)
        )
        workshop.save(db_manager)
        
        if paid_today:
            # Mise à jour de la date du dernier paiement si l'atelier est payé aujourd'hui
            user.update_last_payment_date(db_manager)

def update_payment_status():
    users = User.get_all(db_manager)
    for user in users:
        workshops = Workshop.get_user_workshops(db_manager, user.id)
        for workshop in workshops:
            if workshop.paid_today:
                user.update_last_payment_date(db_manager)

if __name__ == "__main__":
    num_users = 250  # Nombre d'utilisateurs à générer
    num_workshops = 500  # Nombre d'ateliers à générer

    print("Génération des utilisateurs...")
    generate_users(num_users)
    print(f"{num_users} utilisateurs générés.")

    print("Génération des ateliers...")
    generate_workshops(num_workshops)
    print(f"{num_workshops} ateliers générés.")

    print("Mise à jour des statuts de paiement...")
    update_payment_status()
    print("Statuts de paiement mis à jour.")

    print("Génération des données de test terminée.")
