import customtkinter as ctk
from database.db_manager import DatabaseManager
from utils.date_utils import convert_from_db_date
from models.workshop import Workshop


class WorkshopHistory(ctk.CTkFrame):
    def __init__(self, master, db_manager=None, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Historique des ateliers", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Tableau d'historique
        self.history_frame = ctk.CTkFrame(self)
        self.history_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.history_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Nom", "Prénom", "Date", "Type d'atelier", "Conseiller"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.history_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        self.load_history()

    def load_history(self):
        workshops = Workshop.get_all_with_users(self.db_manager)

        for widget in self.history_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("font").cget("weight") != "bold":
                widget.destroy()

        for row, workshop in enumerate(workshops, start=1):
            ctk.CTkLabel(self.history_frame, text=workshop.user_nom).grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.history_frame, text=workshop.user_prenom).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.history_frame, text=workshop.date).grid(row=row, column=2, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.history_frame, text=workshop.categorie).grid(row=row, column=3, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(self.history_frame, text=workshop.conseiller).grid(row=row, column=4, padx=10, pady=5, sticky="ew")

    def load_workshops(self):
        # Rechargez l'historique des ateliers
        pass
