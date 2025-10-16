import os
import json
from datetime import datetime

class SaveManager:
    def __init__(self, dossier="histoires", fichier_favoris="favoris.json"):
        self.dossier = dossier
        self.fichier_favoris = fichier_favoris

        os.makedirs(self.dossier, exist_ok=True)

        if not os.path.exists(self.fichier_favoris):
            with open(self.fichier_favoris, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def sauvegarder_histoire(self, titre, contenu, auteur=None, genre=None):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nom_fichier = f"{titre.replace(' ', '_')}_{int(datetime.now().timestamp())}.txt"
        chemin = os.path.join(self.dossier, nom_fichier)

        metadata = f"Titre : {titre}\nAuteur : {auteur or 'Anonyme'}\nGenre : {genre or 'Non précisé'}\nDate : {date}\n\n"
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(metadata + contenu.strip())

        print(f"Histoire sauvegardée : {chemin}")
        return chemin

    def lister_histoires(self):
        fichiers = sorted(os.listdir(self.dossier))
        return [os.path.splitext(f)[0] for f in fichiers]

    def lire_histoire(self, nom):
        chemin = os.path.join(self.dossier, nom + ".txt")
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Histoire {nom} introuvable")
        with open(chemin, "r", encoding="utf-8") as f:
            return f.read()

    def ajouter_favori(self, nom):
        favoris = self._charger_favoris()
        if nom not in favoris:
            favoris.append(nom)
            self._sauvegarder_favoris(favoris)
            print(f"Ajouté aux favoris : {nom}")
        else:
            print(f"{nom} est déjà dans les favoris")

    def retirer_favori(self, nom):
        favoris = self._charger_favoris()
        if nom in favoris:
            favoris.remove(nom)
            self._sauvegarder_favoris(favoris)
            print(f"Retiré des favoris : {nom}")

    def lister_favoris(self):
        return self._charger_favoris()

    def _charger_favoris(self):
        with open(self.fichier_favoris, "r", encoding="utf-8") as f:
            return json.load(f)

    def _sauvegarder_favoris(self, data):
        with open(self.fichier_favoris, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
