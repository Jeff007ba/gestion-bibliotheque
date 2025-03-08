import json
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTableWidget, QVBoxLayout, QDialog, QPushButton, QLabel, QLineEdit, QListWidget, QWidget, QMessageBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from datetime import datetime

# Importe tes classes et fonctions existantes
from Backend.livre import Livre
from Backend.utilisateur import Utilisateur
from Backend.arbre_binaire import ArbreBinaire
from Backend.liste_chainee import ListeChainee
from Backend.pile_historique import Pile

# Initialisation des structures de données
bibliotheque = ArbreBinaire()
utilisateurs = ListeChainee()
historique = Pile()

class BibliothequeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de la Bibliothèque Numérique")
        self.setGeometry(100, 100, 1000, 800)


        # Onglets principaux
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Onglet Livres
        self.livres_tab = QWidget()
        self.setup_livres_tab()
        self.tabs.addTab(self.livres_tab, "Livres")

        # Onglet Utilisateurs
        self.utilisateurs_tab = QWidget()
        self.setup_utilisateurs_tab()
        self.tabs.addTab(self.utilisateurs_tab, "Utilisateurs")

        # Onglet Emprunts/Retours
        self.emprunts_tab = QWidget()
        self.setup_emprunts_tab()
        self.tabs.addTab(self.emprunts_tab, "Emprunts/Retours")

        # Onglet Historique
        self.historique_tab = QWidget()
        self.setup_historique_tab()
        self.tabs.addTab(self.historique_tab, "Historique")

        self.charger_donnees()

    def sauvegarder_donnees(self):
        # Chemin relatif vers le fichier JSON dans le dossier backend
        chemin_dossier = os.path.join("..", "Data")
        chemin_fichier = os.path.join(chemin_dossier, "donnees_bibliotheque.json")

        # Créer le dossier Data s'il n'existe pas
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)

        # Préparer les données à sauvegarder
        donnees = {
            "livres": [],
            "utilisateurs": []
        }

        # Sauvegarder les livres
        livres = []
        _parcourir_arbre(bibliotheque.racine, livres)
        for livre in livres:
            donnees["livres"].append({
                "isbn": livre.isbn,
                "titre": livre.titre,
                "auteur": livre.auteur,
                "annee": livre.annee,
                "categorie": livre.categorie,
                "emprunte": livre.emprunte
            })

        # Sauvegarder les utilisateurs
        for utilisateur in utilisateurs.lister():
            donnees["utilisateurs"].append({
                "nom": utilisateur.nom,
                "id": utilisateur.id,
                "email": utilisateur.email
            })

        # Écrire les données dans un fichier JSON
        try:
            with open(chemin_fichier, "w") as fichier:
                json.dump(donnees, fichier, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def charger_donnees(self):
        # Chemin relatif vers le fichier JSON dans le dossier backend
        chemin_fichier = os.path.join("../Data", "donnees_bibliotheque.json")

        try:
            with open(chemin_fichier, "r") as fichier:
                donnees = json.load(fichier)

                # Charger les livres
                for livre_data in donnees["livres"]:
                    livre = Livre(
                        livre_data["isbn"],
                        livre_data["titre"],
                        livre_data["auteur"],
                        livre_data["annee"],
                        livre_data["categorie"]
                    )
                    livre.emprunte = livre_data["emprunte"]
                    bibliotheque.ajouter(livre)

                # Charger les utilisateurs
                for utilisateur_data in donnees["utilisateurs"]:
                    utilisateur = Utilisateur(
                        utilisateur_data["nom"],
                        utilisateur_data["id"],
                        utilisateur_data["email"]
                    )
                    utilisateurs.ajouter(utilisateur)

                self.update_livres_list()
                self.update_utilisateurs_list()
        except FileNotFoundError:
            print("Aucune donnée trouvée. Démarrage avec une bibliothèque vide.")
        except json.JSONDecodeError:
            print("Erreur : Le fichier JSON est corrompu ou mal formaté.")
        except PermissionError:
            print("Erreur : Permission refusée pour accéder au fichier.")
        except Exception as e:
            print(f"Erreur inattendue lors du chargement des données : {e}")

    def closeEvent(self, event):
        # Sauvegarder les données à la fermeture
        self.sauvegarder_donnees()
        event.accept()

    def setup_livres_tab(self):
        layout = QVBoxLayout()

        # Formulaire pour ajouter un livre
        form_livre = QFormLayout()
        self.isbn_input = QLineEdit()
        self.titre_input = QLineEdit()
        self.auteur_input = QLineEdit()
        self.annee_input = QLineEdit()
        self.categorie_input = QLineEdit()
        form_livre.addRow("ISBN", self.isbn_input)
        form_livre.addRow("Titre", self.titre_input)
        form_livre.addRow("Auteur", self.auteur_input)
        form_livre.addRow("Année", self.annee_input)
        form_livre.addRow("Catégorie", self.categorie_input)
        self.ajouter_livre_btn = QPushButton("Ajouter un livre")
        self.ajouter_livre_btn.clicked.connect(self.ajouter_livre)
        layout.addLayout(form_livre)
        layout.addWidget(self.ajouter_livre_btn)

        # Bouton pour modifier un livre
        self.modifier_livre_btn = QPushButton("Modifier un livre")
        self.modifier_livre_btn.clicked.connect(self.modifier_livre)
        layout.addWidget(self.modifier_livre_btn)

        self.livres_tab.setLayout(layout)
        # Rechercher un livre
        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("Rechercher par titre ou auteur")
        self.recherche_btn = QPushButton("Rechercher")
        self.recherche_btn.clicked.connect(self.rechercher_livre)
        layout.addWidget(self.recherche_input)
        layout.addWidget(self.recherche_btn)

        # Liste des livres
        self.livres_list = QListWidget(self)
        self.livres_list.setStyleSheet("""
                QListWidget {
                    background-color: black;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                }
                QListWidget::item {
                    padding: 5px;
                }
            """)
        layout.addWidget(QLabel("Liste des livres :"))
        layout.addWidget(self.livres_list)

        # Bouton pour afficher les livres disponibles
        self.livres_disponibles_btn = QPushButton("Afficher les livres disponibles")
        self.livres_disponibles_btn.clicked.connect(self.afficher_livres_disponibles)
        layout.addWidget(self.livres_disponibles_btn)

        # Bouton pour supprimer un livre
        self.supprimer_livre_btn = QPushButton("Supprimer un livre")
        self.supprimer_livre_btn.clicked.connect(self.supprimer_livre)
        layout.addWidget(self.supprimer_livre_btn)

        self.livres_tab.setLayout(layout)

    def modifier_livre(self):
        # Vérifier qu'un livre est sélectionné
        if not self.livres_list.currentItem():
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un livre à modifier.")
            return

        # Récupérer le livre sélectionné
        livre_titre = self.livres_list.currentItem().text().split(" par ")[0]
        livre_trouve = bibliotheque.rechercher_par_titre(livre_titre)

        if not livre_trouve:
            QMessageBox.warning(self, "Erreur", "Livre non trouvé.")
            return

        # Ouvrir une fenêtre de dialogue pour modifier le livre
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un livre")
        layout = QFormLayout(dialog)

        # Champs pour modifier le livre
        nouveau_titre = QLineEdit(livre_trouve.livre.titre)
        nouveau_auteur = QLineEdit(livre_trouve.livre.auteur)
        nouvelle_annee = QLineEdit(str(livre_trouve.livre.annee))
        nouvelle_categorie = QLineEdit(livre_trouve.livre.categorie)
        nouveau_isbn = QLineEdit(livre_trouve.livre.isbn)

        layout.addRow("Titre :", nouveau_titre)
        layout.addRow("Auteur :", nouveau_auteur)
        layout.addRow("Année :", nouvelle_annee)
        layout.addRow("Catégorie :", nouvelle_categorie)
        layout.addRow("ISBN :", nouveau_isbn)

        # Bouton pour valider les modifications
        valider_btn = QPushButton("Valider")
        valider_btn.clicked.connect(lambda: self.valider_modification_livre(
            livre_trouve.livre, nouveau_titre.text(), nouveau_auteur.text(), nouvelle_annee.text(),
            nouvelle_categorie.text(), nouveau_isbn.text(), dialog
        ))
        layout.addWidget(valider_btn)

        dialog.exec()

    def valider_modification_livre(self, livre, titre, auteur, annee, categorie, isbn, dialog):
        # Vérifier que tous les champs sont remplis
        if not titre or not auteur or not annee or not categorie or not isbn:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # Vérifier que l'année est un nombre valide
        try:
            annee = int(annee)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'année doit être un nombre valide.")
            return

        # Mettre à jour les informations du livre
        livre.titre = titre
        livre.auteur = auteur
        livre.annee = annee
        livre.categorie = categorie
        livre.isbn = isbn

        # Mettre à jour l'affichage
        self.update_livres_list()
        dialog.close()
        QMessageBox.information(self, "Succès", "Livre modifié avec succès !")

    def setup_utilisateurs_tab(self):
        layout = QVBoxLayout()

        # Formulaire pour ajouter un utilisateur
        form_utilisateur = QFormLayout()
        self.nom_input = QLineEdit()
        self.id_input = QLineEdit()
        self.email_input = QLineEdit()
        form_utilisateur.addRow("ID", self.id_input)
        form_utilisateur.addRow("Nom", self.nom_input)
        form_utilisateur.addRow("Email", self.email_input)
        self.ajouter_utilisateur_btn = QPushButton("Ajouter un utilisateur")
        self.ajouter_utilisateur_btn.clicked.connect(self.ajouter_utilisateur)
        layout.addLayout(form_utilisateur)
        layout.addWidget(self.ajouter_utilisateur_btn)
        self.modifier_utilisateur_btn = QPushButton("Modifier un utilisateur")
        self.modifier_utilisateur_btn.clicked.connect(self.modifier_utilisateur)
        layout.addWidget(self.modifier_utilisateur_btn)


        # Liste des utilisateurs
        self.utilisateurs_list = QListWidget(self)
        self.utilisateurs_list.setStyleSheet("""
                QListWidget {
                    background-color: black;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                }
                QListWidget::item {
                    padding: 5px;
                }
            """)
        layout.addWidget(QLabel("Liste des utilisateurs :"))
        layout.addWidget(self.utilisateurs_list)

        # Bouton pour supprimer un utilisateur
        self.supprimer_utilisateur_btn = QPushButton("Supprimer un utilisateur")
        self.supprimer_utilisateur_btn.clicked.connect(self.supprimer_utilisateur)
        layout.addWidget(self.supprimer_utilisateur_btn)

        self.utilisateurs_tab.setLayout(layout)

    def modifier_utilisateur(self):
        # Vérifier qu'un utilisateur est sélectionné
        if not self.utilisateurs_list.currentItem():
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un utilisateur à modifier.")
            return

        # Récupérer l'utilisateur sélectionné
        utilisateur_info = self.utilisateurs_list.currentItem().text()
        utilisateur_id = int(utilisateur_info.split("ID: ")[1].split(",")[0])
        utilisateur_trouve = None

        for utilisateur in utilisateurs.lister():
            if utilisateur.id == utilisateur_id:
                utilisateur_trouve = utilisateur
                break

        if not utilisateur_trouve:
            QMessageBox.warning(self, "Erreur", "Utilisateur non trouvé.")
            return

        # Ouvrir une fenêtre de dialogue pour modifier l'utilisateur
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un utilisateur")
        layout = QFormLayout(dialog)

        # Champs pour modifier l'utilisateur
        nouveau_id = QLineEdit(str(utilisateur_trouve.id))
        nouveau_nom = QLineEdit(utilisateur_trouve.nom)
        nouveau_email = QLineEdit(utilisateur_trouve.email)

        layout.addRow("ID :", nouveau_id)
        layout.addRow("Nom :", nouveau_nom)
        layout.addRow("Email :", nouveau_email)

        # Bouton pour valider les modifications
        valider_btn = QPushButton("Valider")
        valider_btn.clicked.connect(lambda: self.valider_modification_utilisateur(
            utilisateur_trouve, nouveau_nom.text(), nouveau_id.text(), nouveau_email.text(), dialog
        ))
        layout.addWidget(valider_btn)

        dialog.exec()

    def valider_modification_utilisateur(self, utilisateur, nom, id, email, dialog):
        # Vérifier que tous les champs sont remplis
        if not nom or not id or not email:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # Vérifier que l'ID est un nombre valide
        try:
            id = int(id)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'ID doit être un nombre valide.")
            return

        # Vérifier si l'ID est déjà utilisé par un autre utilisateur
        for u in utilisateurs.lister():
            if u.id == id and u != utilisateur:
                QMessageBox.warning(self, "Erreur", "Cet ID est déjà utilisé par un autre utilisateur.")
                return

        # Mettre à jour les informations de l'utilisateur
        utilisateur.id = id
        utilisateur.nom = nom
        utilisateur.email = email

        # Mettre à jour l'affichage
        self.update_utilisateurs_list()
        dialog.close()
        QMessageBox.information(self, "Succès", "Utilisateur modifié avec succès !")


    def setup_emprunts_tab(self):
        layout = QVBoxLayout()

        # Titre de la section
        titre_emprunt = QLabel("Emprunter un livre")
        titre_emprunt.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titre_emprunt)

        # Formulaire pour emprunter un livre
        form_emprunt = QFormLayout()
        self.livre_emprunt_combo = QComboBox()
        self.livre_emprunt_combo.setPlaceholderText("Sélectionner un livre")
        self.utilisateur_emprunt_combo = QComboBox()
        self.utilisateur_emprunt_combo.setPlaceholderText("Sélectionner un utilisateur")
        form_emprunt.addRow("Livre à emprunter :", self.livre_emprunt_combo)
        form_emprunt.addRow("Utilisateur :", self.utilisateur_emprunt_combo)
        self.emprunter_btn = QPushButton("Emprunter")
        self.emprunter_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.emprunter_btn.clicked.connect(self.emprunter_livre)
        layout.addLayout(form_emprunt)
        layout.addWidget(self.emprunter_btn)

        # Séparateur
        separateur = QLabel("-----------------------------")
        separateur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separateur)

        # Titre de la section
        titre_retour = QLabel("Retourner un livre")
        titre_retour.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titre_retour)

        # Formulaire pour retourner un livre
        form_retour = QFormLayout()
        self.livre_retour_combo = QComboBox()
        self.livre_retour_combo.setPlaceholderText("Sélectionner un livre")
        form_retour.addRow("Livre à retourner :", self.livre_retour_combo)
        self.retourner_btn = QPushButton("Retourner")
        self.retourner_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.retourner_btn.clicked.connect(self.retourner_livre)
        layout.addLayout(form_retour)
        layout.addWidget(self.retourner_btn)

        self.emprunts_tab.setLayout(layout)

        # Mettre à jour les listes déroulantes lorsque l'onglet est affiché
        self.emprunts_tab.showEvent = self.update_emprunt_combos

    def update_emprunt_combos(self, event=None):
        # Mettre à jour la liste des livres disponibles pour l'emprunt
        self.livre_emprunt_combo.clear()
        livres = []
        _parcourir_arbre(bibliotheque.racine, livres)
        for livre in livres:
            if not livre.emprunte:
                self.livre_emprunt_combo.addItem(livre.titre)

        # Mettre à jour la liste des livres empruntés pour le retour
        self.livre_retour_combo.clear()
        for livre in livres:
            if livre.emprunte:
                self.livre_retour_combo.addItem(livre.titre)

        # Mettre à jour la liste des utilisateurs
        self.utilisateur_emprunt_combo.clear()
        for utilisateur in utilisateurs.lister():
            self.utilisateur_emprunt_combo.addItem(f"{utilisateur.nom} (ID: {utilisateur.id})")

    def setup_historique_tab(self):
        layout = QVBoxLayout()

        # Historique des actions
        self.historique_list = QListWidget(self)
        self.historique_list.setStyleSheet("""
                QListWidget {
                    background-color: black;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                }
                QListWidget::item {
                    padding: 5px;
                }
            """)
        layout.addWidget(QLabel("Historique des actions :"))
        layout.addWidget(self.historique_list)

        # Bouton pour annuler la dernière action
        self.annuler_btn = QPushButton("Annuler la dernière action")
        self.annuler_btn.clicked.connect(self.annuler_derniere_action)
        layout.addWidget(self.annuler_btn)

        self.historique_tab.setLayout(layout)

    def ajouter_livre(self):
        # Récupérer les valeurs des champs
        isbn = self.isbn_input.text().strip()
        titre = self.titre_input.text().strip()
        auteur = self.auteur_input.text().strip()
        annee = self.annee_input.text().strip()
        categorie = self.categorie_input.text().strip()

        # Vérifier que tous les champs sont remplis
        if not isbn or not titre or not auteur or not annee or not categorie:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # Vérifier que l'année est un nombre valide
        try:
            annee = int(annee)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'année doit être un nombre valide.")
            return

        # Vérifier si le livre existe déjà (optionnel, si tu veux éviter les doublons)
        livre_existant = bibliotheque.rechercher_par_titre(titre)
        if livre_existant:
            QMessageBox.warning(self, "Erreur", "Un livre avec ce titre existe déjà.")
            return

        # Ajouter le livre
        livre = Livre(isbn, titre, auteur, annee, categorie)
        bibliotheque.ajouter(livre)
        empiler_historique("ajout_livre", livre, f"Ajout du livre : {titre}")
        self.update_livres_list()
        self.update_historique_list()

        QMessageBox.information(self, "Succès", f"Livre '{titre}' ajouté avec succès !")
        self.isbn_input.clear()
        self.titre_input.clear()
        self.auteur_input.clear()
        self.annee_input.clear()
        self.categorie_input.clear()

    def rechercher_livre(self):
        recherche = self.recherche_input.text()
        resultats_titre = bibliotheque.rechercher_par_titre(recherche)
        resultats_auteur = bibliotheque.rechercher_par_auteur(recherche)

        if resultats_titre:
            self.livres_list.clear()
            self.livres_list.addItem(f"Livre trouvé : {resultats_titre.livre}")
        elif resultats_auteur:
            self.livres_list.clear()
            for livre in resultats_auteur:
                self.livres_list.addItem(f"Livre trouvé : {str(livre)}")
        else:
            QMessageBox.warning(self, "Erreur", "Aucun livre trouvé.")

    def ajouter_utilisateur(self):
        # Récupérer les valeurs des champs
        nom = self.nom_input.text().strip()
        id = self.id_input.text().strip()
        email = self.email_input.text().strip()

        # Vérifier que tous les champs sont remplis
        if not nom or not id or not email:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # Vérifier que l'ID est un nombre valide
        try:
            id = int(id)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'ID doit être un nombre valide.")
            return

        # Vérifier si l'ID est déjà utilisé
        for utilisateur in utilisateurs.lister():
            if utilisateur.id == id:
                QMessageBox.warning(self, "Erreur", "Cet ID est déjà utilisé par un autre utilisateur.")
                return

        # Ajouter l'utilisateur
        utilisateur = Utilisateur(nom, id, email)
        utilisateurs.ajouter(utilisateur)
        empiler_historique("ajout_utilisateur", utilisateur, f"Ajout de l'utilisateur : {nom} (ID: {id})")
        self.update_utilisateurs_list()
        self.update_historique_list()
        QMessageBox.information(self, "Succès", f"Utilisateur '{nom}' ajouté avec succès !")
        self.nom_input.clear()
        self.id_input.clear()
        self.email_input.clear()


    def emprunter_livre(self):
        livre_titre = self.livre_emprunt_combo.currentText()
        utilisateur_info = self.utilisateur_emprunt_combo.currentText()

        # Vérifier qu'un livre et un utilisateur sont sélectionnés
        if not livre_titre or not utilisateur_info:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un livre et un utilisateur.")
            return

        # Trouver le livre et l'utilisateur
        livre_trouve = bibliotheque.rechercher_par_titre(livre_titre)
        utilisateur_id = int(utilisateur_info.split("ID: ")[1].split(")")[0])

        if livre_trouve:
            if livre_trouve.livre.emprunte:
                QMessageBox.warning(self, "Erreur", "Le livre est déjà emprunté.")
            else:
                utilisateur_trouve = None
                for utilisateur in utilisateurs.lister():
                    if utilisateur.id == utilisateur_id:
                        utilisateur_trouve = utilisateur
                        break
                if utilisateur_trouve:
                    livre_trouve.livre.emprunte = True
                    empiler_historique("emprunt_livre", livre_trouve.livre,
                                       f"Emprunt : {livre_trouve.livre.titre} par {utilisateur_trouve.nom}")
                    self.update_emprunt_combos()  # Mettre à jour les listes déroulantes
                    self.update_historique_list()  # Mettre à jour l'historique
                    QMessageBox.information(self, "Succès",
                                            f"Livre '{livre_trouve.livre.titre}' emprunté par {utilisateur_trouve.nom}.")
                else:
                    QMessageBox.warning(self, "Erreur", "Utilisateur non trouvé.")
        else:
            QMessageBox.warning(self, "Erreur", "Livre non trouvé.")

    def retourner_livre(self):
        livre_titre = self.livre_retour_combo.currentText()

        # Vérifier qu'un livre est sélectionné
        if not livre_titre:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un livre à retourner.")
            return

        # Trouver le livre
        livre_trouve = bibliotheque.rechercher_par_titre(livre_titre)
        if livre_trouve:
            if livre_trouve.livre.emprunte:
                livre_trouve.livre.emprunte = False
                empiler_historique("retour_livre", livre_trouve.livre, f"Retour : {livre_trouve.livre.titre}")
                self.update_emprunt_combos()  # Mettre à jour les listes déroulantes
                self.update_historique_list()  # Mettre à jour l'historique
                QMessageBox.information(self, "Succès", f"Livre '{livre_trouve.livre.titre}' retourné avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "Le livre n'est pas emprunté.")
        else:
            QMessageBox.warning(self, "Erreur", "Livre non trouvé.")

    def supprimer_livre(self):
        titre = self.livres_list.currentItem().text().split(" par ")[0]
        livre_trouve = bibliotheque.rechercher_par_titre(titre)
        if livre_trouve:
            if livre_trouve.livre.emprunte:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer, le livre est emprunté.")
            else:
                bibliotheque.supprimer_livre(titre)
                empiler_historique("suppression_livre", livre_trouve.livre, f"Suppression du livre : {titre}")
                self.update_livres_list()
                self.update_historique_list()
                QMessageBox.information(self, "Succès", f"Livre '{titre}' supprimé avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", "Livre non trouvé.")

    def supprimer_utilisateur(self):
        # Récupérer l'utilisateur sélectionné dans la liste
        utilisateur_item = self.utilisateurs_list.currentItem()
        if not utilisateur_item:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un utilisateur à supprimer.")
            return

        # Extraire l'ID de l'utilisateur
        utilisateur_info = utilisateur_item.text()
        id = int(utilisateur_info.split("ID: ")[1].split(",")[0])

        # Trouver l'objet Utilisateur correspondant à l'ID
        utilisateur_trouve = None
        for utilisateur in utilisateurs.lister():
            if utilisateur.id == id:
                utilisateur_trouve = utilisateur
                break

        if utilisateur_trouve:
            # Supprimer l'utilisateur
            if utilisateurs.supprimer_utilisateur(id):
                # Empiler l'objet Utilisateur complet dans l'historique
                empiler_historique("suppression_utilisateur", utilisateur_trouve,
                                   f"Suppression de l'utilisateur : ID {id}")
                self.update_utilisateurs_list()  # Mettre à jour la liste des utilisateurs
                self.update_historique_list()  # Mettre à jour l'historique
                QMessageBox.information(self, "Succès", f"Utilisateur avec l'ID {id} supprimé avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "La suppression a échoué.")
        else:
            QMessageBox.warning(self, "Erreur", "Utilisateur non trouvé.")


    def annuler_derniere_action(self):
        if historique.est_vide():
            QMessageBox.warning(self, "Erreur", "Aucune action à annuler.")
        else:
            type_action, donnees, message = historique.depiler()
            if type_action == "ajout_livre":
                bibliotheque.supprimer_livre(donnees.titre)
                QMessageBox.information(self, "Annulation", f"Livre '{donnees.titre}' supprimé.")
            elif type_action == "suppression_livre":
                bibliotheque.ajouter(donnees)
                QMessageBox.information(self, "Annulation", f"Livre '{donnees.titre}' réajouté.")
            elif type_action == "ajout_utilisateur":
                utilisateurs.supprimer_utilisateur(donnees.id)
                QMessageBox.information(self, "Annulation", f"Utilisateur '{donnees.nom}' supprimé.")
            elif type_action == "suppression_utilisateur":
                utilisateurs.ajouter(donnees)
                QMessageBox.information(self, "Annulation", f"Utilisateur '{donnees.nom}' réajouté.")
            elif type_action == "emprunt_livre":
                donnees.emprunte = False
                QMessageBox.information(self, "Annulation", f"Livre '{donnees.titre}' retourné.")
            elif type_action == "retour_livre":
                donnees.emprunte = True
                QMessageBox.information(self, "Annulation", f"Livre '{donnees.titre}' réemprunté.")
            else:
                QMessageBox.warning(self, "Erreur", "Type d'action non reconnu.")

            self.update_livres_list()
            self.update_utilisateurs_list()
            self.update_historique_list()

    def afficher_livres_disponibles(self):
        self.livres_list.clear()
        livres = []
        _parcourir_arbre(bibliotheque.racine, livres)
        for livre in livres:
            if not livre.emprunte:
                self.livres_list.addItem(f"{str(livre)} - Disponible")
            else:
                self.livres_list.addItem(f"{livre} - Emprunté")

    def update_livres_list(self):
        self.livres_list.clear()
        livres = []
        _parcourir_arbre(bibliotheque.racine, livres)
        for livre in livres:
            self.livres_list.addItem(str(livre))

    def update_utilisateurs_list(self):
        self.utilisateurs_list.clear()
        for utilisateur in utilisateurs.lister():
            self.utilisateurs_list.addItem(str(utilisateur))

    def update_historique_list(self):
        self.historique_list.clear()
        # Afficher les éléments en ordre inverse (dernier en premier)
        for action, _, message in reversed(historique.elements):
            self.historique_list.addItem(message)

def _parcourir_arbre(noeud, livres):
    if noeud is not None:
        livres.append(noeud.livre)
        _parcourir_arbre(noeud.gauche, livres)
        _parcourir_arbre(noeud.droit, livres)

def empiler_historique(type_action, donnees, message=None):
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message is None:
        message = f"{type_action} : {donnees}"
    historique.empiler((type_action, donnees, f"{maintenant} : {message}"))


# Lancement de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliothequeApp()
    window.show()
    sys.exit(app.exec())