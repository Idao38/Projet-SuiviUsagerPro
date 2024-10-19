import csv
import logging
from utils.date_utils import convert_from_db_date, is_valid_date, convert_to_db_date
import os
from datetime import datetime
from models.user import User
from models.workshop import Workshop
from utils.observer import Observable

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w')

class CSVExporter(Observable):
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_users(self):
        file_path = os.path.join(self.export_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        try:
            users = self.db_manager.get_all_users()
            logging.info(f"Nombre d'utilisateurs récupérés : {len(users)}")
            for user in users:
                logging.debug(f"Utilisateur : {vars(user)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 'Email', 'Adresse', 'Date de création', 'Dernière activité', 'Dernier paiement'])
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        convert_from_db_date(user.date_naissance) if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        convert_from_db_date(user.date_creation),
                        convert_from_db_date(user.last_activity_date) if user.last_activity_date else '',
                        convert_from_db_date(user.last_payment_date) if user.last_payment_date else ''
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des utilisateurs : {str(e)}"

    def export_workshops(self):
        file_path = os.path.join(self.export_dir, f"workshops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        try:
            workshops = self.db_manager.get_all_workshops()
            logging.info(f"Nombre d'ateliers récupérés : {len(workshops)}")
            for workshop in workshops:
                logging.debug(f"Atelier : {vars(workshop)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'User ID', 'Description', 'Catégorie', 'Payant', 'Payé', 'Date', 'Conseiller'])
                for workshop in workshops:
                    writer.writerow([
                        workshop.id,
                        workshop.user_id,
                        workshop.description,
                        workshop.categorie,
                        'Oui' if workshop.payant else 'Non',
                        'Oui' if workshop.paid else 'Non',
                        convert_from_db_date(workshop.date),
                        workshop.conseiller
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des ateliers : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des ateliers : {str(e)}"

    def export_all_data(self):
        try:
            users_file = os.path.join(self.export_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            workshops_file = os.path.join(self.export_dir, f"workshops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

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
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 'Email', 'Adresse', 'Date de création', 'Dernière activité', 'Dernier paiement'])
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        user.date_naissance if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        user.date_creation if user.date_creation else '',
                        user.last_activity_date if user.last_activity_date else '',
                        user.last_payment_date if user.last_payment_date else ''
                    ])
            return True, f"Les données des utilisateurs ont été exportées avec succès dans {file_path}"
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs : {str(e)}", exc_info=True)
            return False, f"Erreur lors de l'exportation des utilisateurs : {str(e)}"

    def export_workshops_to_file(self, file_path):
        try:
            workshops = self.db_manager.get_all_workshops()
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'User ID', 'Description', 'Catégorie', 'Payant', 'Payé', 'Date', 'Conseiller'])
                for workshop in workshops:
                    writer.writerow([
                        workshop.id,
                        workshop.user_id,
                        workshop.description,
                        workshop.categorie,
                        'Oui' if workshop.payant else 'Non',
                        'Oui' if workshop.paid else 'Non',
                        workshop.date if workshop.date else '',
                        workshop.conseiller
                    ])
            return True, f"Les données des ateliers ont été exportées avec succès dans {file_path}"
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des ateliers : {str(e)}", exc_info=True)
            return False, f"Erreur lors de l'exportation des ateliers : {str(e)}"

    def import_data(self, file_path):
        logging.info(f"Début de l'importation du fichier : {file_path}")
        errors = []
        imported_count = {'users': 0, 'workshops': 0}
        
        if not os.path.exists(file_path):
            logging.error(f"Le fichier {file_path} n'existe pas.")
            return False, f"Le fichier {file_path} n'existe pas."
        
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute("BEGIN TRANSACTION")
                logging.info("Transaction commencée")
                
                with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                    logging.info(f"Fichier ouvert : {file_path}")
                    # Utiliser un Sniffer pour détecter automatiquement le délimiteur
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample)
                        logging.info(f"Dialecte détecté : {dialect}")
                    except csv.Error as e:
                        logging.error(f"Erreur lors de la détection du dialecte CSV : {e}")
                        return False, f"Erreur lors de la détection du format CSV : {e}"
                    
                    reader = csv.DictReader(csvfile, dialect=dialect)
                    headers = reader.fieldnames
                    logging.info(f"En-têtes détectés : {headers}")
                    
                    if not headers:
                        logging.error("Aucun en-tête détecté dans le fichier CSV")
                        return False, "Format de fichier non reconnu ou invalide. Aucun en-tête détecté."
                    
                    if 'ID' in headers and all(header in headers for header in ['Nom', 'Prénom']):
                        logging.info("Importation d'utilisateurs détectée")
                        for row in reader:
                            try:
                                logging.debug(f"Tentative d'importation de l'utilisateur : {row}")
                                user = self.import_user(row)
                                user.save(self.db_manager)
                                logging.info(f"Utilisateur importé avec succès : ID {user.id}")
                                imported_count['users'] += 1
                            except Exception as e:
                                error_msg = f"Erreur lors de l'importation de l'utilisateur {row.get('ID', 'inconnu')}: {str(e)}"
                                logging.error(error_msg)
                                errors.append(error_msg)
                    elif 'User ID' in headers and all(header in headers for header in ['Description', 'Catégorie', 'Payant', 'Payé', 'Date', 'Conseiller']):
                        logging.info("Importation d'ateliers détectée")
                        for row in reader:
                            try:
                                logging.debug(f"Tentative d'importation de l'atelier : {row}")
                                workshop = self.import_workshop(row)
                                workshop.save(self.db_manager)
                                logging.info(f"Atelier importé avec succès : ID {workshop.id}")
                                imported_count['workshops'] += 1
                            except Exception as e:
                                error_msg = f"Erreur lors de l'importation de l'atelier pour l'utilisateur {row.get('User ID', 'inconnu')}: {str(e)}"
                                logging.error(error_msg)
                                errors.append(error_msg)
                    else:
                        logging.error(f"Format de fichier non reconnu. En-têtes : {headers}")
                        return False, "Format de fichier non reconnu. Assurez-vous d'importer un fichier CSV d'utilisateurs ou d'ateliers valide."
                
                conn.execute("COMMIT")
                logging.info("Transaction validée avec succès")
            
            logging.info(f"Importation terminée. Utilisateurs importés : {imported_count['users']}, Ateliers importés : {imported_count['workshops']}")
            return True, f"Importation réussie. {imported_count['users']} utilisateurs et {imported_count['workshops']} ateliers importés."
        
        except Exception as e:
            logging.error(f"Erreur lors de l'importation : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'importation : {str(e)}"

    def _verify_imported_users(self, imported_ids):
        check_query = "SELECT COUNT(*) as count FROM users WHERE id = ?"
        for user_id in imported_ids:
            result = self.db_manager.fetch_one(check_query, (user_id,))
            if result['count'] == 0:
                logging.error(f"L'utilisateur avec l'ID {user_id} n'a pas été importé correctement.")

    def _verify_imported_workshops(self, imported_ids):
        check_query = "SELECT COUNT(*) as count FROM workshops WHERE id = ?"
        for workshop_id in imported_ids:
            result = self.db_manager.fetch_one(check_query, (workshop_id,))
            if result['count'] == 0:
                logging.error(f"L'atelier avec l'ID {workshop_id} n'a pas été importé correctement.")

    def import_user(self, row):
        try:
            user = User(
                nom=row['Nom'],
                prenom=row.get('Prénom', ''),
                date_naissance=convert_to_db_date(row.get('Date de naissance', '')) if row.get('Date de naissance') else None,
                telephone=row.get('Téléphone', ''),
                email=row.get('Email', ''),
                adresse=row.get('Adresse', ''),
                date_creation=convert_to_db_date(row.get('Date de création', '')) if row.get('Date de création') else None,
                last_activity_date=convert_to_db_date(row.get('Dernière activité', '')) if row.get('Dernière activité') else None,
                last_payment_date=convert_to_db_date(row.get('Dernier paiement', '')) if row.get('Dernier paiement') else None
            )
            return user
        except KeyError as e:
            raise ValueError(f"Champ manquant dans les données utilisateur : {str(e)}")
        except ValueError as e:
            raise ValueError(f"Erreur de conversion de données pour l'utilisateur : {str(e)}")

    def import_workshop(self, row):
        try:
            date = row['Date']
            if date:
                # Essayer d'abord le format JJ/MM/YYYY
                try:
                    date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    # Si ça échoue, essayer le format YYYY-MM-DD
                    date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            workshop = Workshop(
                user_id=int(row['User ID']) if row['User ID'] else None,
                description=row['Description'],
                categorie=row['Catégorie'],
                payant=row['Payant'] == 'Oui',
                paid=row.get('Payé', 'Non') == 'Oui',
                date=date,
                conseiller=row['Conseiller']
            )
            
            # Mise à jour de la date de dernière activité de l'utilisateur
            if workshop.user_id and workshop.date:
                workshop_date = datetime.strptime(workshop.date, "%Y-%m-%d")
                if (datetime.now() - workshop_date).days <= 365:
                    user = User.get_by_id(self.db_manager, workshop.user_id)
                    if user:
                        user.update_last_activity_date(self.db_manager, workshop.date)
            
            return workshop
        except KeyError as e:
            raise ValueError(f"Champ manquant dans les données de l'atelier : {str(e)}")
        except ValueError as e:
            raise ValueError(f"Erreur de conversion de données pour l'atelier : {str(e)}")
