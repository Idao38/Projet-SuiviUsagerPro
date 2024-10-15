import customtkinter as ctk
from tkinter import messagebox
from models.workshop import Workshop
from utils.date_utils import convert_to_db_date, convert_from_db_date

class EditWorkshop(ctk.CTkFrame):
    def __init__(self, master, db_manager, workshop, update_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.workshop = workshop
        self.update_callback = update_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text=f"Éditer l'atelier", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Formulaire d'édition
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)

        self.date_entry = self.create_form_field(self.form_frame, "Date", 0, convert_from_db_date(workshop.date))
        self.categorie_entry = self.create_form_field(self.form_frame, "Catégorie", 1, workshop.categorie)
        self.conseiller_entry = self.create_form_field(self.form_frame, "Conseiller", 2, workshop.conseiller)
        self.payant_var = ctk.StringVar(value="Oui" if workshop.payant else "Non")
        self.payant_checkbox = ctk.CTkCheckBox(self.form_frame, text="Atelier payant", variable=self.payant_var, onvalue="Oui", offvalue="Non")
        self.payant_checkbox.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")

        self.description_label = ctk.CTkLabel(self.form_frame, text="Description")
        self.description_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.description_entry = ctk.CTkTextbox(self.form_frame, height=100)
        self.description_entry.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="nsew")
        self.description_entry.insert("1.0", workshop.description)

        self.submit_button = ctk.CTkButton(self.form_frame, text="Mettre à jour l'atelier", command=self.update_workshop)
        self.submit_button.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def create_form_field(self, parent, label, row, default_value=""):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        entry.insert(0, default_value)
        return entry

    def update_workshop(self):
        self.workshop.date = convert_to_db_date(self.date_entry.get())
        self.workshop.categorie = self.categorie_entry.get()
        self.workshop.conseiller = self.conseiller_entry.get()
        self.workshop.payant = self.payant_var.get() == "Oui"
        self.workshop.description = self.description_entry.get("1.0", "end-1c")

        try:
            self.workshop.save(self.db_manager)
            messagebox.showinfo("Succès", "L'atelier a été mis à jour avec succès.")
            self.update_callback()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de mettre à jour l'atelier : {str(e)}")