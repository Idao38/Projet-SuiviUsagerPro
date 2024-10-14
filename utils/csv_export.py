import csv
import logging
from tkinter import filedialog
from utils.date_utils import convert_from_db_date, is_valid_date
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w')

class CSVExporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.export_dir = None  # Initialisation de export_dir

    def export_users(self):
        if self.export_dir is None:
            self.export_dir = filedialog.askdirectory(title="Choisir le dossier pour l'exportation des utilisateurs")
        if not self.export_dir:
            return False, "L'exportation des utilisateurs a été annulée."

        file_path = os.path.join(self.export_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not file_path:
            return False, "L'exportation des utilisateurs a été annulée."

        try:
            users = self.db_manager.get_all_users()
            logging.info(f"Nombre d'utilisateurs récupérés : {len(users)}")
            for user in users:
                logging.debug(f"Utilisateur : {vars(user)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 'Email', 'Adresse', 'Date de création'])
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        convert_from_db_date(user.date_naissance) if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        convert_from_db_date(user.date_creation)
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des utilisateurs : {str(e)}"

    def export_workshops(self):
        if self.export_dir is None:
            self.export_dir = filedialog.askdirectory(title="Choisir le dossier pour l'exportation des ateliers")
        if not self.export_dir:
            return False, "L'exportation des ateliers a été annulée."

        file_path = os.path.join(self.export_dir, f"workshops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not file_path:
            return False, "L'exportation des ateliers a été annulée."

        try:
            workshops = self.db_manager.get_all_workshops()
            logging.info(f"Nombre d'ateliers récupérés : {len(workshops)}")
            for workshop in workshops:
                logging.debug(f"Atelier : {vars(workshop)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'User ID', 'Description', 'Catégorie', 'Payant', 'Date', 'Conseiller'])
                for workshop in workshops:
                    writer.writerow([
                        workshop.id,
                        workshop.user_id,
                        workshop.description,
                        workshop.categorie,
                        'Oui' if workshop.payant else 'Non',
                        convert_from_db_date(workshop.date),
                        workshop.conseiller
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des ateliers : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des ateliers : {str(e)}"

    def export_all_data(self):
        self.export_dir = filedialog.askdirectory(title="Choisir le dossier pour l'exportation de toutes les données")
        if not self.export_dir:
            return False, "L'exportation de toutes les données a été annulée."

        try:
            users_file = f"{self.export_dir}/users_export.csv"
            workshops_file = f"{self.export_dir}/workshops_export.csv"

            users_success, users_message = self.export_users_to_file(users_file)
            workshops_success, workshops_message = self.export_workshops_to_file(workshops_file)

            if users_success and workshops_success:
                return True, f"Toutes les données ont été exportées avec succès dans {self.export_dir}"
            elif users_success:
                return False, f"Exportation partielle : {users_message}. Erreur pour les ateliers : {workshops_message}"
            elif workshops_success:
                return False, f"Exportation partielle : {workshops_message}. Erreur pour les utilisateurs : {users_message}"
            else:
                return False, f"Échec de l'exportation : {users_message}, {workshops_message}"

        except Exception as e:
            return False, f"Une erreur s'est produite lors de l'exportation de toutes les données : {str(e)}"

    def export_users_to_file(self, file_path):
        try:
            users = self.db_manager.get_all_users()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 'Email', 'Adresse', 'Date de création'])
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        user.date_naissance if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        user.date_creation if user.date_creation else ''
                    ])
            return True, f"Les données des utilisateurs ont été exportées avec succès"
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs : {str(e)}", exc_info=True)
            return False, f"Erreur lors de l'exportation des utilisateurs : {str(e)}"

    def export_workshops_to_file(self, file_path):
        try:
            workshops = self.db_manager.get_all_workshops()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'User ID', 'Description', 'Catégorie', 'Payant', 'Date', 'Conseiller'])
                for workshop in workshops:
                    writer.writerow([
                        workshop.id,
                        workshop.user_id,
                        workshop.description,
                        workshop.categorie,
                        'Oui' if workshop.payant else 'Non',
                        workshop.date if workshop.date else '',
                        workshop.conseiller
                    ])
            return True, f"Les données des ateliers ont été exportées avec succès"
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des ateliers : {str(e)}", exc_info=True)
            return False, f"Erreur lors de l'exportation des ateliers : {str(e)}"
