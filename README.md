# 📜 HistoiRik  
HistoiRik est une application qui génère des histoires personnalisées pour enfants à partir des préférences de l’utilisateur : prénom, âge, univers, durée, ton, etc.

L’histoire est ensuite racontée à voix haute grâce à un moteur TTS (Text-To-Speech) fonctionnant en local, puis affichée et sauvegardée sur la machine de l’utilisateur.

## 🎯 Objectif du projet

HistoiRik est un **Proof of Concept (PoC)** qui démontre comment :
- Déployer et interagir avec un modèle d’IA open-source localement  
- Intégrer une synthèse vocale sans connexion Internet   
- Mesurer la consommation énergétique réelle en local  

---

## 🧩 Fonctionnalités

• **Génération d’histoires locales**
- Utilisation d’Ollama + Mistral  
- Paramètres : prénom, âge, genre, ton, longueur, décor  

• **Lecture vocale (TTS local)**
- Synthèse vocale via `pyttsx3`  
- Choix de la voix, de la vitesse et du volume  

• **Interface simple**
- Choix des paramètres  
- Bouton “Générer”, “Lire à voix haute”, “Sauvegarder”  

• **Sauvegarde locale**
- Les histoires sont enregistrées en `.txt` ou `.pdf`  
- Un fichier `favoris.json` permet de garder les meilleures histoires  

• **Mode hors-ligne complet**
- Aucune API externe ni connexion Internet requise  

---

## 🧱 Structure du projet

| Module | Fichier | Description |
|--------|----------|-------------|
| 🧠 Génération d’histoire | `generateStory.py` | Utilise Ollama + Mistral pour créer l’histoire |
| 🗣️ Lecture vocale | `tts.py` | Lecture locale de l’histoire via pyttsx3 |
| 💻 Interface | `ui.py` (ou `app.py`) | Interface locale (Tkinter / Flask / Streamlit) |
| 💾 Sauvegarde | `utils.py` | Sauvegarde en .txt/.pdf et gestion des favoris |
| ⚙️ Lancement | `main.py` | Point d’entrée du projet |
| 📚 Données | `stories/` | Contient les histoires générées |
| ⭐ Favoris | `favoris.json` | Stocke les histoires marquées comme favorites |

---

## 🧠 Technologies utilisées

| Technologie | Rôle | Justification |
|--------------|------|----------------|
| **Python 3.11+** | Langage principal | Simple, portable, rapide à prototyper |
| **Ollama** | Exécution du modèle local | Permet de lancer Mistral localement |
| **Mistral 7B** | Modèle de génération de texte | Léger, open-source, efficace pour le texte |
| **pyttsx3** | Text-to-Speech local | Fonctionne sans Internet, multiplateforme |
| **Tkinter / Flask / Streamlit** | Interface utilisateur | Simple, intuitive, adaptée à un PoC |
| **psutil** | Mesure énergétique | Pour comparer la consommation locale |
| **Git** | Versioning & collaboration | Travail d’équipe fluide et clair |

---

## ⚙️ Installation & Lancement

### 🧱 Prérequis

Avant de commencer, assurez-vous d’avoir installer :

- Python 3.11
- Ollama ([https://ollama.ai](https://ollama.ai))  
- Le modèle Mistral téléchargé localement  

```bash
# Installation d’Ollama (macOS / Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Sur Windows, téléchargez le setup :
# https://ollama.ai/download

# Télécharger le modèle Mistral
ollama pull mistral

# StoryGenerator
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
