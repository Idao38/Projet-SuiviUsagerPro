import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config import get_dark_mode
from theme import set_dark_theme, set_light_theme
import os
import logging


VERSION = "1.0.0"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry("1100x700")
        self.title("Gestion des Usagers - Version " + VERSION)
        self.minsize(1000, 600)

        # Initialiser le mode d'apparence en fonction de la configuration
        is_dark = get_dark_mode()
        ctk.set_appearance_mode("dark" if is_dark else "light")
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()

        # Créer le dossier data s'il n'existe pas
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialiser le DatabaseManager avec un chemin persistant
        db_path = os.path.join(data_dir, 'suivi_usager.db')
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize()
        
        self.main_window = MainWindow(self, db_manager=self.db_manager, update_callback=self.update_interface)
        self.main_window.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_interface(self):
        # Mettez à jour toutes les parties nécessaires de l'interface utilisateur
        if hasattr(self.main_window, 'user_management'):
            self.main_window.user_management.refresh_user_list()
        if hasattr(self.main_window, 'workshop_history'):
            self.main_window.workshop_history.refresh_workshop_list()
        # Ajoutez d'autres mises à jour si nécessaire
        logging.debug("Interface mise à jour")

    def on_closing(self):
        self.main_window.on_closing()
        self.quit()


def main():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    main()
