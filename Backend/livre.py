from datetime import datetime

class Livre:
    def __init__(self, isbn, titre, auteur, annee, categorie):
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.categorie = categorie
        self.emprunte = False
        self.date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"{self.titre} par {self.auteur} ({self.annee}) - Ajouté le {self.date_ajout}"