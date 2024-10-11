import customtkinter as ctk
from tkinter import messagebox, filedialog
from database.db_manager import DatabaseManager
import csv
from utils.date_utils import convert_from_db_date
from config import get_current_conseiller, set_current_conseiller, get_conseillers, add_conseiller, remove_conseiller, get_dark_mode, set_dark_mode
from theme import set_dark_theme, set_light_theme

class Settings(ctk.CTkFrame):
    def __init__(self, master, db_manager, main_window, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.main_window = main_window  # Assurez-vous que cette ligne est présente

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Paramètres", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Contenu des paramètres
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Exportation CSV
        self.export_label = ctk.CTkLabel(self.settings_frame, text="Exportation CSV", font=ctk.CTkFont(size=18, weight="bold"))
        self.export_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.export_button = ctk.CTkButton(self.settings_frame, text="Exporter les données", command=self.export_data)
        self.export_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Autres paramètres
        self.other_settings_label = ctk.CTkLabel(self.settings_frame, text="Autres paramètres", font=ctk.CTkFont(size=18, weight="bold"))
        self.other_settings_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")

        # Mode sombre
        is_dark = get_dark_mode()
        self.dark_mode_var = ctk.StringVar(value="on" if is_dark else "off")
        self.dark_mode_switch = ctk.CTkSwitch(self.settings_frame, text="Activer le mode sombre", 
                                              variable=self.dark_mode_var, command=self.toggle_dark_mode,
                                              onvalue="on", offvalue="off")
        self.dark_mode_switch.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.dark_mode_switch.select() if is_dark else self.dark_mode_switch.deselect()

        # Gestion des conseillers
        self.conseillers_label = ctk.CTkLabel(self.settings_frame, text="Gestion des conseillers", font=ctk.CTkFont(size=18, weight="bold"))
        self.conseillers_label.grid(row=4, column=0, padx=20, pady=(20, 10), sticky="w")

        self.add_conseiller_button = ctk.CTkButton(self.settings_frame, text="Ajouter un conseiller", command=self.add_conseiller)
        self.add_conseiller_button.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.remove_conseiller_button = ctk.CTkButton(self.settings_frame, text="Supprimer un conseiller", command=self.remove_conseiller)
        self.remove_conseiller_button.grid(row=6, column=0, padx=20, pady=10, sticky="w")
    def toggle_dark_mode(self):
        is_dark = self.dark_mode_var.get() == "on"
        set_dark_mode(is_dark)
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()
        self.main_window.update_appearance()
        self.update()

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        users_query = "SELECT * FROM users"
        workshops_query = "SELECT * FROM workshops"

        users_data = self.db_manager.fetch_all(users_query)
        workshops_data = self.db_manager.fetch_all(workshops_query)

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            csv_writer.writerow(["Users"])
            csv_writer.writerow(["id", "nom", "prenom", "date_naissance", "telephone", "email", "adresse", "date_creation"])
            for user in users_data:
                user = list(user)
                user[3] = convert_from_db_date(user[3])  # date_naissance
                user[7] = convert_from_db_date(user[7])  # date_creation
                csv_writer.writerow(user)
            
            csv_writer.writerow([])
            csv_writer.writerow(["Workshops"])
            csv_writer.writerow(["id", "user_id", "description", "categorie", "payant", "date", "conseiller"])
            for workshop in workshops_data:
                workshop = list(workshop)
                workshop[5] = convert_from_db_date(workshop[5])  # date
                csv_writer.writerow(workshop)

        messagebox.showinfo("Succès", "Les données ont été exportées avec succès.")

    def add_conseiller(self):
        new_name = ctk.CTkInputDialog(text="Entrez le nom du nouveau conseiller :", title="Ajouter un conseiller").get_input()
        if new_name:
            add_conseiller(new_name)
            self.main_window.update_conseiller_dropdown()
            messagebox.showinfo("Succès", f"Le conseiller {new_name} a été ajouté.")
        else:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide. Aucun conseiller n'a été ajouté.")

    def remove_conseiller(self):
        conseillers = get_conseillers()
        if not conseillers:
            messagebox.showerror("Erreur", "Il n'y a aucun conseiller à supprimer.")
            return
        
        to_remove = ctk.CTkInputDialog(text="Entrez le nom du conseiller à supprimer :", title="Supprimer un conseiller").get_input()
        if to_remove in conseillers:
            remove_conseiller(to_remove)
            self.main_window.update_conseiller_dropdown()
            messagebox.showinfo("Succès", f"Le conseiller {to_remove} a été supprimé.")
        else:
            messagebox.showerror("Erreur", f"Le conseiller {to_remove} n'existe pas.")
