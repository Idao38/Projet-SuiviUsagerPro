from dateutil import parser
from datetime import datetime
import re

def convert_to_db_date(date_string):
    """
    Convertit une date du format DD/MM/YYYY au format YYYY-MM-DD.
    """
    if not date_string:
        return None
    if not is_valid_date(date_string):
        return date_string  # Retourner la date telle quelle si elle n'est pas au format DD/MM/YYYY
    day, month, year = date_string.split('/')
    return f"{year}-{month}-{day}"

def convert_from_db_date(db_date):
    """
    Convertit une date du format YYYY-MM-DD ou DD/MM/YYYY au format DD/MM/YYYY.
    """
    try:
        # Essaie d'abord le format YYYY-MM-DD
        return datetime.strptime(db_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        try:
            # Si ça échoue, essaie le format DD/MM/YYYY
            datetime.strptime(db_date, '%d/%m/%Y')
            return db_date  # La date est déjà au bon format
        except ValueError:
            raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD ou DD/MM/YYYY.")

def is_valid_date(date_string):
    """
    Vérifie si la chaîne de date est au format DD/MM/YYYY et représente une date valide.
    """
    # Vérifie d'abord le format avec une expression régulière
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_string):
        return False
    
    # Essaie de convertir la chaîne en objet date
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def get_current_date():
    """
    Retourne la date actuelle au format JJ/MM/AAAA.
    
    Returns:
    str: La date actuelle au format JJ/MM/AAAA.
    """
    return datetime.now().strftime("%d/%m/%Y")
