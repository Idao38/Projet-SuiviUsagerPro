import customtkinter as ctk
from tkinter import messagebox
from models.workshop import Workshop
from utils.date_utils import is_valid_date, convert_to_db_date, get_current_date
from config import get_current_conseiller
from models.user import User
import logging

WORKSHOP_TYPES = ["Atelier numérique", "Démarche administrative"]

class AddWorkshop(ctk.CTkFrame):
    def __init__(self, master, db_manager, user, show_user_edit_callback, update_callback):
        logging.debug(f"Initialisation de AddWorkshop avec user: {user}")
        super().__init__(master)
        self.db_manager = db_manager
        self.user = user
        self.show_user_edit_callback = show_user_edit_callback
        self.update_callback = update_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text=f"Ajouter un atelier pour {user.nom} {user.prenom}", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Formulaire d'ajout d'atelier
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)
        self.form_frame.grid_rowconfigure(4, weight=1)

        current_date = get_current_date()
        current_conseiller = get_current_conseiller()

        self.date_entry = self.create_form_field(self.form_frame, "Date *", 0, current_date)
        self.create_workshop_type_dropdown(self.form_frame, "Type d'atelier *", 1)
        self.conseiller_entry = self.create_form_field(self.form_frame, "Conseiller *", 2, current_conseiller)
        
        self.payant_var = ctk.StringVar(value="Non")
        self.payant_checkbox = ctk.CTkCheckBox(self.form_frame, text="Atelier payant", variable=self.payant_var, onvalue="Oui", offvalue="Non")
        self.payant_checkbox.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")

        ctk.CTkLabel(self.form_frame, text="Description").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="nw")
        self.description_entry = ctk.CTkTextbox(self.form_frame, height=100)
        self.description_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="nsew")

        self.submit_button = ctk.CTkButton(self.form_frame, text="Ajouter l'atelier", command=self.add_workshop)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def create_form_field(self, parent, label, row, default_value=""):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        entry.insert(0, default_value)
        return entry

    def create_workshop_type_dropdown(self, parent, label, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        self.workshop_type_var = ctk.StringVar(value=WORKSHOP_TYPES[0])
        dropdown = ctk.CTkOptionMenu(parent, variable=self.workshop_type_var, values=WORKSHOP_TYPES)
        dropdown.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")

    def add_workshop(self):
        logging.debug("Début de la méthode add_workshop")
        date = convert_to_db_date(self.date_entry.get())
        categorie = self.workshop_type_var.get()
        conseiller = self.conseiller_entry.get()
        payant = self.payant_var.get() == "Oui"
        description = self.description_entry.get("1.0", "end-1c")

        if not date or not categorie or not conseiller:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        new_workshop = Workshop(user_id=self.user.id, date=date, categorie=categorie,
                                conseiller=conseiller, payant=payant, description=description)
        try:
            new_workshop.save(self.db_manager)
            logging.debug("Atelier sauvegardé avec succès")
            messagebox.showinfo("Succès", "L'atelier a été ajouté avec succès.")
            logging.debug("Message de succès affiché")
            
            logging.debug("Appel de update_callback")
            self.update_callback()
            logging.debug("update_callback terminé")
            
            logging.debug("Appel de show_user_edit_callback")
            self.show_user_edit_callback()
            logging.debug("show_user_edit_callback terminé")
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'atelier : {e}")
            messagebox.showerror("Erreur", f"Impossible d'ajouter l'atelier : {str(e)}")
        
        logging.debug("Fin de la méthode add_workshop")
