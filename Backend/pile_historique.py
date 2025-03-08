class Pile:
    def __init__(self):
        self.elements = []

    def empiler(self, element):
        self.elements.append(element)

    def depiler(self):
        if not self.est_vide():
            return self.elements.pop()
        return None

    def est_vide(self):
        return len(self.elements) == 0

    def sommet(self):
        if not self.est_vide():
            return self.elements[-1]
        return None