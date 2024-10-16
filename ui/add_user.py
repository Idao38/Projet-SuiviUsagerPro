import customtkinter as ctk
from tkinter import messagebox
from models.user import User
from utils.date_utils import convert_to_db_date, is_valid_date

class AddUser(ctk.CTkFrame):
    def __init__(self, master, db_manager, update_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.update_callback = update_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text="Ajouter un usager", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Formulaire d'ajout d'usager
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)

        self.nom_entry = self.create_form_field(self.form_frame, "Nom *", 0)
        self.prenom_entry = self.create_form_field(self.form_frame, "Prénom *", 1)
        self.telephone_entry = self.create_form_field(self.form_frame, "Numéro de téléphone *", 2)
        self.date_naissance_entry = self.create_form_field(self.form_frame, "Date de naissance", 3)
        self.email_entry = self.create_form_field(self.form_frame, "Mail", 4)
        self.adresse_entry = self.create_form_field(self.form_frame, "Adresse postale", 5)

        self.submit_button = ctk.CTkButton(self.form_frame, text="Valider la création du nouvel utilisateur", command=self.add_user)
        self.submit_button.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Note pour les champs obligatoires
        self.obligatory_note = ctk.CTkLabel(self.form_frame, text="* obligatoire", font=ctk.CTkFont(size=12, slant="italic"))
        self.obligatory_note.grid(row=7, column=1, padx=20, pady=(0, 10), sticky="e")

    def create_form_field(self, parent, label, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        return entry

    def add_user(self):
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        date_naissance = convert_to_db_date(self.date_naissance_entry.get())
        telephone = self.telephone_entry.get()
        email = self.email_entry.get()
        adresse = self.adresse_entry.get()

        if not nom or not prenom or not telephone:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        new_user = User(nom=nom, prenom=prenom, telephone=telephone, date_naissance=date_naissance, email=email, adresse=adresse)
        new_user.save(self.db_manager)
        
        # Utilisez la méthode create_user de MainWindow
        self.master.master.create_user(new_user.get_state())

        messagebox.showinfo("Succès", "L'usager a été ajouté avec succès.")
        self.clear_form()
        self.update_callback()

    def clear_fields(self):
        self.nom_entry.delete(0, 'end')
        self.prenom_entry.delete(0, 'end')
        self.date_naissance_entry.delete(0, 'end')
        self.telephone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.adresse_entry.delete(0, 'end')

    def clear_form(self):
        for entry in [self.nom_entry, self.prenom_entry, self.telephone_entry, 
                      self.date_naissance_entry, self.email_entry, self.adresse_entry]:
            entry.delete(0, 'end')
