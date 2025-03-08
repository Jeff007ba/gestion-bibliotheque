class Utilisateur:
    def __init__(self, nom, id, email):
        self.nom = nom
        self.id = id
        self.email = email

    def __str__(self):
        return f"{self.nom} (ID: {self.id}, Email: {self.email})"