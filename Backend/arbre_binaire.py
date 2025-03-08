class Noeud:
    def __init__(self, livre):
        self.livre = livre
        self.gauche = None
        self.droit = None

class ArbreBinaire:
    def __init__(self):
        self.racine = None

    def ajouter(self, livre):
        if self.racine is None:
            self.racine = Noeud(livre)
        else:
            self._ajouter_recursif(self.racine, livre)

    def _ajouter_recursif(self, noeud, livre):
        if livre.titre < noeud.livre.titre:
            if noeud.gauche is None:
                noeud.gauche = Noeud(livre)
            else:
                self._ajouter_recursif(noeud.gauche, livre)
        else:
            if noeud.droit is None:
                noeud.droit = Noeud(livre)
            else:
                self._ajouter_recursif(noeud.droit, livre)

    def rechercher_par_titre(self, titre):
        return self._rechercher_recursif(self.racine, titre)

    def _rechercher_recursif(self, noeud, titre):
        if noeud is None or noeud.livre.titre == titre:
            return noeud
        if titre < noeud.livre.titre:
            return self._rechercher_recursif(noeud.gauche, titre)
        return self._rechercher_recursif(noeud.droit, titre)

    def supprimer_livre(self, titre):
        self.racine = self._supprimer_recursif(self.racine, titre)

    def _supprimer_recursif(self, noeud, titre):
        if noeud is None:
            return None
        if titre < noeud.livre.titre:
            noeud.gauche = self._supprimer_recursif(noeud.gauche, titre)
        elif titre > noeud.livre.titre:
            noeud.droit = self._supprimer_recursif(noeud.droit, titre)
        else:
            # Livre trouvé
            if noeud.livre.emprunte:
                print("Impossible de supprimer : le livre est emprunté.")
                return noeud
            # Cas 1 : Pas de fils gauche
            if noeud.gauche is None:
                return noeud.droit
            # Cas 2 : Pas de fils droit
            elif noeud.droit is None:
                return noeud.gauche
            # Cas 3 : Deux fils
            else:
                successeur = self._trouver_min(noeud.droit)
                noeud.livre = successeur.livre
                noeud.droit = self._supprimer_recursif(noeud.droit, successeur.livre.titre)
        return noeud

    def _trouver_min(self, noeud):
        while noeud.gauche is not None:
            noeud = noeud.gauche
        return noeud

    def rechercher_par_auteur(self, auteur):
        resultats = []
        self._rechercher_par_auteur_recursif(self.racine, auteur, resultats)
        return resultats

    def _rechercher_par_auteur_recursif(self, noeud, auteur, resultats):
        if noeud is not None:
            if noeud.livre.auteur == auteur:
                resultats.append(noeud.livre)
            self._rechercher_par_auteur_recursif(noeud.gauche, auteur, resultats)
            self._rechercher_par_auteur_recursif(noeud.droit, auteur, resultats)