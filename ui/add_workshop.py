import customtkinter as ctk
from tkinter import messagebox
from models.workshop import Workshop
from utils.date_utils import is_valid_date, convert_to_db_date, get_current_date
from config import get_current_conseiller
from models.user import User
import logging
from utils.config_utils import get_default_paid_workshops

def get_workshop_types():
    return ["Atelier numérique", "Démarche administrative"]

class AddWorkshop(ctk.CTkFrame):
    def __init__(self, master, db_manager, user, show_user_edit_callback, update_callback):
        logging.debug(f"Initialisation de AddWorkshop avec user: {user}")
        super().__init__(master)
        self.db_manager = db_manager
        self.user = user
        self.show_user_edit_callback = show_user_edit_callback
        self.update_callback = update_callback
        self.default_paid_workshops = get_default_paid_workshops()

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
        
        self.paid_var = ctk.BooleanVar(value=False)
        
        # Créer un nouveau frame pour le paiement
        self.payment_frame = ctk.CTkFrame(self.form_frame)
        self.payment_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
        self.payment_frame.grid_columnconfigure(1, weight=1)  # Cette ligne permet l'expansion de l'espace central

        # Ajouter le statut de paiement
        self.payment_status_label = ctk.CTkLabel(self.payment_frame, text="Statut de paiement : ")
        self.payment_status_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
        self.payment_status_value = ctk.CTkLabel(self.payment_frame, text="")
        self.payment_status_value.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="w")

        # Ajouter la case à cocher pour le paiement
        self.paid_checkbox = ctk.CTkCheckBox(self.payment_frame, text="Payé", variable=self.paid_var, command=self.update_payment_status)
        self.paid_checkbox.grid(row=0, column=2, padx=(10, 0), pady=0, sticky="e")

        ctk.CTkLabel(self.form_frame, text="Description").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="nw")
        self.description_entry = ctk.CTkTextbox(self.form_frame, height=100)
        self.description_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="nsew")

        self.submit_button = ctk.CTkButton(self.form_frame, text="Ajouter l'atelier", command=self.add_workshop)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.user.calculate_workshop_payment_status(self.db_manager)  # Calculer le statut
        self.update_payment_status()

    def create_form_field(self, parent, label, row, default_value=""):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        entry.insert(0, default_value)
        return entry

    def create_workshop_type_dropdown(self, parent, label, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        self.workshop_type_var = ctk.StringVar(value=get_workshop_types()[0])
        workshop_type_dropdown = ctk.CTkOptionMenu(parent, variable=self.workshop_type_var, values=get_workshop_types())
        workshop_type_dropdown.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")

    def add_workshop(self):
        logging.debug("Début de la méthode add_workshop")
        date = convert_to_db_date(self.date_entry.get())
        categorie = self.workshop_type_var.get()
        conseiller = self.conseiller_entry.get()
        is_paid_type = categorie in self.default_paid_workshops
        paid = self.paid_var.get()
        description = self.description_entry.get("1.0", "end-1c")

        if not date or not categorie or not conseiller:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        new_workshop = Workshop(user_id=self.user.id, date=date, categorie=categorie,
                                conseiller=conseiller, payant=is_paid_type, paid=paid, description=description)
        try:
            new_workshop.save(self.db_manager)
            if paid:
                self.user.update_last_payment_date(self.db_manager)
            self.user.calculate_workshop_payment_status(self.db_manager)  # Ajoutez cette ligne
            self.user.notify_observers('user_updated', self.user)  # Ajoutez cette ligne
            logging.debug("Atelier sauvegardé avec succès")
            messagebox.showinfo("Succès", "L'atelier a été ajouté avec succès.")
            logging.debug("Message de succès affiché")
            
         
            self.update_callback()
            self.show_user_edit_callback()
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'atelier : {e}")
            messagebox.showerror("Erreur", f"Impossible d'ajouter l'atelier : {str(e)}")
        
        logging.debug("Fin de la méthode add_workshop")

    def update_payment_status(self):
        status = self.user.get_workshop_payment_status(self.db_manager)
        self.payment_status_value.configure(text=status)

# Déplacez cette ligne à la fin du fichier
WORKSHOP_TYPES = ["Atelier numérique", "Démarche administrative"]
