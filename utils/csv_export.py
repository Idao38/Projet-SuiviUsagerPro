import csv
import os
from datetime import datetime

class CSVExporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def export_users(self, filename):
        users = self.db_manager.get_all_users()
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Nom", "Prénom", "Date de naissance", "Téléphone", "Email", "Adresse", "Date de création"])
            for user in users:
                writer.writerow([user.id, user.nom, user.prenom, user.date_naissance, user.telephone, user.email, user.adresse, user.date_creation])

    def export_workshops(self, filename):
        workshops = self.db_manager.get_all_workshops()
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "ID Usager", "Description", "Catégorie", "Payant", "Date", "Conseiller"])
            for workshop in workshops:
                writer.writerow([workshop.id, workshop.user_id, workshop.description, workshop.categorie, workshop.payant, workshop.date, workshop.conseiller])

    def export_all_data(self):
        try:
            export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            users_filename = os.path.join(export_dir, f"users_export_{timestamp}.csv")
            workshops_filename = os.path.join(export_dir, f"workshops_export_{timestamp}.csv")
            
            self.export_users(users_filename)
            self.export_workshops(workshops_filename)
            
            return True, f"Les données ont été exportées avec succès dans le dossier 'exports'."
        except Exception as e:
            return False, f"Une erreur s'est produite lors de l'exportation : {str(e)}"
