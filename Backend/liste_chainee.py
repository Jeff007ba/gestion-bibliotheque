class NoeudListe:
    def __init__(self, valeur):
        self.valeur = valeur
        self.suivant = None

class ListeChainee:
    def __init__(self):
        self.tete = None

    def ajouter(self, valeur):
        nouveau_noeud = NoeudListe(valeur)
        if self.tete is None:
            self.tete = nouveau_noeud
        else:
            courant = self.tete
            while courant.suivant:
                courant = courant.suivant
            courant.suivant = nouveau_noeud

    def lister(self):
        elements = []
        courant = self.tete
        while courant:
            elements.append(courant.valeur)
            courant = courant.suivant
        return elements

    def supprimer_utilisateur(self, id):
        courant = self.tete
        precedent = None

        # Parcourir la liste pour trouver l'utilisateur
        while courant is not None:
            if courant.valeur.id == id:
                if precedent is None:
                    self.tete = courant.suivant
                else:
                    precedent.suivant = courant.suivant
                return True
            precedent = courant
            courant = courant.suivant

        return False