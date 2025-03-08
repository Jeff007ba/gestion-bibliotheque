
from livre import Livre
from utilisateur import Utilisateur
from arbre_binaire import ArbreBinaire
from liste_chainee import ListeChainee
from pile_historique import Pile
from datetime import datetime
import json

# Initialisation des structures de données
bibliotheque = ArbreBinaire()
utilisateurs = ListeChainee()
historique = Pile()

def ajouter_livre():
    isbn = input("Entrez l'ISBN du livre : ")
    titre = input("Entrez le titre du livre : ")
    auteur = input("Entrez l'auteur du livre : ")
    annee = int(input("Entrez l'année de publication : "))
    categorie = input("Entrez la catégorie du livre : ")
    livre = Livre(isbn, titre, auteur, annee, categorie)
    bibliotheque.ajouter(livre)
    empiler_historique("ajout_livre", livre, f"Ajout du livre : {titre}")
    print(f"Livre '{titre}' ajouté avec succès !")

def afficher_tous_les_livres():
    print("Liste de tous les livres :")
    livres = []
    _parcourir_arbre(bibliotheque.racine, livres)
    for livre in livres:
        print(livre)

def _parcourir_arbre(noeud, livres):
    if noeud is not None:
        livres.append(noeud.livre)
        _parcourir_arbre(noeud.gauche, livres)
        _parcourir_arbre(noeud.droit, livres)

def rechercher_livre():
    titre = input("Entrez le titre du livre à rechercher : ")
    resultat = bibliotheque.rechercher_par_titre(titre)
    if resultat:
        print(f"Livre trouvé : {resultat.livre}")
        empiler_historique(f"Recherche du livre : {titre}", "general")
    else:
        print("Livre non trouvé.")

def ajouter_utilisateur():
    nom = input("Entrez le nom de l'utilisateur : ")
    id = int(input("Entrez l'ID de l'utilisateur : "))
    email = input("Entrez l'email de l'utilisateur : ")

    for utilisateur in utilisateurs.lister():
        if utilisateur.id == id:
            print("❌ Erreur : Cet ID est déjà utilisé par un autre utilisateur.")
            return

    utilisateur = Utilisateur(nom, id, email)
    utilisateurs.ajouter(utilisateur)
    empiler_historique("ajout_utilisateur", utilisateur, f"Ajout de l'utilisateur : {nom} (ID: {id})")
    print(f"Utilisateur '{nom}' ajouté avec succès !")

def emprunter_livre():
    titre = input("Entrez le titre du livre à emprunter : ")
    livre_trouve = bibliotheque.rechercher_par_titre(titre)
    if livre_trouve:
        if livre_trouve.livre.emprunte:
            print("❌ Erreur : Le livre est déjà emprunté.")
        else:
            id_utilisateur = int(input("Entrez l'ID de l'utilisateur : "))
            utilisateur_trouve = None
            for utilisateur in utilisateurs.lister():
                if utilisateur.id == id_utilisateur:
                    utilisateur_trouve = utilisateur
                    break
            if utilisateur_trouve:
                livre_trouve.livre.emprunte = True
                empiler_historique("emprunt_livre", livre_trouve.livre, f"Emprunt : {livre_trouve.livre.titre} par {utilisateur_trouve.nom}")
                print(f"Livre '{livre_trouve.livre.titre}' emprunté par {utilisateur_trouve.nom}.")
            else:
                print("❌ Erreur : Utilisateur non trouvé.")
    else:
        print("❌ Erreur : Livre non trouvé.")

def retourner_livre():
    titre = input("Entrez le titre du livre à retourner : ")
    livre_trouve = bibliotheque.rechercher_par_titre(titre)
    if livre_trouve:
        if livre_trouve.livre.emprunte:
            livre_trouve.livre.emprunte = False
            empiler_historique("retour_livre", livre_trouve.livre, f"Retour : {livre_trouve.livre.titre}")
            print(f"Livre '{livre_trouve.livre.titre}' retourné avec succès.")
        else:
            print("❌ Erreur : Le livre n'est pas emprunté.")
    else:
        print("❌ Erreur : Livre non trouvé.")

def afficher_historique():
    print("Historique des actions :")
    for action in historique.elements:
        print(action)

def supprimer_livre():
    titre = input("Entrez le titre du livre à supprimer : ")
    livre_trouve = bibliotheque.rechercher_par_titre(titre)
    if livre_trouve:
        if livre_trouve.livre.emprunte:
            print("❌ Erreur : Impossible de supprimer, le livre est emprunté.")
        else:
            bibliotheque.supprimer_livre(titre)
            empiler_historique("suppression_livre", livre_trouve.livre, f"Suppression du livre : {titre}")
            print(f"Livre '{titre}' supprimé avec succès.")
    else:
        print("❌ Erreur : Livre non trouvé.")

def supprimer_utilisateur():
    id = int(input("Entrez l'ID de l'utilisateur à supprimer : "))

    # Vérifier si l'utilisateur existe avant de le supprimer
    utilisateur_trouve = False
    for utilisateur in utilisateurs.lister():
        if utilisateur.id == id:
            utilisateur_trouve = True
            break

    if utilisateur_trouve:
        # Supprimer l'utilisateur
        if utilisateurs.supprimer_utilisateur(id):
            empiler_historique("suppression_utilisateur", utilisateur_trouve, f"Suppression de l'utilisateur : ID {id}")
            print(f"Utilisateur avec l'ID {id} supprimé avec succès.")
        else:
            print("❌ Erreur : La suppression a échoué.")
    else:
        print("❌ Erreur : Utilisateur non trouvé.")

def rechercher_par_auteur():
    auteur = input("Entrez le nom de l'auteur : ")
    resultats = bibliotheque.rechercher_par_auteur(auteur)
    if resultats:
        print(f"Livres trouvés par {auteur} :")
        for livre in resultats:
            print(livre)
    else:
        print("Aucun livre trouvé pour cet auteur.")

def lister_utilisateurs():
    print("Liste des utilisateurs enregistrés :")
    for utilisateur in utilisateurs.lister():
        print(utilisateur)

def annuler_derniere_action():
    if historique.est_vide():
        print("Aucune action à annuler.")
    else:
        type_action, donnees, message = historique.depiler()
        print(f"Annulation de l'action : {message}")

        if type_action == "ajout_livre":
            # Annuler l'ajout d'un livre : le supprimer
            bibliotheque.supprimer_livre(donnees.titre)
            print(f"Livre '{donnees.titre}' a été supprimé.")
        elif type_action == "suppression_livre":
            # Annuler la suppression d'un livre : le réajouter
            bibliotheque.ajouter(donnees)
            print(f"Livre '{donnees.titre}' a été réajouté.")
        elif type_action == "ajout_utilisateur":
            # Annuler l'ajout d'un utilisateur : le supprimer
            utilisateurs.supprimer_utilisateur(donnees.id)
            print(f"Utilisateur '{donnees.nom}' (ID: {donnees.id}) a été supprimé.")
        elif type_action == "suppression_utilisateur":
            # Annuler la suppression d'un utilisateur : le réajouter
            utilisateurs.ajouter(donnees)
            print(f"Utilisateur '{donnees.nom}' (ID: {donnees.id}) a été réajouté.")
        elif type_action == "emprunt_livre":
            # Annuler l'emprunt d'un livre : le retourner
            donnees.emprunte = False
            print(f"Livre '{donnees.titre}' a été retourné.")
        elif type_action == "retour_livre":
            # Annuler le retour d'un livre : le réemprunter
            donnees.emprunte = True
            print(f"Livre '{donnees.titre}' a été réemprunté.")
        else:
            print("❌ Erreur : Type d'action non reconnu.")

def afficher_livres_disponibles():
    print("Livres disponibles :")
    livres_disponibles = []
    _parcourir_arbre(bibliotheque.racine, livres_disponibles)
    for livre in livres_disponibles:
        if not livre.emprunte:
            print(livre)
        else:
            print(livre, "Non disponible ! [Emprunt]")

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

def menu():
    print("\n--- Gestion de la Bibliothèque Numérique ---")
    print("1. Ajouter un livre")
    print("2. Rechercher un livre par titre")
    print("3. Rechercher un livre par auteur")
    print("4. Supprimer un livre")
    print("5. Ajouter un utilisateur")
    print("6. Lister tous les utilisateurs")
    print("7. Supprimer un utilisateur")
    print("8. Emprunter un livre")
    print("9. Retourner un livre")
    print("10. Afficher l'historique")
    print("11. Afficher tous les livres")
    print("12. Annuler la dernière action")
    print("13. Quitter")
    choix = input("Choisissez une option : ")
    return choix

# Boucle principale du programme
while True:
    choix = menu()
    if choix == "1":
        ajouter_livre()
    elif choix == "2":
        rechercher_livre()
    elif choix == "3":
        rechercher_par_auteur()
    elif choix == "4":
        supprimer_livre()
    elif choix == "5":
        ajouter_utilisateur()
    elif choix == "6":
        lister_utilisateurs()
    elif choix == "7":
        supprimer_utilisateur()
    elif choix == "8":
        emprunter_livre()
    elif choix == "9":
        retourner_livre()
    elif choix == "10":
        afficher_historique()
    elif choix == "11":
        afficher_livres_disponibles()
    elif choix == "12":
        annuler_derniere_action()
    elif choix == "13":
        print("Merci d'avoir utilisé la bibliothèque numérique. À bientôt !")
        break
    else:
        print("Option invalide. Veuillez réessayer.")
