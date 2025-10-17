import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import threading
from readStory import read_story
from save_manager import SaveManager
import os

manager = SaveManager()

def generate_story(prenom, age, style, duree, output_box, button):
    button.config(state="disabled")
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Génération de l’histoire en cours...\n")

    def task():
        prompt = f"""
        Écris une histoire **entièrement en français** pour une personne nommé {prenom}, âgé de {age} ans.
        Le style est {style}.
        L’histoire doit durer environ {duree} minutes.
        Garde un ton positif et imaginatif.
        N'écris rien en anglais.
        """


        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": prompt},
                stream=True,
                timeout=60
            )

            story = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        story += data["response"]
                except json.JSONDecodeError:
                    continue

            output_box.delete(1.0, tk.END)
            output_box.insert(tk.END, story.strip() if story else "Aucune histoire générée.")
        except requests.RequestException as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le serveur : {e}")
        finally:
            button.config(state="normal")

    threading.Thread(target=task, daemon=True).start()

dernier_fichier = None

def sauvegarder_histoire_ui(prenom, age, style, histoire):
    global dernier_fichier
    if not histoire.strip():
        messagebox.showwarning("Attention", "Aucune histoire à sauvegarder !")
        return
    chemin = manager.sauvegarder_histoire(prenom, age, style, histoire)
    # garder uniquement le nom sans dossier et sans extension
    dernier_fichier = os.path.splitext(os.path.basename(chemin))[0]
    messagebox.showinfo("Succès", f"Histoire sauvegardée : {dernier_fichier}")


def voir_histoires_ui():
    histoires = manager.lister_histoires()
    if not histoires:
        messagebox.showinfo("Histoires", "Aucune histoire sauvegardée.")
        return

    fenetre = tk.Toplevel()
    fenetre.title("Histoires sauvegardées")
    fenetre.geometry("500x400")

    for i, h in enumerate(histoires):
        ttk.Label(fenetre, text=h).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        ttk.Button(fenetre, text="Lire", command=lambda nom=h: lire_histoire_ui(nom)).grid(row=i, column=1, padx=5, pady=2)
        ttk.Button(fenetre, text="Retirer", command=lambda nom=h: retirer_histoire_ui(nom, fenetre)).grid(row=i, column=2, padx=5, pady=2)

def lire_histoire_ui(nom):
    texte = manager.lire_histoire(nom)
    fenetre = tk.Toplevel()
    fenetre.title(nom)
    text_box = tk.Text(fenetre, wrap="word")
    text_box.pack(expand=True, fill="both")
    text_box.insert(tk.END, texte)

def retirer_histoire_ui(nom, fenetre):
    # Supprimer le fichier du disque
    chemin = os.path.join(manager.dossier, nom + ".txt")
    if os.path.exists(chemin):
        os.remove(chemin)
        messagebox.showinfo("Histoires", f"Histoire supprimée : {nom}")
    else:
        messagebox.showwarning("Histoires", f"Histoire introuvable : {nom}")

    fenetre.destroy()  # Fermer la fenêtre
    voir_histoires_ui()  # Réouvrir pour mettre à jour la liste



def toggle_favoris_ui(fichier):
    if not fichier or not fichier.strip():
        messagebox.showwarning("Attention", "Aucune histoire à ajouter aux favoris !")
        return
    if fichier in manager.lister_favoris():
        manager.retirer_favori(fichier)
        messagebox.showinfo("Favoris", f"Retiré des favoris : {fichier}")
    else:
        manager.ajouter_favori(fichier)
        messagebox.showinfo("Favoris", f"Ajouté aux favoris : {fichier}")


def voir_favoris_ui():
    favoris = manager.lister_favoris()
    if not favoris:
        messagebox.showinfo("Favoris", "Aucun favori pour le moment.")
        return

    fenetre = tk.Toplevel()
    fenetre.title("Favoris")
    fenetre.geometry("400x300")

    canvas = tk.Canvas(fenetre)
    scrollbar = ttk.Scrollbar(fenetre, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, fav in enumerate(favoris):
        ttk.Label(scrollable_frame, text=fav, wraplength=200).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        ttk.Button(scrollable_frame, text="Lire", command=lambda f=fav: lire_histoire_ui(f)).grid(row=i, column=1, padx=5, pady=2)
        ttk.Button(scrollable_frame, text="Retirer", command=lambda f=fav: retirer_favori_ui(f, fenetre)).grid(row=i, column=2, padx=5, pady=2)


def retirer_favori_ui(fichier, fenetre):
    manager.retirer_favori(fichier)
    messagebox.showinfo("Favoris", f"Favori retiré : {fichier}")
    fenetre.destroy()  # fermer la fenêtre
    voir_favoris_ui()  # rouvrir pour mettre à jour


def main():
    root = tk.Tk()
    root.title("Générateur d'histoires")
    root.geometry("600x500")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Prénom :").grid(row=0, column=0, sticky="w")
    prenom_entry = ttk.Entry(frame, width=30)
    prenom_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Âge :").grid(row=1, column=0, sticky="w")
    age_spin = ttk.Spinbox(frame, from_=2, to=15, width=5)
    age_spin.grid(row=1, column=1, pady=5, sticky="w")

    ttk.Label(frame, text="Style d'histoire :").grid(row=2, column=0, sticky="w")

    # --- Menu déroulant pour le style d’histoire ---
    genres = [
        "Genre de l'histoire : ",
        "magique",
        "aventure",
        "animaux",
        "science-fiction",
        "conte de fées",
        "amitié",
        "mystère",
        "pirates",
        "chevaliers et dragons",
        "voyage fantastique"
    ]
    style_var = tk.StringVar(value=genres[0])
    style_menu = ttk.Combobox(frame, textvariable=style_var, values=genres, state="readonly", width=27)
    style_menu.grid(row=2, column=1, pady=5, sticky="w")

    ttk.Label(frame, text="Durée (en minutes) :").grid(row=3, column=0, sticky="w")
    duree_spin = ttk.Spinbox(frame, from_=1, to=20, width=5)
    duree_spin.grid(row=3, column=1, pady=5, sticky="w")

    output_box = tk.Text(frame, wrap="word", height=15)
    output_box.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")

    frame.rowconfigure(5, weight=1)
    frame.columnconfigure(1, weight=1)

    generate_button = ttk.Button(
        frame,
        text="Générer l'histoire",
        command=lambda: generate_story(
            prenom_entry.get(),
            age_spin.get(),
            style_var.get(),
            duree_spin.get(),
            output_box,
            generate_button
        )
    )
    generate_button.grid(row=4, column=0, columnspan=2, pady=10)

    # --- Bouton pour lire l'histoire ---
    def lire_histoire():
        story = output_box.get("1.0", tk.END).strip()
        if story:
            read_story(story)
    save_button = ttk.Button(
        frame,
        text="Sauvegarder l'histoire",
        command=lambda: sauvegarder_histoire_ui(
            prenom_entry.get(),
            age_spin.get(),
            style_var.get(),
            output_box.get(1.0, tk.END).strip()
        )
    )
    save_button.grid(row=6, column=0, pady=5, sticky="ew")

    voir_histoires_button = ttk.Button(
        frame, 
        text="Voir les histoires", 
        command=voir_histoires_ui
    )
    voir_histoires_button.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

    favoris_button = ttk.Button(
        frame,
        text="Ajouter aux favoris",
        command=lambda: toggle_favoris_ui(dernier_fichier)
        
    )
    favoris_button.grid(row=6, column=1, pady=5, sticky="ew")

    voir_favoris_button = ttk.Button(
        frame,
        text="Voir les favoris",
        command=voir_favoris_ui
    )   
    voir_favoris_button.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")



    root.mainloop()

    lire_button = ttk.Button(
        frame,
        text="Lire l'histoire",
        command=lire_histoire
    )
    lire_button.grid(row=6, column=0, columnspan=2, pady=5)

    lire_button = ttk.Button(
        frame,
        text="Lire l'histoire",
        command=lire_histoire
    )
    lire_button.grid(row=6, column=0, columnspan=2, pady=5)

    # --- Bouton pour arrêter la lecture ---
    def arreter_histoire():
        from readStory import stop_reading
        stop_reading()

    arreter_button = ttk.Button(
        frame,
        text="Arrêter la lecture",
        command=arreter_histoire
    )
    arreter_button.grid(row=7, column=0, columnspan=2, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
