import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config import get_dark_mode
from theme import set_dark_theme, set_light_theme
import os
import logging
import sys
import appdirs
from utils.observer import Observable


VERSION = "1.0.1"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_base_path():
    if getattr(sys, 'frozen', False):
        # Si l'application est "gelée" (exécutable)
        return os.path.dirname(sys.executable)
    else:
        # Si l'application est en cours d'exécution à partir du script
        return os.path.dirname(os.path.abspath(__file__))


class MainApplication(ctk.CTk, Observable):
    def __init__(self):
        super().__init__()
        Observable.__init__(self)
        
        logging.debug("Initialisation de MainApplication")
        
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

        # Définir le dossier de données de l'application
        base_path = get_base_path()
        data_dir = os.path.join(base_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialiser le DatabaseManager avec un chemin persistant
        db_path = os.path.join(data_dir, 'suivi_usager.db')
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize()
        
        logging.debug("MainWindow créé")
        
        self.main_window = MainWindow(self, db_manager=self.db_manager, update_callback=self.update_interface)
        self.main_window.pack(fill=ctk.BOTH, expand=True)
        self.add_observer(self.main_window.dashboard)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Configure>", self.on_resize)

        self.last_theme = None

        logging.debug("Interface mise à jour")
        self.update_idletasks()
        self.update()

    def update_interface(self):
        self.notify_observers()
        logging.debug("Interface mise à jour")

    def on_closing(self):
        self.main_window.on_closing()
        self.quit()

    def on_resize(self, event):
        current_theme = ctk.get_appearance_mode()
        if hasattr(self, 'last_theme') and self.last_theme != current_theme:
            self.notify_observers()
        self.last_theme = current_theme


def main():
    logging.info(f"Chemin d'exécution : {os.getcwd()}")
    logging.info(f"Chemin du script : {os.path.abspath(__file__)}")
    logging.info(f"sys.executable : {sys.executable}")
    logging.info(f"sys._MEIPASS (si disponible) : {getattr(sys, '_MEIPASS', 'Non disponible')}")

    base_path = get_base_path()
    data_dir = os.path.join(base_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    logging.info(f"Dossier de données : {data_dir}")
    
    db_path = os.path.join(data_dir, 'suivi_usager.db')
    logging.info(f"Chemin de la base de données : {db_path}")

    logging.debug("Création de MainApplication")
    app = MainApplication()
    logging.debug("Démarrage de la boucle principale")
    app.mainloop()

if __name__ == "__main__":
    main()
