import customtkinter as ctk
from tkinter import messagebox
from utils.rgpd_manager import RGPDManager
from utils.csv_export import CSVExporter
from models.user import User
from datetime import timedelta

class DataManagement(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Gestion des données", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Contenu
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Section RGPD
        self.rgpd_frame = self.create_section(self.content_frame, "Gestion RGPD", 0)
        self.rgpd_button = ctk.CTkButton(self.rgpd_frame, text="Gérer les données RGPD", command=self.manage_rgpd)
        self.rgpd_button.pack(pady=10)

        # Section Exportation CSV
        self.export_frame = self.create_section(self.content_frame, "Exportation CSV", 1)
        
        # Menu déroulant pour choisir le type d'export
        self.export_options = ["Utilisateurs", "Ateliers", "Toutes les données"]
        self.export_var = ctk.StringVar(value=self.export_options[0])
        self.export_menu = ctk.CTkOptionMenu(self.export_frame, variable=self.export_var, values=self.export_options)
        self.export_menu.pack(pady=(0, 10))

        # Bouton pour valider l'export
        self.export_button = ctk.CTkButton(self.export_frame, text="Exporter les données", command=self.export_csv)
        self.export_button.pack(pady=10)

    def create_section(self, parent, title, row):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        return frame

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

    def export_csv(self):
        exporter = CSVExporter(self.db_manager)
        export_type = self.export_var.get()

        if export_type == "Utilisateurs":
            success, message = exporter.export_users()
        elif export_type == "Ateliers":
            success, message = exporter.export_workshops()
        elif export_type == "Toutes les données":
            success, message = exporter.export_all_data()
        else:
            messagebox.showerror("Erreur", "Type d'exportation non reconnu.")
            return

        if success:
            messagebox.showinfo("Exportation réussie", message)
        else:
            messagebox.showerror("Erreur d'exportation", message)
