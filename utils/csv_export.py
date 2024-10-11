import csv

class CSVExporter:
    @staticmethod
    def export_users(users, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Nom", "Prénom", "Date de naissance", "Téléphone", "Email", "Adresse", "Date de création"])
            for user in users:
                writer.writerow([user.id, user.nom, user.prenom, user.date_naissance, user.telephone, user.email, user.adresse, user.date_creation])

    @staticmethod
    def export_workshops(workshops, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "ID Usager", "Description", "Catégorie", "Payant", "Date", "Conseiller"])
            for workshop in workshops:
                writer.writerow([workshop.id, workshop.user_id, workshop.description, workshop.categorie, workshop.payant, workshop.date, workshop.conseiller])
