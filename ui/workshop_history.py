import customtkinter as ctk
from database.db_manager import DatabaseManager
from utils.date_utils import convert_from_db_date
from models.workshop import Workshop


class WorkshopHistory(ctk.CTkFrame):
    def __init__(self, master, db_manager=None, edit_workshop_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.edit_workshop_callback = edit_workshop_callback
        self.workshops = []
        self.offset = 0
        self.limit = 25

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Historique des ateliers", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Tableau d'historique
        self.history_frame = ctk.CTkScrollableFrame(self)
        self.history_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.history_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Nom", "Prénom", "Date", "Type d'atelier", "Conseiller"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.history_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        # Bouton pour charger plus d'ateliers
        self.load_more_button = ctk.CTkButton(self, text="Charger plus", command=self.load_more_workshops)
        self.load_more_button.grid(row=2, column=0, pady=(0, 20), sticky="ew")

        self.load_history()

    def load_history(self):
        new_workshops = Workshop.get_paginated_with_users(self.db_manager, self.offset, self.limit)
        self.workshops.extend(new_workshops)
        self.display_workshops(new_workshops)
        self.offset += self.limit

        # Masquer le bouton si tous les ateliers sont chargés
        if len(new_workshops) < self.limit:
            self.load_more_button.grid_remove()

    def display_workshops(self, workshops):
        start_row = len(self.history_frame.winfo_children()) // 5  # 5 colonnes par atelier
        for i, workshop in enumerate(workshops, start=start_row):
            user = workshop.get_user(self.db_manager)
            row_frame = ctk.CTkFrame(self.history_frame)
            row_frame.grid(row=i, column=0, columnspan=5, sticky="ew", padx=5, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            row_frame.bind("<Button-1>", lambda e, w=workshop: self.on_workshop_click(w))

            labels = [
                ctk.CTkLabel(row_frame, text=user.nom if user else "N/A", anchor="w"),
                ctk.CTkLabel(row_frame, text=user.prenom if user else "N/A", anchor="w"),
                ctk.CTkLabel(row_frame, text=workshop.date, anchor="w"),
                ctk.CTkLabel(row_frame, text=workshop.categorie, anchor="w"),
                ctk.CTkLabel(row_frame, text=workshop.conseiller, anchor="w")
            ]

            for col, label in enumerate(labels):
                label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
                label.bind("<Button-1>", lambda e, w=workshop: self.on_workshop_click(w))

    def load_more_workshops(self):
        self.load_history()

    def refresh_workshop_list(self):
        # Réinitialiser la liste et recharger les ateliers
        self.workshops = []
        self.offset = 0
        for widget in self.history_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
        self.load_history()
        self.load_more_button.grid()

    def load_workshops(self):
        # Rechargez l'historique des ateliers
        pass

    def on_frame_configure(self, event):
        self.history_frame.configure(scrollregion=self.history_frame.bbox("all"))

    def on_mousewheel(self, event):
        if self.history_frame.winfo_height() < self.history_frame.bbox("all")[3]:
            if self.history_frame.yview()[1] >= 0.9:
                self.load_history()

    def on_workshop_click(self, workshop):
        if self.edit_workshop_callback:
            self.edit_workshop_callback(workshop)
