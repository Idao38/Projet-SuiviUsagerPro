import customtkinter as ctk
from tkinter import messagebox
from models.user import User
from models.workshop import Workshop
from utils.date_utils import convert_to_db_date, convert_from_db_date, is_valid_date
from datetime import datetime
from utils.observer import Observer

class UserEditFrame(ctk.CTkFrame, Observer):
    def __init__(self, master, db_manager, user, show_user_management_callback, show_add_workshop_callback, edit_workshop_callback, update_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.user = user
        self.user.add_observer(self)  # Ajoutez cette ligne
        for workshop in Workshop.get_by_user(self.db_manager, self.user.id):
            workshop.add_observer(self)
        self.show_user_management_callback = show_user_management_callback
        self.show_add_workshop_callback = show_add_workshop_callback
        self.edit_workshop_callback = edit_workshop_callback
        self.update_callback = update_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Titre
        self.title = ctk.CTkLabel(self, text=f"Éditer le profil de {user.nom if user else ''} {user.prenom if user else ''}", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Formulaire d'édition
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)

        self.nom_entry = self.create_form_field(self.form_frame, "Nom *", 0, user.nom)
        self.prenom_entry = self.create_form_field(self.form_frame, "Prénom *", 1, user.prenom)
        self.telephone_entry = self.create_form_field(self.form_frame, "Numéro de téléphone *", 2, user.telephone)
        self.date_naissance_entry = self.create_form_field(self.form_frame, "Date de naissance", 3, convert_from_db_date(user.date_naissance) if user.date_naissance else "")
        self.email_entry = self.create_form_field(self.form_frame, "Mail", 4, user.email)
        self.adresse_entry = self.create_form_field(self.form_frame, "Adresse postale", 5, user.adresse)

        # Créez un nouveau Frame pour les boutons et le statut de paiement
        self.bottom_frame = ctk.CTkFrame(self.form_frame)
        self.bottom_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.bottom_frame.grid_columnconfigure(3, weight=1)  # Ajoutez cette ligne pour pousser le statut de paiement à droite

        # Bouton Ajouter un atelier
        self.add_workshop_button = ctk.CTkButton(self.bottom_frame, text="Ajouter un atelier", command=self.open_add_workshop)
        self.add_workshop_button.grid(row=0, column=0, padx=5)
        
        # Bouton Sauvegarder
        self.save_button = ctk.CTkButton(self.bottom_frame, text="Sauvegarder les modifications", command=self.save_user)
        self.save_button.grid(row=0, column=1, padx=5)

        # Bouton Retour
        self.back_button = ctk.CTkButton(self.bottom_frame, text="Retour à la liste des utilisateurs", command=self.back_to_list)
        self.back_button.grid(row=0, column=2, padx=5)

        # Statut de paiement (déplacé à droite)
        self.payment_status_label = ctk.CTkLabel(self.bottom_frame, text="Statut de paiement : ")
        self.payment_status_label.grid(row=0, column=3, padx=(20, 5), sticky="e")
        self.payment_status_value = ctk.CTkLabel(self.bottom_frame, text="")
        self.payment_status_value.grid(row=0, column=4, padx=(0, 20), sticky="w")

        # Ajout de l'historique des ateliers
        self.history_frame = ctk.CTkScrollableFrame(self.form_frame)
        self.history_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nsew")
        self.history_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Ajoutez ces lignes pour définir les couleurs alternées
        self.colors = {"even": "#E6E6E6", "odd": "#FFFFFF"}  # Gris clair et blanc

        headers = ["Date", "Type d'atelier", "Conseiller", "Payé"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.history_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        self.load_user_workshops()

        self.update_payment_status()

    def create_form_field(self, parent, label, row, value):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        entry.insert(0, value if value else "")
        return entry

    def save_changes(self):
        self.user.nom = self.nom_entry.get()
        self.user.prenom = self.prenom_entry.get()
        self.user.date_naissance = convert_to_db_date(self.date_naissance_entry.get())
        self.user.telephone = self.telephone_entry.get()
        self.user.email = self.email_entry.get()
        self.user.adresse = self.adresse_entry.get()

        try:
            self.user.save(self.db_manager)
            messagebox.showinfo("Succès", "Les modifications ont été enregistrées.")
            self.update_callback()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder les modifications : {str(e)}")

    def save_user(self):
        # Récupérer les nouvelles valeurs
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        telephone = self.telephone_entry.get()
        date_naissance = self.date_naissance_entry.get()
        email = self.email_entry.get()
        adresse = self.adresse_entry.get()

        # Vérifier les champs obligatoires
        if not all([nom, prenom, telephone]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        # Vérifier le format de la date
        if date_naissance and not is_valid_date(date_naissance):
            messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA.")
            return

        # Convertir la date pour la base de données
        date_naissance = convert_to_db_date(date_naissance) if date_naissance else None

        # Mettre à jour l'utilisateur
        self.user.nom = nom
        self.user.prenom = prenom
        self.user.telephone = telephone
        self.user.date_naissance = date_naissance
        self.user.email = email
        self.user.adresse = adresse
        self.user.last_activity_date = datetime.now().strftime("%Y-%m-%d")

        # Sauvegarder les modifications
        self.user.save(self.db_manager)
        self.user.notify_observers('user_updated', self.user)  # Ajoutez cette ligne

        # Vérifiez le statut de paiement
        is_up_to_date = self.user.is_workshop_payment_up_to_date(self.db_manager)
        payment_status = "À jour" if is_up_to_date else "En retard"
        
        # Mettez à jour l'interface utilisateur avec le nouveau statut
        # (Assurez-vous d'avoir un widget pour afficher ce statut)
        self.payment_status_label.configure(text=f"Statut de paiement : {payment_status}")

        messagebox.showinfo("Succès", "Les modifications ont été sauvegardées avec succès.")
        self.update_callback()
        self.back_to_list()

    def back_to_list(self):
        self.show_user_management_callback()

    def open_add_workshop(self):
        self.show_add_workshop_callback(self.user)

    def load_user_workshops(self):
        workshops = Workshop.get_by_user(self.db_manager, self.user.id)
        headers = ["Date", "Type d'atelier", "Conseiller", "Payé"]
        
        # Créer une ligne d'en-tête
        header_frame = ctk.CTkFrame(self.history_frame)
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, header in enumerate(headers):
            ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="ew")

        for i, workshop in enumerate(workshops, start=1):
            row_frame = ctk.CTkFrame(self.history_frame)
            row_frame.grid(row=i, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            row_frame.bind("<Button-1>", lambda e, w=workshop: self.on_workshop_click(w))

            labels = [
                ctk.CTkLabel(row_frame, text=workshop.date, anchor="w"),
                ctk.CTkLabel(row_frame, text=workshop.categorie, anchor="w"),
                ctk.CTkLabel(row_frame, text=workshop.conseiller, anchor="w"),
                ctk.CTkLabel(row_frame, text="Oui" if workshop.paid else "Non", anchor="w")  
            ]

            for col, label in enumerate(labels):
                label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
                label.bind("<Button-1>", lambda e, w=workshop: self.on_workshop_click(w))

    def on_workshop_click(self, workshop):
        if self.edit_workshop_callback:
            self.edit_workshop_callback(workshop)

    def update_user_info(self):
        self.user = User.get_by_id(self.db_manager, self.user.id)  # Rafraîchir l'utilisateur
        # Mettre à jour les champs du formulaire
        self.nom_entry.delete(0, 'end')
        self.nom_entry.insert(0, self.user.nom)
        self.prenom_entry.delete(0, 'end')
        self.prenom_entry.insert(0, self.user.prenom)
        self.telephone_entry.delete(0, 'end')
        self.telephone_entry.insert(0, self.user.telephone)
        self.date_naissance_entry.delete(0, 'end')
        self.date_naissance_entry.insert(0, convert_from_db_date(self.user.date_naissance) if self.user.date_naissance else "")
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, self.user.email if self.user.email else "")
        self.adresse_entry.delete(0, 'end')
        self.adresse_entry.insert(0, self.user.adresse if self.user.adresse else "")
        
        # Mettre à jour la liste des ateliers
        for widget in self.history_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
        self.load_user_workshops()

        # Mettre à jour le statut de paiement
        self.update_payment_status()

        # Mettre à jour le titre
        self.title.configure(text=f"Éditer le profil de {self.user.nom} {self.user.prenom}")

    def update_payment_status(self):
        self.user.calculate_workshop_payment_status(self.db_manager)  # Ajoutez cette ligne
        status = self.user.get_workshop_payment_status(self.db_manager)
        self.payment_status_value.configure(text=status)

    def update(self, observable, *args, **kwargs):
        if isinstance(observable, User) or isinstance(observable, Workshop):
            self.update_user_info()
