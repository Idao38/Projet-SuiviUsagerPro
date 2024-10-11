from dateutil import parser
from datetime import datetime

def convert_to_db_date(date_string):
    """
    Convertit une chaîne de date en format de date pour la base de données (YYYY-MM-DD).
    
    Args:
    date_string (str): La chaîne de date à convertir.
    
    Returns:
    str: La date au format YYYY-MM-DD, ou None si la conversion échoue.
    """
    try:
        # Essayer de parser la chaîne de date
        parsed_date = parser.parse(date_string, dayfirst=True)
        
        # Convertir la date parsée en format YYYY-MM-DD
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        # print(f"Impossible de convertir la date : {date_string}")  # Commentez ou supprimez cette ligne
        return None

def convert_from_db_date(db_date):
    """
    Convertit une date en format de base de données (YYYY-MM-DD) en format JJ/MM/AAAA.
    
    Args:
    db_date (str): La date en format YYYY-MM-DD.
    
    Returns:
    str: La date en format JJ/MM/AAAA, ou None si la conversion échoue.
    """
    try:
        # Convertir la date en format JJ/MM/AAAA
        return datetime.strptime(db_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        # Si la conversion échoue, retourner None
        print(f"Impossible de convertir la date de la base de données : {db_date}")
        return None

def is_valid_date(date_string):
    """
    Vérifie si une chaîne peut être convertie en date valide.
    
    Args:
    date_string (str): La chaîne de date à vérifier.
    
    Returns:
    bool: True si la chaîne est une date valide, False sinon.
    """
    try:
        parser.parse(date_string, dayfirst=True)
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
