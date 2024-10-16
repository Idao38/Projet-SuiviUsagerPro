import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import DatabaseManager
import logging
import matplotlib
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)
matplotlib.set_loglevel("WARNING")

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        if db_manager is None:
            raise ValueError("DatabaseManager ne peut pas être None")
        self.db_manager = db_manager

        # Contenu du tableau de bord
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Titre
        self.title = ctk.CTkLabel(content_frame, text="Tableau de bord", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.pack(anchor="w", padx=20, pady=(20, 10))

        # Statistiques
        self.stats_frame = ctk.CTkFrame(content_frame)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_container = ctk.CTkFrame(self.stats_frame)
        stats_container.pack(expand=True)

        # Utilisation de grid avec des poids pour répartir l'espace
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.users_count_frame, self.users_count_label = self.create_stat_widget(stats_container, "Nombre d'usagers", "0")
        self.users_count_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.workshops_count_frame, self.workshops_count_label = self.create_stat_widget(stats_container, "Nombre d'ateliers", "0")
        self.workshops_count_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.active_users_frame, self.active_users_label = self.create_stat_widget(stats_container, "Usagers actifs", "0")
        self.active_users_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.workshops_this_month_frame, self.workshops_this_month_label = self.create_stat_widget(stats_container, "Ateliers ce mois", "0")
        self.workshops_this_month_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        # Graphique
        self.graph_frame = ctk.CTkFrame(content_frame)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
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
            logger.error(f"Erreur lors de la mise à jour des statistiques : {e}")

    def update_graph(self):
        try:
            # Obtenir la date d'il y a 12 mois
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            data = self.db_manager.fetch_all("""
                SELECT strftime('%Y-%m', datetime(substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2))) as month,
                       SUM(CASE WHEN categorie = 'Atelier numérique' THEN 1 ELSE 0 END) as numerique,
                       SUM(CASE WHEN categorie = 'Démarche administrative' THEN 1 ELSE 0 END) as administratif
                FROM workshops
                WHERE datetime(substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) >= ?
                GROUP BY month
                ORDER BY month
            """, (start_date.strftime('%Y-%m-%d'),))
            
            logger.info(f"Données récupérées détaillées : {[dict(row) for row in data]}")
            
            if not data:
                logger.warning("Aucune donnée disponible pour le graphique")
                self.display_no_data_graph()
            else:
                all_months = [
                    (start_date + timedelta(days=30*i)).strftime('%Y-%m')
                    for i in range(12)
                ]
                month_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                
                numerique = [0] * 12
                administratif = [0] * 12

                data_dict = {row['month']: row for row in data}

                for i, month in enumerate(all_months):
                    if month in data_dict:
                        row = data_dict[month]
                        numerique[i] = int(row['numerique'] or 0)
                        administratif[i] = int(row['administratif'] or 0)
                    logger.info(f"Mois {month}: numerique={numerique[i]}, administratif={administratif[i]}")

                logger.info(f"Données traitées : numerique={numerique}, administratif={administratif}")

                self.display_graph(all_months, month_labels, numerique, administratif)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du graphique : {e}")
            logger.exception("Détails de l'erreur:")

    def display_no_data_graph(self):
        if hasattr(self, 'graph_frame'):
            self.graph_frame.destroy()
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Aucune donnée disponible", ha='center', va='center', transform=ax.transAxes)
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def display_graph(self, all_months, month_labels, numerique, administratif):
        if hasattr(self, 'graph_frame'):
            self.graph_frame.destroy()
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=20)

        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)

        total_workshops = [i + a for i, a in zip(numerique, administratif)]
        max_workshops = max(total_workshops) if total_workshops else 0

        x = range(len(all_months))
        
        # Utiliser les couleurs du thème pour le fond et le texte
        bg_color = ctk.ThemeManager.theme["CTk"]["fg_color"][1]  # Couleur de fond
        text_color = ctk.ThemeManager.theme["CTk"]["text"][1]  # Couleur du texte

        # Configurer les couleurs du graphique
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        ax.spines['left'].set_color(text_color)

        # Garder les couleurs actuelles pour les barres
        ax.bar(x, numerique, label='Atelier numérique', color='#4CAF50')
        ax.bar(x, administratif, bottom=numerique, label='Démarche administrative', color='#2196F3')

        ax.set_ylabel('Nombre d\'ateliers', color=text_color)
        ax.set_title('Ateliers par mois', color=text_color)
        
        ax.set_ylim(0, max_workshops * 1.1 if max_workshops > 0 else 1)
        
        for i, total in enumerate(total_workshops):
            if total > 0:
                ax.text(i, total, str(total), ha='center', va='bottom', color=text_color)

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        fig.tight_layout()
        fig.subplots_adjust(bottom=0.2)

        ax.set_xticks(x)
        ax.set_xticklabels([f"{month_labels[datetime.strptime(m, '%Y-%m').month - 1]}\n{m[:4]}" for m in all_months], rotation=45, ha='right', color=text_color)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        logger.info("Graphique mis à jour avec succès")
