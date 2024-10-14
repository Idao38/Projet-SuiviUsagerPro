import os
import customtkinter as ctk
from tkinter import messagebox
from utils.config_utils import (
    get_conseillers,
    get_current_conseiller,
    set_current_conseiller,
    add_conseiller,
    get_dark_mode,
    set_dark_mode
)
from database.db_manager import DatabaseManager
from .dashboard import Dashboard
from .add_user import AddUser
from .user_management import UserManagement
from .workshop_history import WorkshopHistory
from .settings import Settings
from .data_management import DataManagement
from .user_edit import UserEditFrame
from theme import set_dark_theme, set_light_theme
from .add_workshop import AddWorkshop

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.current_frame = None  # Ajoutez cette ligne

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
        self.add_user = AddUser(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)
        self.user_management = UserManagement(self.main_content, db_manager=self.db_manager, edit_user_callback=self.edit_user)
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
        try:
            users = self.db_manager.search_users(search_term)
            if hasattr(self, 'user_management') and isinstance(self.user_management, UserManagement):
                self.user_management.display_search_results(users)
            else:
                print("Le widget user_management n'existe pas ou n'est pas du bon type.")
                # Recréez le widget user_management si nécessaire
                self.show_user_management()
                if hasattr(self, 'user_management'):
                    self.user_management.display_search_results(users)
        except Exception as e:
            print(f"Erreur lors de la recherche d'utilisateurs : {e}")

    def show_dashboard(self):
        self.clear_main_content()
        self.dashboard = Dashboard(self.main_content, self.db_manager)
        self.dashboard.pack(fill="both", expand=True)
        self.current_frame = self.dashboard  # Ajoutez cette ligne

    def show_user_management(self):
        self.clear_main_content()
        self.user_management = UserManagement(self.main_content, db_manager=self.db_manager, edit_user_callback=self.edit_user)
        self.user_management.pack(fill="both", expand=True)
        self.current_frame = self.user_management  # Ajoutez cette ligne

    def show_workshop_history(self):
        self.clear_main_content()
        self.workshop_history = WorkshopHistory(self.main_content, db_manager=self.db_manager)
        self.workshop_history.pack(fill="both", expand=True)
        self.current_frame = self.workshop_history  # Ajoutez cette ligne

    def show_data_management(self):
        self.clear_main_content()
        self.data_management = DataManagement(self.main_content, db_manager=self.db_manager)
        self.data_management.pack(fill="both", expand=True)
        self.current_frame = self.data_management  # Ajoutez cette ligne

    def show_settings(self):
        self.clear_main_content()
        self.settings = Settings(self.main_content, db_manager=self.db_manager, main_window=self)
        self.settings.pack(fill="both", expand=True)
        self.current_frame = self.settings  # Ajoutez cette ligne

    def show_add_user(self):
        self.clear_main_content()
        self.add_user = AddUser(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)
        self.add_user.pack(fill="both", expand=True)
        self.current_frame = self.add_user  # Ajoutez cette ligne

    def edit_user(self, user):
        self.clear_main_content()
        self.user_edit = UserEditFrame(
            self.main_content,
            self.db_manager,
            user,
            show_user_management_callback=self.show_user_management,
            show_add_workshop_callback=self.show_add_workshop,
            update_callback=self.update_all_sections
        )
        self.user_edit.pack(fill="both", expand=True)
        self.current_frame = self.user_edit  # Ajoutez cette ligne

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def hide_all_frames(self):
        for frame in (self.dashboard, self.add_user, self.user_management, self.workshop_history, self.settings, self.data_management, getattr(self, 'user_edit', None)):
            if frame:
                frame.grid_forget()

    def on_closing(self):
        self.db_manager.close()
        self.master.destroy()

    def update_all_sections(self):
        try:
            if hasattr(self, 'dashboard') and self.dashboard.winfo_exists():
                self.dashboard.update()
            if hasattr(self, 'user_management') and self.user_management.winfo_exists():
                self.user_management.load_users()
            if hasattr(self, 'workshop_history') and self.workshop_history.winfo_exists():
                self.workshop_history.load_history()
        except Exception as e:
            print(f"Erreur lors de la mise à jour des sections : {e}")
            # Vous pouvez également afficher un message d'erreur à l'utilisateur ici

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

    def show_add_workshop(self, user):
        self.clear_main_content()
        self.add_workshop = AddWorkshop(
            self.main_content,
            self.db_manager,
            user,
            show_user_edit_callback=lambda: self.show_user_edit(user),
            update_callback=self.update_all_sections
        )
        self.add_workshop.pack(fill="both", expand=True)
        self.current_frame = self.add_workshop

    def update_and_show_user_edit(self, user):
        self.update_all_sections()
        self.show_user_edit(user)

    def show_user_edit(self, user):
        self.clear_main_content()
        self.user_edit = UserEditFrame(
            self.main_content,
            self.db_manager,
            user,
            show_user_management_callback=self.show_user_management,
            show_add_workshop_callback=self.show_add_workshop,
            update_callback=self.update_all_sections
        )
        self.user_edit.pack(fill="both", expand=True)
        self.current_frame = self.user_edit  # Ajoutez cette ligne

    def show_add_workshop(self, user):
        self.clear_main_content()
        self.add_workshop = AddWorkshop(self.main_content, self.db_manager, user, lambda: self.show_user_edit(user), self.update_all_sections)
        self.add_workshop.pack(fill="both", expand=True)
