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
| 🗣️ Lecture vocale | `readStory.py` | Lecture locale de l’histoire via pyttsx3 |
| 💻 Interface | `generateStory.py` | Interface locale (Tkinter / Flask / Streamlit) |
| 💾 Sauvegarde | `save_manager.py` | Sauvegarde en .txt/.pdf et gestion des favoris |
| ⚙️ Lancement | `generateStory.py` | Point d’entrée du projet |
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

# Installation de espeak :
sudo apt install espeak
```

# Impact énergétique de l’application

## Méthodologie de mesure

Basé sur psutil,  **energyMonitor.py** estime l’énergie CPU consommée pendant l’utilisation de l’application.

### Principe

- À chaque pas de 1 s, on relève `cpu_percent()` et on approxime la puissance instantanée du package CPU par :  
  `P(t) ≈ (CPU% / 100) × TDP`  
  _(TDP paramétrable, 28 W par défaut)_

- L’énergie totale sur l’intervalle :  
  `E_total += P(t) × Δt`  
  (en J, puis convertie en Wh).

- Répartition de l’énergie entre processus selon leur part de **temps CPU actif** (utilisateur + système).

- En fin d’exécution, le script affiche l’**énergie CPU totale** et l’**énergie attribuée à chaque processus**.

> ⚠️ **Approximation CPU-only** : GPU/NPU, DRAM, stockage, écran, réseau, etc. ne sont pas comptés.  
> Le TDP sert d’hypothèse de puissance, pas d’une mesure capteur.

---

## Protocole

1. Lancer l’application et la/les tâche(s) représentatives.  
2. Identifier les **PID** des deux cibles (notre app + un comparatif léger, ex. éditeur de texte).  
3. Exécuter la commande suivante :  

   ```bash
   python energyMonitor.py
   # saisir : PID de l'app, puis "Nom PID" du comparatif, puis la durée (ex. 60 s)
   ```

---

## Pourquoi 28 W ?

- **Valeur réaliste pour portables actuels** : beaucoup de CPU mobiles (Intel/AMD séries U/H basse consommation) opèrent avec un **PL1/TDP nominal entre ~15 et 30 W**.  
  **28 W** se situe au milieu de cette plage et évite une sous-estimation (15 W) ou une surestimation (45 W) trop marquées pour un laptop « standard ».

- **Paramétrable** : le script accepte `tdp_watts` — si votre machine a un TDP différent  
  (ex. **15 W** pour un ultra-portable, **45 W** pour une workstation), remplacez **28** par la valeur réelle  
  _(fiche technique constructeur ou outil système)_.

- **Recalage simple** : si vous découvrez votre TDP exact a posteriori, **multipliez l’énergie rapportée par**  
  `(TDP_réel / 28)`.  
  Exemple : résultats × (15/28) pour un CPU 15 W, ou × (45/28) pour 45 W.

> Pour une mesure plus précise, utilisez quand c’est possible des **compteurs matériels**  
> (`RAPL` / `intel_rapl`, `amd_energy`, `HWMON`) ou un **wattmètre externe**.  
> Notre approche reste une **estimation légère et reproductible**, idéale pour comparer plusieurs scénarios entre eux.
