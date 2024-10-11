import customtkinter as ctk
from tkinter import messagebox
from models.user import User
from models.workshop import Workshop
from datetime import datetime, timedelta
import csv
from utils.date_utils import convert_from_db_date

class UserManagement(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Gestion des usagers", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Boutons d'action
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.export_button = ctk.CTkButton(self.action_frame, text="Exporter CSV", command=self.export_csv)
        self.export_button.pack(side="left", padx=5)
        
        self.rgpd_button = ctk.CTkButton(self.action_frame, text="Gestion RGPD", command=self.manage_rgpd)
        self.rgpd_button.pack(side="left", padx=5)

        # Liste des usagers
        self.user_list = ctk.CTkScrollableFrame(self)
        self.user_list.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.load_users()

    def display_search_results(self, users):
        self.clear_user_list()
        for user in users:
            self.add_user_to_list(user)

    def clear_user_list(self):
        for widget in self.user_list.winfo_children():
            widget.destroy()

    def add_user_to_list(self, user):
        user_frame = ctk.CTkFrame(self.user_list)
        user_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom}").pack(side="left", padx=5)
        ctk.CTkButton(user_frame, text="Modifier", command=lambda: self.edit_user(user)).pack(side="right", padx=5)
        ctk.CTkButton(user_frame, text="Supprimer", command=lambda: self.delete_user(user)).pack(side="right", padx=5)
        ctk.CTkButton(user_frame, text="Ateliers", command=lambda: self.show_user_workshops(user)).pack(side="right", padx=5)

    def load_users(self):
        self.clear_user_list()
        users = User.get_all(self.db_manager)
        for user in users:
            self.add_user_to_list(user)

    def edit_user(self, user):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Modifier {user.nom} {user.prenom}")
        edit_window.geometry("400x400")

        form_frame = ctk.CTkFrame(edit_window)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        nom_entry = self.create_form_field(form_frame, "Nom", 0, user.nom)
        prenom_entry = self.create_form_field(form_frame, "Prénom", 1, user.prenom)
        date_naissance_entry = self.create_form_field(form_frame, "Date de naissance", 2, user.date_naissance)
        telephone_entry = self.create_form_field(form_frame, "Téléphone", 3, user.telephone)
        email_entry = self.create_form_field(form_frame, "Email", 4, user.email)
        adresse_entry = self.create_form_field(form_frame, "Adresse", 5, user.adresse)

        save_button = ctk.CTkButton(form_frame, text="Enregistrer les modifications", 
                                    command=lambda: self.save_user_changes(user, nom_entry, prenom_entry, 
                                                                           date_naissance_entry, telephone_entry, 
                                                                           email_entry, adresse_entry))
        save_button.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def create_form_field(self, parent, label, row, default_value=None):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        if default_value is not None:
            entry.insert(0, str(default_value))
        return entry

    def save_user_changes(self, user, nom_entry, prenom_entry, date_naissance_entry, telephone_entry, email_entry, adresse_entry):
        user.nom = nom_entry.get()
        user.prenom = prenom_entry.get()
        date_naissance = date_naissance_entry.get()
        user.date_naissance = date_naissance if date_naissance else None
        user.telephone = telephone_entry.get()
        user.email = email_entry.get()
        user.adresse = adresse_entry.get()
        user.save(self.db_manager)
        messagebox.showinfo("Succès", "Modifications enregistrées avec succès.")
        self.load_users()

    def delete_user(self, user):
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer l'usager {user.nom} {user.prenom} ?"):
            user.delete(self.db_manager)
            self.load_users()

    def show_user_workshops(self, user):
        workshops_window = ctk.CTkToplevel(self)
        workshops_window.title(f"Ateliers de {user.nom} {user.prenom}")
        workshops_window.geometry("600x400")

        workshops_frame = ctk.CTkScrollableFrame(workshops_window)
        workshops_frame.pack(padx=20, pady=20, fill="both", expand=True)

        workshops = Workshop.get_by_user(self.db_manager, user.id)
        for workshop in workshops:
            workshop_frame = ctk.CTkFrame(workshops_frame)
            workshop_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(workshop_frame, text=f"{workshop.date} - {workshop.description}").pack(side="left", padx=5)
            ctk.CTkLabel(workshop_frame, text=f"{'Payant' if workshop.payant else 'Gratuit'}").pack(side="right", padx=5)
            ctk.CTkLabel(workshop_frame, text=workshop.categorie).pack(side="right", padx=5)

        add_button = ctk.CTkButton(workshops_window, text="Ajouter un atelier", command=lambda: self.add_workshop(user))
        add_button.pack(pady=10)

    def add_workshop(self, user):
        add_window = ctk.CTkToplevel(self)
        add_window.title(f"Ajouter un atelier pour {user.nom} {user.prenom}")
        add_window.geometry("400x300")

        form_frame = ctk.CTkFrame(add_window)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        description_entry = self.create_form_field(form_frame, "Description", 0)
        categorie_var = ctk.StringVar(value="Atelier")
        categorie_menu = ctk.CTkOptionMenu(form_frame, values=["Atelier", "Démarche administrative"], variable=categorie_var)
        categorie_menu.grid(row=1, column=1, padx=20, pady=(10, 0), sticky="ew")
        ctk.CTkLabel(form_frame, text="Catégorie").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        payant_var = ctk.StringVar(value="Non")
        payant_switch = ctk.CTkSwitch(form_frame, text="Payant", variable=payant_var, onvalue="Oui", offvalue="Non")
        payant_switch.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")

        save_button = ctk.CTkButton(form_frame, text="Enregistrer l'atelier", 
                                    command=lambda: self.save_workshop(user, description_entry.get(), 
                                                                       categorie_var.get(), payant_var.get() == "Oui"))
        save_button.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def save_workshop(self, user, description, categorie, payant):
        workshop = Workshop(user_id=user.id, description=description, categorie=categorie, payant=payant, date=datetime.now())
        workshop.save(self.db_manager)
        messagebox.showinfo("Succès", "Atelier ajouté avec succès.")
        self.show_user_workshops(user)

    def export_csv(self):
        users = User.get_all(self.db_manager)
        filename = f"export_usagers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Nom", "Prénom", "Date de naissance", "Téléphone", "Email", "Adresse", "Date de création"])
            for user in users:
                writer.writerow([user.id, user.nom, user.prenom, user.date_naissance, user.telephone, user.email, user.adresse, user.date_creation])
        messagebox.showinfo("Export réussi", f"Les données ont été exportées dans le fichier {filename}")

    def manage_rgpd(self):
        inactive_users = User.get_inactive_users(self.db_manager, timedelta(days=365))
        if not inactive_users:
            messagebox.showinfo("Information", "Aucun usager inactif depuis plus d'un an.")
            return

        rgpd_window = ctk.CTkToplevel(self)
        rgpd_window.title("Gestion RGPD")
        rgpd_window.geometry("600x400")

        rgpd_frame = ctk.CTkScrollableFrame(rgpd_window)
        rgpd_frame.pack(padx=20, pady=20, fill="both", expand=True)

        for user in inactive_users:
            user_frame = ctk.CTkFrame(rgpd_frame)
            user_frame.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom} - Inactif depuis le {user.last_activity_date}").pack(side="left", padx=5)
            ctk.CTkButton(user_frame, text="Supprimer", command=lambda u=user: self.delete_inactive_user(u)).pack(side="right", padx=5)

        delete_all_button = ctk.CTkButton(rgpd_window, text="Supprimer tous les usagers inactifs", command=self.delete_all_inactive_users)
        delete_all_button.pack(pady=10)

    def delete_inactive_user(self, user):
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer définitivement l'usager {user.nom} {user.prenom} ?"):
            user.delete(self.db_manager)
            messagebox.showinfo("Suppression", f"L'usager {user.nom} {user.prenom} a été supprimé.")
            self.manage_rgpd()

    def delete_all_inactive_users(self):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer tous les usagers inactifs depuis plus d'un an ?"):
            User.delete_inactive_users(self.db_manager, timedelta(days=365))
            messagebox.showinfo("Suppression", "Tous les usagers inactifs ont été supprimés.")
            self.manage_rgpd()