import customtkinter as ctk
from tkinter import messagebox
from models.user import User
from models.workshop import Workshop
from datetime import datetime, timedelta
import csv
from utils.date_utils import convert_from_db_date

class UserManagement(ctk.CTkFrame):
    def __init__(self, master, db_manager, edit_user_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.edit_user_callback = edit_user_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Gestion des usagers", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Liste des usagers
        self.user_list = ctk.CTkScrollableFrame(self)
        self.user_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Ajoutez cette ligne pour créer l'attribut search_entry
        self.search_entry = ctk.CTkEntry(self)

        # Chargement initial des usagers
        self.load_users()

    def load_users(self):
        # Vérifier si le widget user_list existe toujours
        if hasattr(self, 'user_list') and self.user_list.winfo_exists():
            for widget in self.user_list.winfo_children():
                widget.destroy()
        else:
            # Recréer le widget user_list s'il n'existe plus
            self.user_list = ctk.CTkScrollableFrame(self)
            self.user_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Charger les usagers depuis la base de données
        users = User.get_all(self.db_manager)

        # Afficher chaque usager dans la liste
        for user in users:
            user_frame = ctk.CTkFrame(self.user_list)
            user_frame.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom}")
            name_label.pack(side="left", padx=5)

            # Bouton de suppression
            delete_button = ctk.CTkButton(user_frame, text="Supprimer", command=lambda u=user: self.delete_user(u), fg_color="red", hover_color="dark red")
            delete_button.pack(side="right", padx=5)

            # Bouton Ouvrir
            edit_button = ctk.CTkButton(user_frame, text="Ouvrir", command=lambda u=user: self.edit_user(u))
            edit_button.pack(side="right", padx=5)

    def edit_user(self, user):
        self.edit_user_callback(user)

    def display_search_results(self, users):
        # Effacer la liste actuelle
        for widget in self.user_list.winfo_children():
            widget.destroy()

        # Afficher les résultats de la recherche
        for user in users:
            user_frame = ctk.CTkFrame(self.user_list)
            user_frame.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom}")
            name_label.pack(side="left", padx=5)

            edit_button = ctk.CTkButton(user_frame, text="Ouvrir", command=lambda u=user: self.edit_user(u))
            edit_button.pack(side="right", padx=5)

    def delete_user(self, user):
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer l'usager {user.nom} {user.prenom} ?"):
            try:
                User.delete(self.db_manager, user.id)
                messagebox.showinfo("Suppression", f"L'usager {user.nom} {user.prenom} a été supprimé.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer l'usager : {str(e)}")

    def add_workshop(self, user_id):
        from ui.add_workshop import AddWorkshopFrame  # Import local pour éviter les imports circulaires
        add_workshop_frame = AddWorkshopFrame(self.master, self.db_manager, user_id, self.update_user_list)
        add_workshop_frame.grid(row=0, column=0, sticky="nsew")
        add_workshop_frame.tkraise()

    def update_user_list(self):
        # Cette méthode est appelée après l'ajout d'un atelier pour rafraîchir la liste des utilisateurs
        self.load_users()

    def update_user_info(self, user_id):
        user = User.get_by_id(self.db_manager, user_id)
        if user:
            # Mettre à jour les informations de l'utilisateur
            user.nom = self.nom_entry.get()
            user.prenom = self.prenom_entry.get()
            user.date_naissance = self.date_naissance_entry.get()
            user.telephone = self.telephone_entry.get()
            user.email = self.email_entry.get()
            user.adresse = self.adresse_entry.get()
            
            # Mettre à jour la last_activity_date
            user.last_activity_date = datetime.now().strftime("%Y-%m-%d")
            
            user.save(self.db_manager)
            messagebox.showinfo("Mise à jour", "Les informations de l'utilisateur ont été mises à jour.")
            self.update_user_list()
        else:
            messagebox.showerror("Erreur", "Utilisateur non trouvé.")
