import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockManager:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")
        self.root.geometry("900x700")

        # Création des onglets
        self.tab_control = ttk.Notebook(root)

        # Onglets
        self.tab_dashboard = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_dashboard, text='Tableau de bord')

        self.tab_products = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_products, text='Produits')

        self.tab_sales = ttk.Frame(self.tab_control)  # Définir tab_sales ici
        self.tab_control.add(self.tab_sales, text='Ventes')

        self.tab_graphs = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_graphs, text='Graphiques')

        self.tab_control.pack(expand=1, fill="both")

        # Initialisation des onglets et de la base de données
        self.setup_database()
        self.setup_dashboard()
        self.setup_products()
        self.setup_sales()  # Appeler setup_sales après avoir défini tab_sales
        self.setup_graphs()


        
    def setup_database(self):
        self.conn = sqlite3.connect('stock.db')
        self.cur = self.conn.cursor()

        # Table des produits
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                categorie TEXT,
                quantite INTEGER,
                prix REAL,
                fournisseur TEXT
            )
        ''')

        # Table des ventes
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produit TEXT NOT NULL,
                quantite INTEGER,
                annee INTEGER,
                mois INTEGER,
                fournisseur TEXT,
                prix_total REAL
            )
        ''')

        self.conn.commit()

    
    def setup_dashboard(self):
        # Frame des statistiques
        style = ttk.Style()
        style.configure("StatsFrame.TLabelframe", background="#87CEEB")  # Bleu ciel
        style.configure("StatsFrame.TLabelframe.Label", background="#87CEEB", font=("Arial", 11, "bold"))  # Titre en bleu ciel

        # Crée un label personnalisé pour le titre "Statistiques"
        stats_label = ttk.Label(self.tab_dashboard, text="Statistiques", background="#87CEEB", font=("Helvetica", 18, "normal"))

        # Applique ce label comme titre du LabelFrame
        stats_frame = ttk.LabelFrame(self.tab_dashboard, labelwidget=stats_label, padding=(20, 40), style="StatsFrame.TLabelframe")
        stats_frame.pack(fill="x", padx=50, pady=40)

        # Style pour les labels de statistiques
        style.configure("Statistique.TLabel", background="#87CEEB", font=("Helvetica", 14, "normal"))

        self.total_produits = tk.StringVar(value="Total Produits: 0")
        self.stock_critique = tk.StringVar(value="Stock Critique: 0")
        self.valeur_totale = tk.StringVar(value="Valeur Totale: 0 DH")

        ttk.Label(stats_frame, textvariable=self.total_produits, style="Statistique.TLabel").grid(row=0, column=0, padx=5)
        ttk.Label(stats_frame, textvariable=self.stock_critique, style="Statistique.TLabel").grid(row=0, column=1, padx=5)
        ttk.Label(stats_frame, textvariable=self.valeur_totale, style="Statistique.TLabel").grid(row=0, column=2, padx=5)

        # Configurer les colonnes pour qu'elles s'étendent proportionnellement
        stats_frame.columnconfigure(0, weight=1)  # Colonne de "Total Produits"
        stats_frame.columnconfigure(1, weight=1)  # Colonne de "Stock Critique"
        stats_frame.columnconfigure(2, weight=1)  # Colonne de "Valeur Totale"

        # Frame pour les formulaires
        forms_frame = ttk.Frame(self.tab_dashboard)
        forms_frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Frame Vente de produit (gauche)
        vente_frame = ttk.LabelFrame(forms_frame, text="Vendre un produit", padding=20, style="StatsFrame.TLabelframe")
        vente_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        style.configure("Stat.TLabel", background="#87CEEB")

        # Champs pour la vente
        ttk.Label(vente_frame, text="Produit:", style="Stat.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.vente_produit = ttk.Combobox(vente_frame)
        self.vente_produit.grid(row=0, column=1, padx=5, pady=5)
        self.vente_produit.bind('<KeyRelease>', self.filtrer_combobox)

        ttk.Label(vente_frame, text="Quantité:", style="Stat.TLabel").grid(row=1, column=0, padx=5, pady=5)
        self.vente_quantite = ttk.Entry(vente_frame)
        self.vente_quantite.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(vente_frame, text="Année:", style="Stat.TLabel").grid(row=2, column=0, padx=5, pady=5)
        self.vente_annee = ttk.Combobox(vente_frame, values=[str(year) for year in range(2000, 2031)])
        self.vente_annee.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(vente_frame, text="Mois:", style="Stat.TLabel").grid(row=3, column=0, padx=5, pady=5)
        self.vente_mois = ttk.Combobox(vente_frame, values=[str(month).zfill(2) for month in range(1, 13)])
        self.vente_mois.grid(row=3, column=1, padx=5, pady=5)

        # Déplacer le bouton "Vendre" sous les champs "Année" et "Mois"
        style.configure("Green.TButton", background="green", foreground="green")
        ttk.Button(vente_frame, text="Vendre", command=self.vendre_produit, style="Green.TButton").grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Frame Ajout rapide de produit (droite)
        ajout_frame = ttk.LabelFrame(forms_frame, text="Ajouter un produit", padding=20, style="StatsFrame.TLabelframe")
        ajout_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Champs pour l'ajout rapide
        labels = ['Nom:', 'Catégorie:', 'Quantité:', 'Prix:', 'Fournisseur:']
        self.ajout_rapide_vars = {}

        for i, label in enumerate(labels):
            ttk.Label(ajout_frame, text=label, style="Stat.TLabel").grid(row=i, column=0, padx=5, pady=5)
            var = tk.StringVar()
            self.ajout_rapide_vars[label] = var
            ttk.Entry(ajout_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(ajout_frame, text="Ajouter", command=self.ajouter_produit, style="Green.TButton").grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )

        # Configuration du grid
        forms_frame.grid_columnconfigure(0, weight=1)
        forms_frame.grid_columnconfigure(1, weight=1)

        # Mise à jour des statistiques
        self.update_statistics()
        self.update_vente_combobox()

    def setup_products(self):
        # Frame de recherche
        search_frame = ttk.Frame(self.tab_products)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="Rechercher:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_products)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=5)
        
        # Frame des formulaires
        form_frame = ttk.LabelFrame(self.tab_products, text="Ajouter/Modifier un produit", padding=20)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Champs de formulaire
        labels = ['Nom:', 'Catégorie:', 'Quantité:', 'Prix:', 'Fournisseur:']
        self.form_vars = {}
        
        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            var = tk.StringVar()
            self.form_vars[label] = var
            ttk.Entry(form_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Modifier", command=self.modifier_produit).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.supprimer_produit).pack(side="left", padx=5)
        
        # Liste des produits
        tree_frame = ttk.LabelFrame(self.tab_products, text="Liste des produits", padding=20)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Nom', 'Catégorie', 'Quantité', 'Prix', 'Fournisseur')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=100)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Chargement initial des produits
        self.load_products()
    
    def load_products(self):
        self.tree.delete(*self.tree.get_children())
        self.cur.execute('SELECT * FROM produits')
        for row in self.cur.fetchall():
            self.tree.insert('', 'end', values=row)
    
    def search_products(self, *args):
        search_term = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        self.cur.execute('SELECT * FROM produits WHERE LOWER(nom) LIKE ? OR LOWER(categorie) LIKE ?',
                        (f'%{search_term}%', f'%{search_term}%'))
        for row in self.cur.fetchall():
            self.tree.insert('', 'end', values=row)
    
    def sort_treeview(self, col):
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
    
    def update_statistics(self):
        self.cur.execute('SELECT COUNT(*) FROM produits')
        total = self.cur.fetchone()[0]
        self.total_produits.set(f"Total Produits: {total}")
        
        self.cur.execute('SELECT COUNT(*) FROM produits WHERE quantite < 10')
        critique = self.cur.fetchone()[0]
        self.stock_critique.set(f"Stock Critique: {critique}")
        
        self.cur.execute('SELECT SUM(prix * quantite) FROM produits')
        valeur = self.cur.fetchone()[0] or 0
        self.valeur_totale.set(f"Valeur Totale: {valeur:.2f} DH")

    def vendre_produit(self):
        # Récupérer les données du formulaire
        produit = self.vente_produit.get()
        quantite = self.vente_quantite.get()
        annee = self.vente_annee.get()
        mois = self.vente_mois.get()

        if not produit or not quantite or not annee or not mois:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
            return

        try:
            quantite = int(quantite)
            if quantite <= 0:
                raise ValueError("La quantité doit être un nombre positif.")

            # Vérifier si le produit existe
            self.cur.execute('SELECT quantite, fournisseur, prix FROM produits WHERE nom=?', (produit,))
            result = self.cur.fetchone()

            if not result:
                messagebox.showerror("Erreur", "Le produit sélectionné n'existe pas.")
                return

            stock_disponible, fournisseur, prix_unitaire = result

            # Vérifier si la quantité demandée est disponible
            if quantite > stock_disponible:
                messagebox.showerror("Erreur", "Quantité demandée supérieure au stock disponible.")
                return

            # Mettre à jour la quantité en stock
            nouvelle_quantite = stock_disponible - quantite
            self.cur.execute('UPDATE produits SET quantite=? WHERE nom=?', (nouvelle_quantite, produit))
            self.conn.commit()

            # Calculer le prix total
            prix_total = quantite * prix_unitaire

            # Enregistrer la vente dans la table `ventes`
            self.cur.execute('''
                INSERT INTO ventes (produit, quantite, annee, mois, fournisseur, prix_total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (produit, quantite, annee, mois, fournisseur, prix_total))
            self.conn.commit()

            # Mettre à jour l'interface
            self.load_products()
            self.load_sales()  # Recharger les ventes
            self.update_statistics()
            messagebox.showinfo("Succès", "Produit vendu avec succès!")
            self.clear_form(form_type="vente")

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une quantité valide.")



    def update_vente_combobox(self):
        # Récupérer tous les noms de produits depuis la base de données
        self.cur.execute('SELECT nom FROM produits')
        produits = [row[0] for row in self.cur.fetchall()]
    
        # Mettre à jour les options de la Combobox
        self.vente_produit['values'] = produits
        
    def filtrer_combobox(self, event):
        # Récupère la saisie de l'utilisateur
        saisie = self.vente_produit.get().lower()
    
        # Récupère tous les produits de la base de données
        self.cur.execute("SELECT nom FROM produits")
        produits = [row[0] for row in self.cur.fetchall()]
    
        # Filtre les produits correspondant à la saisie
        filtres = [produit for produit in produits if saisie in produit.lower()]
    
        # Met à jour les options de la Combobox
        self.vente_produit['values'] = filtres
       
    def ajouter_produit(self):
        try:
            values = [var.get() for var in self.ajout_rapide_vars.values()]
            if any(not value for value in values):
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
                return
        
            self.cur.execute('''
                INSERT INTO produits (nom, categorie, quantite, prix, fournisseur)
                VALUES (?, ?, ?, ?, ?)
            ''', values)
            self.conn.commit()

            # Mettre à jour l'interface
            self.load_products()
            self.update_statistics()
            self.update_vente_combobox()  # Mettre à jour la liste des produits pour la vente
            messagebox.showinfo("Succès", "Produit ajouté avec succès!")
            self.clear_form(form_type="ajouter")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")


    def setup_sales(self):
        sales_frame = ttk.LabelFrame(self.tab_sales, text="Liste des ventes", padding=20)
        sales_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ('ID', 'Produit', 'Quantité', 'Année', 'Mois', 'Fournisseur', 'Prix Total')
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns, show='headings')

        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120)

        self.sales_tree.pack(fill="both", expand=True)

        # Ajouter un bouton pour supprimer les ventes
        ttk.Button(self.tab_sales, text="Supprimer la vente", command=self.supprimer_vente).pack(pady=10)

        self.load_sales()



    def load_sales(self):
        # Effacer les données existantes
        self.sales_tree.delete(*self.sales_tree.get_children())

        # Charger les données depuis la base
        self.cur.execute('SELECT * FROM ventes')
        for row in self.cur.fetchall():
            self.sales_tree.insert('', 'end', values=row)


    def supprimer_vente(self):
        selected_item = self.sales_tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une vente à supprimer.")
            return

        item = self.sales_tree.item(selected_item[0])
        vente_id = item['values'][0]  # ID de la vente

        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette vente ?"):
            self.cur.execute('DELETE FROM ventes WHERE id=?', (vente_id,))
            self.conn.commit()

            # Mettre à jour l'interface
            self.load_sales()
            messagebox.showinfo("Succès", "Vente supprimée avec succès !")



    
    def modifier_produit(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un produit à modifier")
            return
        
        try:
            values = [var.get() for var in self.form_vars.values()]
            values.append(self.selected_id)
            
            self.cur.execute('''
                UPDATE produits
                SET nom=?, categorie=?, quantite=?, prix=?, fournisseur=?
                WHERE id=?
            ''', values)
            self.conn.commit()
            
            self.load_products()
            self.update_statistics()
            self.clear_form()
            messagebox.showinfo("Succès", "Produit modifié avec succès!")
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides")
    
    def supprimer_produit(self):
        if not self.selected_id:
            messagebox.showwarning("Attention", "Veuillez sélectionner un produit à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce produit?"):
            self.cur.execute('DELETE FROM produits WHERE id=?', (self.selected_id,))
            self.conn.commit()
            
            self.load_products()
            self.update_statistics()
            self.clear_form()
            messagebox.showinfo("Succès", "Produit supprimé avec succès!")
    
    def on_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = self.tree.item(selected_items[0])
        values = item['values']
        self.selected_id = values[0]
        
        # Mise à jour des champs du formulaire
        for i, var in enumerate(self.form_vars.values()):
            var.set(values[i + 1])

    def setup_graphs(self):
            # Diviser l'onglet en trois espaces
            frame1 = ttk.LabelFrame(self.tab_graphs, text="Pourcentage des ventes par catégorie")
            frame1.pack(fill="both", expand=True, padx=10, pady=10)

            frame2 = ttk.LabelFrame(self.tab_graphs, text="Quantité des ventes par mois")
            frame2.pack(fill="both", expand=True, padx=10, pady=10)

            frame3 = ttk.LabelFrame(self.tab_graphs, text="Variabilité des ventes par mois")
            frame3.pack(fill="both", expand=True, padx=10, pady=10)
  
        # Premier graphique : Diagramme circulaire
            ttk.Label(frame1, text="Année:").grid(row=0, column=0, padx=5, pady=5)
            self.pie_annee = ttk.Combobox(frame1, values=[str(year) for year in range(2000, 2031)])
            self.pie_annee.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(frame1, text="Mois:").grid(row=0, column=2, padx=5, pady=5)
            self.pie_mois = ttk.Combobox(frame1, values=[str(month).zfill(2) for month in range(1, 13)])
            self.pie_mois.grid(row=0, column=3, padx=5, pady=5)

            ttk.Button(frame1, text="Afficher", command=self.show_pie_chart).grid(row=0, column=4, padx=10, pady=5)

            # Deuxième graphique : Diagramme en barres
            ttk.Label(frame2, text="Année:").grid(row=0, column=0, padx=5, pady=5)
            self.bar_annee = ttk.Combobox(frame2, values=[str(year) for year in range(2000, 2031)])
            self.bar_annee.grid(row=0, column=1, padx=5, pady=5)

            ttk.Button(frame2, text="Afficher", command=self.show_bar_chart).grid(row=0, column=2, padx=10, pady=5)

            # Troisième graphique : Graphique linéaire
            ttk.Label(frame3, text="Année:").grid(row=0, column=0, padx=5, pady=5)
            self.line_annee = ttk.Combobox(frame3, values=[str(year) for year in range(2000, 2031)])
            self.line_annee.grid(row=0, column=1, padx=5, pady=5)

            ttk.Button(frame3, text="Afficher", command=self.show_line_chart).grid(row=0, column=2, padx=10, pady=5)


    
    def show_pie_chart(self):
        # Récupérer les données pour le pie chart
        annee = self.pie_annee.get()
        mois = self.pie_mois.get()

        if not annee or not mois:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année et un mois.")
            return

        self.cur.execute('''
            SELECT categorie, SUM(quantite)
            FROM ventes
            JOIN produits ON ventes.produit = produits.nom
            WHERE annee=? AND mois=?
            GROUP BY categorie
        ''', (annee, mois))

        data = self.cur.fetchall()
        if not data:
            messagebox.showinfo("Information", "Aucune donnée pour la période sélectionnée.")
            return

        categories = [row[0] for row in data]
        quantities = [row[1] for row in data]

        # Créer le graphique
        fig, ax = plt.subplots()
        ax.pie(quantities, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Cercle parfait
        plt.title(f"Pourcentage des ventes par catégorie - {mois}/{annee}")

        # Afficher dans une nouvelle fenêtre
        self.display_graph_in_new_window(fig, "Graphique circulaire")


    def show_bar_chart(self):
        # Récupérer les données pour le bar chart
        annee = self.bar_annee.get()

        if not annee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année.")
            return

        self.cur.execute('''
            SELECT mois, SUM(quantite)
            FROM ventes
            WHERE annee=?
            GROUP BY mois
            ORDER BY mois
        ''', (annee,))

        data = self.cur.fetchall()
        if not data:
            messagebox.showinfo("Information", "Aucune donnée pour l'année sélectionnée.")
            return

        months = [row[0] for row in data]
        quantities = [row[1] for row in data]

        # Créer le graphique
        fig, ax = plt.subplots()
        ax.bar(months, quantities, color='skyblue')
        plt.xlabel('Mois')
        plt.ylabel('Quantité vendue')
        plt.title(f"Quantité des ventes par mois - {annee}")

        # Afficher dans une nouvelle fenêtre
        self.display_graph_in_new_window(fig, "Diagramme en barres")



    def show_line_chart(self):
        # Récupérer les données pour le graphique linéaire
        annee = self.line_annee.get()

        if not annee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année.")
            return

        self.cur.execute('''
            SELECT mois, SUM(quantite)
            FROM ventes
            WHERE annee=?
            GROUP BY mois
            ORDER BY mois
        ''', (annee,))

        data = self.cur.fetchall()
        if not data:
            messagebox.showinfo("Information", "Aucune donnée pour l'année sélectionnée.")
            return

        months = [row[0] for row in data]
        quantities = [row[1] for row in data]

        # Créer le graphique
        fig, ax = plt.subplots()
        ax.plot(months, quantities, marker='o', linestyle='-', color='r')
        plt.xlabel('Mois')
        plt.ylabel('Quantité vendue')
        plt.title(f"Variabilité des ventes par mois - {annee}")

        # Afficher dans une nouvelle fenêtre
        self.display_graph_in_new_window(fig, "Graphique linéaire")



    def display_graph_in_new_window(self, fig, title):
        # Créer une nouvelle fenêtre
        new_window = tk.Toplevel(self.root)
        new_window.title(title)
        new_window.geometry("600x500")
    
        # Ajouter le graphique à la fenêtre
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def display_graph(self, fig):
        # Supprimer les graphiques existants avant d'afficher un nouveau graphique
        for widget in self.tab_graphs.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()

        # Créer un canvas pour afficher le graphique
        canvas = FigureCanvasTkAgg(fig, master=self.tab_graphs)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)









    
    def clear_form(self, form_type="produit"):
        if form_type == "produit":
         # Réinitialiser les champs de l'interface Produits
            for var in self.form_vars.values():
                var.set('')
        # Réinitialiser les champs de l'interface Tableau de bord
        elif form_type == "ajouter":
            # Réinitialiser le champ de produit
            for var in self.ajout_rapide_vars.values():
                var.set('')
        elif form_type == "vente" :
            #réinitialisé le champ de vente
            self.vente_quantite.delete(0, 'end') 
            self.vente_produit.delete(0, 'end')  
     
            
    
        self.selected_id = None

if __name__ == "__main__":
    root = tk.Tk()
    app = StockManager(root)
    root.mainloop()