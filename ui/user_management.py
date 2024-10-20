import customtkinter as ctk
from tkinter import messagebox
from models.user import User
from models.workshop import Workshop
from datetime import datetime, timedelta
import csv
from utils.date_utils import convert_from_db_date
from utils.observer import Observer

class UserManagement(ctk.CTkFrame, Observer):
    def __init__(self, master, db_manager, edit_user_callback, edit_workshop_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.edit_user_callback = edit_user_callback
        self.edit_workshop_callback = edit_workshop_callback
        self.users = []
        self.offset = 0
        self.limit = 25

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Gestion des usagers", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Liste des usagers
        self.user_list = ctk.CTkScrollableFrame(self)
        self.user_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Bouton pour charger plus d'utilisateurs
        self.load_more_button = ctk.CTkButton(self, text="Charger plus", command=self.load_more_users)
        self.load_more_button.grid(row=2, column=0, pady=(0, 20), sticky="ew")

        # Ajoutez cette ligne pour créer l'attribut search_entry
        self.search_entry = ctk.CTkEntry(self)

        # Chargement initial des usagers
        self.load_users()

    def load_users(self):
        new_users = User.get_paginated(self.db_manager, self.offset, self.limit)
        self.users.extend(new_users)
        self.display_users(new_users)
        self.offset += self.limit

        # Masquer le bouton si tous les utilisateurs sont chargés
        if len(new_users) < self.limit:
            self.load_more_button.grid_remove()

    def load_more_users(self):
        self.load_users()

    def display_users(self, users):
        for user in users:
            user_frame = ctk.CTkFrame(self.user_list)
            user_frame.pack(fill="x", padx=5, pady=5)

            name_label = ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom} - Dernière activité: {user.last_activity_date or 'N/A'}")
            name_label.pack(side="left", padx=5)

            # Bouton de suppression
            delete_button = ctk.CTkButton(user_frame, text="Supprimer", command=lambda u=user: self.delete_user(u), fg_color="red", hover_color="dark red")
            delete_button.pack(side="right", padx=5)

            # Bouton Ouvrir
            edit_button = ctk.CTkButton(user_frame, text="Ouvrir", command=lambda u=user: self.edit_user(u))
            edit_button.pack(side="right", padx=5)

    def on_frame_configure(self, event):
        self.user_list.configure(scrollregion=self.user_list.bbox("all"))

    def on_mousewheel(self, event):
        if self.user_list.winfo_height() < self.user_list.bbox("all")[3]:
            if self.user_list.yview()[1] >= 0.9:
                self.load_users()

    def edit_user(self, user):
        self.edit_user_callback(user)

    def display_search_results(self, users):
        # Vérifier si le widget user_list existe toujours
        if not hasattr(self, 'user_list') or not self.user_list.winfo_exists():
            # Recréer le widget user_list s'il n'existe plus
            self.user_list = ctk.CTkScrollableFrame(self)
            self.user_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

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

    def update(self, observable, *args, **kwargs):
        if isinstance(observable, User):
            self.refresh_user_list()
        elif isinstance(observable, Workshop):
            self.refresh_workshop_list()

    def refresh_user_list(self):
        # Effacer la liste actuelle
        for item in self.user_list.get_children():
            self.user_list.delete(item)
        
        # Recharger les utilisateurs depuis la base de données
        users = User.get_all(self.db_manager)
        
        # Remplir la liste avec les utilisateurs mis à jour
        for user in users:
            self.user_list.insert("", "end", values=(user.id, user.nom, user.prenom, user.telephone, user.email))

    def refresh_workshop_list(self):
        # Effacer la liste actuelle des ateliers (si elle existe)
        if hasattr(self, 'workshop_list'):
            for item in self.workshop_list.get_children():
                self.workshop_list.delete(item)
        
        # Recharger les ateliers depuis la base de données
        workshops = Workshop.get_all(self.db_manager)
        
        # Remplir la liste avec les ateliers mis à jour
        for workshop in workshops:
            user = User.get_by_id(self.db_manager, workshop.user_id)
            self.workshop_list.insert("", "end", values=(workshop.id, user.nom, user.prenom, workshop.date, workshop.categorie, workshop.conseiller))
