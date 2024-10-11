import os
import customtkinter as ctk
from tkinter import messagebox
from config import get_conseillers, get_current_conseiller, set_current_conseiller, add_conseiller, get_dark_mode, set_dark_mode
from database.db_manager import DatabaseManager
from .dashboard import Dashboard
from .add_user import AddUser
from .user_management import UserManagement
from .workshop_history import WorkshopHistory
from .settings import Settings
from .data_management import DataManagement
from .user_edit import UserEditFrame
from theme import set_dark_theme, set_light_theme

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager

        # Initialiser le mode d'apparence
        self.set_initial_appearance()

        # Configuration du layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Barre latérale
        self.create_sidebar()

        # Barre supérieure
        self.create_top_bar()

        # Zone de contenu principal
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=1, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Initialiser les différentes sections
        self.dashboard = Dashboard(self.main_content, db_manager=self.db_manager)
        self.add_user = AddUser(self.main_content, db_manager=self.db_manager)
        self.user_management = UserManagement(self.main_content, db_manager=self.db_manager, main_window=self)
        self.workshop_history = WorkshopHistory(self.main_content, db_manager=self.db_manager)
        self.settings = Settings(self.main_content, db_manager=self.db_manager, main_window=self)
        self.data_management = DataManagement(self.main_content, db_manager=self.db_manager)

        # Afficher le tableau de bord par défaut
        self.show_dashboard()

    def set_initial_appearance(self):
        is_dark = get_dark_mode()
        if is_dark:
            ctk.set_appearance_mode("dark")
            set_dark_theme()
        else:
            ctk.set_appearance_mode("light")
            set_light_theme()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # Espace extensible avant le bouton Paramètres

        self.logo_label = ctk.CTkLabel(self.sidebar, text="SuiviUsagerPro", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar, text="Tableau de bord", command=self.show_dashboard)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar, text="Ajouter un usager", command=self.show_add_user)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar, text="Gestion des usagers", command=self.show_user_management)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_4 = ctk.CTkButton(self.sidebar, text="Historique des ateliers", command=self.show_workshop_history)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_5 = ctk.CTkButton(self.sidebar, text="Gestion des données", command=self.show_data_management)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)
        # Bouton Paramètres en bas de la barre latérale
        self.settings_button = ctk.CTkButton(self.sidebar, text="Paramètres", command=self.show_settings)
        self.settings_button.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="s")

    def create_top_bar(self):
        self.top_bar = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.top_bar.grid(row=0, column=1, sticky="ew")
        self.top_bar.grid_columnconfigure(0, weight=1)  # Le champ de recherche prendra plus de place

        # Champ de recherche à gauche (élargi)
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Rechercher")
        self.search_entry.grid(row=0, column=0, padx=(20, 10), pady=5, sticky="ew")
        self.search_entry.bind("<Return>", self.search_users)

        self.search_button = ctk.CTkButton(self.top_bar, text="Rechercher", command=self.search_users)
        self.search_button.grid(row=0, column=1, padx=(0, 20), pady=5)

        # Liste déroulante des conseillers
        self.conseillers = get_conseillers()
        self.current_conseiller = get_current_conseiller()
        if not self.conseillers:
            self.ask_new_conseiller()
        else:
            self.create_conseiller_dropdown()

    def create_conseiller_dropdown(self):
        self.conseiller_var = ctk.StringVar(value=self.current_conseiller)
        self.conseiller_dropdown = ctk.CTkOptionMenu(
            self.top_bar, 
            values=self.conseillers,
            variable=self.conseiller_var,
            command=self.on_conseiller_change
        )
        self.conseiller_dropdown.grid(row=0, column=2, padx=20, pady=5)

    def ask_new_conseiller(self):
        new_name = ctk.CTkInputDialog(text="Entrez le nom du nouveau conseiller :", title="Ajouter un conseiller").get_input()
        if new_name:
            add_conseiller(new_name)
            self.conseillers = get_conseillers()
            self.current_conseiller = new_name
            set_current_conseiller(new_name)
            self.create_conseiller_dropdown()
        else:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide. Veuillez réessayer.")
            self.after(100, self.ask_new_conseiller)

    def on_conseiller_change(self, choice):
        set_current_conseiller(choice)

    def update_conseiller_dropdown(self):
        self.conseillers = get_conseillers()
        self.current_conseiller = get_current_conseiller()
        if hasattr(self, 'conseiller_dropdown'):
            self.conseiller_dropdown.configure(values=self.conseillers)
            self.conseiller_var.set(self.current_conseiller)
        else:
            self.create_conseiller_dropdown()

    def search_users(self, event=None):
        search_term = self.search_entry.get()
        if search_term:
            users = self.db_manager.search_users(search_term)
            self.show_user_management()
            self.user_management.display_search_results(users)
        else:
            self.show_user_management()
            self.user_management.load_users()

    def show_dashboard(self):
        self.hide_all_frames()
        self.dashboard.grid(row=0, column=0, sticky="nsew")

    def show_user_management(self):
        self.hide_all_frames()
        self.user_management.grid(row=0, column=0, sticky="nsew")

    def show_workshop_history(self):
        self.hide_all_frames()
        self.workshop_history.grid(row=0, column=0, sticky="nsew")

    def show_data_management(self):
        self.hide_all_frames()
        self.data_management.grid(row=0, column=0, sticky="nsew")

    def show_settings(self):
        self.hide_all_frames()
        self.settings.grid(row=0, column=0, sticky="nsew")

    def show_add_user(self):
        self.hide_all_frames()
        self.add_user.grid(row=0, column=0, sticky="nsew")

    def edit_user(self, user):
        from .user_edit import UserEditFrame
        self.hide_all_frames()
        self.user_edit = UserEditFrame(self.main_content, self.db_manager, user, main_window=self)
        self.user_edit.grid(row=0, column=0, sticky="nsew")

    def hide_all_frames(self):
        for frame in (self.dashboard, self.add_user, self.user_management, self.workshop_history, self.settings, self.data_management, getattr(self, 'user_edit', None)):
            if frame:
                frame.grid_forget()

    def on_closing(self):
        self.db_manager.close()
        self.master.destroy()

    def update_all_sections(self):
        self.dashboard.update_stats()
        self.user_management.load_users()
        self.workshop_history.load_workshops()
        # Ajoutez ici d'autres mises à jour si nécessaire

    def update_appearance(self):
        is_dark = get_dark_mode()
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()
        
        # Mettre à jour tous les widgets
        self.update()
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkBaseClass):
                widget.configure(fg_color=widget.cget("fg_color"))
                widget.update()

        # Mettre à jour les sections spécifiques
        self.dashboard.update()
        self.add_user.update()
        self.user_management.update()
        self.workshop_history.update()
        self.settings.update()