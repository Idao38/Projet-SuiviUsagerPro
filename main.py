import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config import get_dark_mode
from theme import set_dark_theme, set_light_theme
import os

VERSION = "0.6.0"

def main():
    # Initialiser le mode d'apparence en fonction de la configuration
    is_dark = get_dark_mode()
    ctk.set_appearance_mode("dark" if is_dark else "light")
    if is_dark:
        set_dark_theme()
    else:
        set_light_theme()
    
    app = ctk.CTk()
    app.geometry("1000x600")
    app.title("Gestion des Usagers")
    
    # Créer le dossier data s'il n'existe pas
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialiser le DatabaseManager avec un chemin persistant
    db_path = os.path.join(data_dir, 'suivi_usager.db')
    db_manager = DatabaseManager(db_path)
    db_manager.initialize()
    
    main_window = MainWindow(app, db_manager=db_manager)
    main_window.grid(row=0, column=0, sticky="nsew")
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    
    app.protocol("WM_DELETE_WINDOW", main_window.on_closing)  # Gestion de la fermeture de l'application
    
    app.mainloop()

if __name__ == "__main__":
    main()
