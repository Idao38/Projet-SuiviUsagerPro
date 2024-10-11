import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import DatabaseManager

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Contenu du tableau de bord
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Titre
        self.title = ctk.CTkLabel(content_frame, text="Tableau de bord", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Statistiques
        self.stats_frame = ctk.CTkFrame(content_frame)
        self.stats_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.users_count_frame, self.users_count_label = self.create_stat_widget(self.stats_frame, "Nombre d'usagers", "0")
        self.users_count_frame.grid(row=0, column=0, padx=10, pady=10)

        self.workshops_count_frame, self.workshops_count_label = self.create_stat_widget(self.stats_frame, "Nombre d'ateliers", "0")
        self.workshops_count_frame.grid(row=0, column=1, padx=10, pady=10)

        self.active_users_frame, self.active_users_label = self.create_stat_widget(self.stats_frame, "Usagers actifs", "0")
        self.active_users_frame.grid(row=0, column=2, padx=10, pady=10)

        self.workshops_this_month_frame, self.workshops_this_month_label = self.create_stat_widget(self.stats_frame, "Ateliers ce mois", "0")
        self.workshops_this_month_frame.grid(row=0, column=3, padx=10, pady=10)

        # Graphique
        self.graph_frame = ctk.CTkFrame(content_frame)
        self.graph_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.create_graph()

        self.update_stats()
        self.update_graph()

    def create_stat_widget(self, parent, label, value):
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=14)).pack(pady=(5, 0))
        value_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(pady=(0, 5))
        return frame, value_label

    def create_graph(self):
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        individual = [4, 3, 5, 2, 6, 3, 4, 3, 4, 4, 4, 4]
        administrative = [2, 4, 2, 5, 1, 4, 3, 4, 3, 3, 3, 3]

        ax.bar(months, individual, label='Atelier individuel', color='#4CAF50')
        ax.bar(months, administrative, bottom=individual, label='Atelier administratif', color='#2196F3')

        ax.set_ylabel('Nombre d\'ateliers')
        ax.set_title('Ateliers par mois')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def update_stats(self):
        if self.db_manager is None:
            print("Erreur : DatabaseManager non initialisé")
            return

        try:
            users_count = self.db_manager.fetch_all("SELECT COUNT(*) FROM users")[0][0]
            workshops_count = self.db_manager.fetch_all("SELECT COUNT(*) FROM workshops")[0][0]
            active_users = self.db_manager.fetch_all("SELECT COUNT(DISTINCT user_id) FROM workshops WHERE date >= date('now', '-30 days')")[0][0]
            workshops_this_month = self.db_manager.fetch_all("SELECT COUNT(*) FROM workshops WHERE date >= date('now', 'start of month')")[0][0]

            self.users_count_label.configure(text=str(users_count))
            self.workshops_count_label.configure(text=str(workshops_count))
            self.active_users_label.configure(text=str(active_users))
            self.workshops_this_month_label.configure(text=str(workshops_this_month))
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques : {e}")

    def update_graph(self):
        data = self.db_manager.fetch_all("""
            SELECT strftime('%m', date) as month,
                   SUM(CASE WHEN categorie = 'Individuel' THEN 1 ELSE 0 END) as individual,
                   SUM(CASE WHEN categorie = 'Administratif' THEN 1 ELSE 0 END) as administrative
            FROM workshops
            WHERE date >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month
        """)

        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        individual = [0] * 12
        administrative = [0] * 12

        for row in data:
            month_index = int(row[0]) - 1
            individual[month_index] = row[1]
            administrative[month_index] = row[2]

        self.graph_frame.destroy()
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.bar(months, individual, label='Atelier individuel', color='#4CAF50')
        ax.bar(months, administrative, bottom=individual, label='Atelier administratif', color='#2196F3')

        ax.set_ylabel('Nombre d\'ateliers')
        ax.set_title('Ateliers par mois')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)
