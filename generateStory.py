import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import threading


def generate_story(prenom, age, style, duree, output_box, button):
    button.config(state="disabled")
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Génération de l’histoire en cours...\n")

    def task():
        prompt = f"""
        Crée une histoire pour un enfant nommé {prenom}, âgé de {age} ans.
        Le style est {style}.
        La lecture de l'histoire doit durer environ {duree} minutes et être adaptée à un jeune public.
        Garde un ton positif et imaginatif.
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


def main():
    root = tk.Tk()
    root.title("Générateur d'histoires")
    root.geometry("600x500")
    root.resizable(False, False)

 
    style = ttk.Style()
    style.theme_use('clam')  

    
    bg_window = "#F0F8FF"  
    bg_frame = "#D6F0FF"   
    btn_color = "#FFB347"  
    btn_hover = "#FFCC80"  
    label_color = "#333333" 
    text_bg = "#FFFFFF"     
    text_fg = "#1F3A93"    


    root.configure(bg=bg_window)

    
    style.configure("TFrame", background=bg_frame, borderwidth=0, relief="flat")
    style.configure("TLabel", background=bg_frame, font=("Comic Sans MS", 12), foreground=label_color)

    
    style.configure("TButton",
                    font=("Comic Sans MS", 12, "bold"),
                    background=btn_color,
                    foreground="white",
                    padding=8,
                    relief="raised")
    style.map("TButton",
              background=[('active', btn_hover)],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])


    style.configure("TCombobox",
                    font=("Comic Sans MS", 12),
                    padding=5)

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Prénom de l'enfant :").grid(row=0, column=0, sticky="w")
    prenom_entry = ttk.Entry(frame, width=30, font=("Comic Sans MS", 12))
    prenom_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Âge :").grid(row=1, column=0, sticky="w")
    age_spin = ttk.Spinbox(frame, from_=2, to=15, width=5, font=("Comic Sans MS", 12))
    age_spin.grid(row=1, column=1, pady=5, sticky="w")

    ttk.Label(frame, text="Style d'histoire :").grid(row=2, column=0, sticky="w")
    genre = [
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
    style_var = tk.StringVar(value=genre[0])
    style_menu = ttk.Combobox(frame, textvariable=style_var, values=genre, state="readonly", width=27)
    style_menu.grid(row=2, column=1, pady=5, sticky="w")

    ttk.Label(frame, text="Durée (en minutes) :").grid(row=3, column=0, sticky="w")
    duree_spin = ttk.Spinbox(frame, from_=1, to=20, width=5, font=("Comic Sans MS", 12))
    duree_spin.grid(row=3, column=1, pady=5, sticky="w")

    output_box = tk.Text(frame, wrap="word", height=15,
                         bg=text_bg, fg=text_fg, font=("Comic Sans MS", 12), relief="solid", bd=2)
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

    root.mainloop()


if __name__ == "__main__":
    main()
