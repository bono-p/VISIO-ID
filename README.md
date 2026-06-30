# 👁 VISIO·ID — Identify what you see

> Logiciel de reconnaissance faciale en temps réel avec interface graphique moderne.
> Webcam · Caméra IP · Vidéo · Photo

---

## 📋 Table des matières

1. [Présentation](#-présentation)
2. [Architecture du projet](#-architecture-du-projet)
3. [Prérequis système](#-prérequis-système)
4. [Installation étape par étape](#-installation-étape-par-étape)
5. [Lancement de l'application](#-lancement-de-lapplication)
6. [Guide d'utilisation](#-guide-dutilisation)
7. [Compilation avec PyInstaller](#-compilation-avec-pyinstaller)
8. [Comprendre le code](#-comprendre-le-code)
9. [Dépannage](#-dépannage)
10. [Paramètres avancés](#-paramètres-avancés)

---

## 🎯 Présentation

**VISIO·ID** est un logiciel de reconnaissance faciale desktop développé en Python.
Il permet de :

- 📷 Reconnaître des visages en **temps réel** via webcam ou caméra IP (IP Webcam)
- 🎬 Analyser des **fichiers vidéo** avec annotations
- 🖼 Analyser des **photos statiques**
- 👥 Gérer une **base de profils** avec photos multiples par personne
- 💾 Stocker les données localement en **SQLite** (portable, aucun serveur)

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Interface | CustomTkinter (thème sombre) |
| Reconnaissance | face_recognition (dlib) |
| Capture vidéo | OpenCV |
| Base de données | SQLite3 |
| Sérialisation | NumPy + Pickle |

---

## 📁 Architecture du projet

```
VISIO_ID/
│
├── main.py                        # ▶ Point d'entrée — lancer ici
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py              # CRUD SQLite (personnes + encodages)
│   └── face_recog.db              # Base SQLite (auto-générée au premier lancement)
│
├── core/
│   ├── __init__.py
│   ├── encoder.py                 # Calcul des encodages faciaux (face_recognition)
│   ├── recognizer.py              # Moteur de reconnaissance temps réel (thread)
│   └── video_processor.py        # Traitement photo/vidéo statique
│
├── ui/
│   ├── __init__.py
│   ├── app.py                     # Fenêtre principale + navigation
│   ├── theme.py                   # Palette couleurs, polices, constantes UI
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                # Page flux vidéo + sidebar détections
│   │   ├── gallery.py             # Page galerie des profils
│   │   └── add_person.py          # Page ajout d'une personne
│   └── components/
│       ├── __init__.py
│       ├── video_frame.py         # Widget affichage flux vidéo annoté
│       └── profile_card.py        # Carte d'un profil dans la galerie
│
├── assets/
│   └── photos/                    # Photos stockées par personne (auto-créé)
│       ├── 1/                     # Photos de la personne id=1
│       ├── 2/
│       └── ...
│
├── requirements.txt               # Dépendances Python
└── README.md                      # Ce fichier
```

---

## 💻 Prérequis système

- **OS** : Windows 10 / 11 (testé et recommandé)
- **Python** : 3.9, 3.10 ou 3.11 (**⚠ Python 3.12 non supporté par dlib**)
- **RAM** : 4 Go minimum (8 Go recommandé)
- **Webcam** : toute webcam USB ou intégrée
- **CMake** : requis pour compiler dlib (voir ci-dessous)

> ⚠️ **Important** : `face_recognition` utilise `dlib` qui nécessite une compilation C++.
> Suivez l'installation dans l'ordre exact ci-dessous.

---

## 🔧 Installation étape par étape

### Étape 1 — Vérifier la version de Python

```bash
python --version
```

Vous devez voir `Python 3.9.x`, `3.10.x` ou `3.11.x`.

Si vous avez Python 3.12+, installez Python 3.11 depuis [python.org](https://www.python.org/downloads/release/python-3119/)
et utilisez `py -3.11` à la place de `python` dans les commandes suivantes.

---

### Étape 2 — Créer un environnement virtuel

```bash
# Dans le dossier VISIO_ID/
python -m venv venv

# Activer l'environnement virtuel
# Windows :
venv\Scripts\activate

# Le prompt doit afficher (venv) devant la ligne
```

---

### Étape 3 — Installer CMake (requis pour dlib)

Téléchargez et installez CMake depuis : https://cmake.org/download/

Choisissez l'installateur Windows x64 (.msi).
**Cochez "Add CMake to system PATH"** pendant l'installation.

Vérifiez :
```bash
cmake --version
```

---

### Étape 4 — Installer Visual Studio Build Tools (requis pour dlib)

dlib nécessite un compilateur C++.

1. Téléchargez **Visual Studio Build Tools** : https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/
2. Dans l'installateur, cochez **"Développement Desktop en C++"**
3. Installez (environ 3-5 Go)

---

### Étape 5 — Installer dlib

```bash
# Méthode recommandée : wheel précompilé (évite la compilation)
pip install dlib

# Si ça échoue, essayez avec un wheel précompilé pour votre version Python :
# Téléchargez le .whl correspondant sur : https://github.com/z-mahmud22/Dlib_Windows_Python3.x
# Puis : pip install dlib-19.24.x-cp311-cp311-win_amd64.whl
```

---

### Étape 6 — Installer toutes les dépendances

```bash
pip install -r requirements.txt
```

Cela installe :
- `customtkinter` — interface graphique
- `Pillow` — traitement d'images
- `opencv-python` — capture vidéo
- `face_recognition` — reconnaissance faciale
- `numpy` — calcul numérique
- `CTkMessagebox` — boîtes de dialogue modernes
- `requests` — utilitaire réseau

---

### Étape 7 — Vérifier l'installation

```bash
python -c "import face_recognition; print('face_recognition OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import customtkinter; print('CustomTkinter OK')"
```

Les trois lignes doivent afficher `OK`.

---

## ▶ Lancement de l'application

```bash
# Depuis le dossier VISIO_ID/, avec le venv activé :
python main.py
```

Au premier lancement, la base de données `database/face_recog.db` est créée automatiquement.

---

## 📖 Guide d'utilisation

### 1. Ajouter des personnes (onglet ➕ Ajouter)

1. Entrez le **prénom** et le **nom**
2. Cliquez **"Sélectionner des photos"** et choisissez une ou plusieurs photos
   - ✅ **Recommandé** : 5 à 10 photos par personne (angles variés, éclairages différents)
   - ⚠️ **Minimum** : 1 photo (précision réduite)
   - 📌 Chaque photo doit contenir **exactement 1 visage**
3. Cliquez **"Enregistrer le profil"**
4. VISIO·ID encode chaque photo et affiche les résultats (✓ ou ✗ par photo)

### 2. Voir les profils (onglet 👥 Galerie)

- Toutes les personnes enregistrées s'affichent en grille
- **Modifier** (✏) : changer le prénom/nom
- **Supprimer** (🗑) : supprimer la personne et toutes ses photos
- **Rafraîchir** (↻) : recharger depuis la base

### 3. Lancer la reconnaissance (onglet 🎬 Accueil)

#### Webcam
1. Sélectionnez **"Webcam"** dans le menu Source
2. Cliquez **▶ Démarrer**
3. Les personnes reconnues apparaissent avec un rectangle violet et leur nom

#### Caméra IP (smartphone)
1. Sur votre téléphone, installez **IP Webcam** (Android) ou **EpocCam** (iPhone)
2. Démarrez le serveur dans l'app — notez l'URL affichée (ex: `http://192.168.1.42:8080/video`)
3. Dans VISIO·ID, sélectionnez **"IP Webcam"**
4. Entrez l'URL complète dans le champ
5. Cliquez **▶ Démarrer**

> ⚠️ Votre PC et votre téléphone doivent être sur le **même réseau Wi-Fi**

#### Fichier vidéo
1. Sélectionnez **"Fichier vidéo"**
2. Cliquez **📁 Parcourir** et choisissez votre fichier (.mp4, .avi, .mov...)
3. Cliquez **▶ Démarrer** — la vidéo défile avec les annotations

#### Photo statique
1. Sélectionnez **"Photo"**
2. Cliquez **📁 Parcourir** et choisissez une image
3. Cliquez **▶ Démarrer** — le résultat s'affiche immédiatement

---

## 📦 Compilation avec PyInstaller

Pour créer un `.exe` autonome (sans Python installé) :

### Étape 1 — Installer PyInstaller

```bash
pip install pyinstaller
```

### Étape 2 — Compiler

```bash
pyinstaller --onefile --windowed ^
  --add-data "assets;assets" ^
  --add-data "database;database" ^
  --hidden-import "face_recognition" ^
  --hidden-import "dlib" ^
  --hidden-import "cv2" ^
  --name "VISIO-ID" ^
  main.py
```

> La commande `^` permet de couper une longue ligne dans CMD Windows.

### Étape 3 — Récupérer l'exécutable

Le fichier `VISIO-ID.exe` se trouve dans `dist/VISIO-ID.exe`.

### Étape 4 — Distribuer

Pour partager l'application, copiez :
```
dist/
└── VISIO-ID.exe   ← l'exécutable
database/          ← créé automatiquement au premier lancement
assets/            ← dossier des photos
```

> ⚠️ La base SQLite `face_recog.db` et les photos sont dans ces dossiers.
> Ne les supprimez pas si vous voulez conserver vos profils.

---

## 🧠 Comprendre le code

### Comment fonctionne la reconnaissance ?

```
Photo (référence)
       │
       ▼
face_recognition.face_encodings()
       │
       ▼ Vecteur de 128 nombres (float64)
       │   ex: [0.12, -0.34, 0.87, ...]
       │
       └─→ Stocké en BLOB dans SQLite

Au lancement :
       │
       ▼ Chargement en RAM (tous les encodages)
       │
  Frame vidéo
       │
       ▼ face_recognition.face_locations() → positions des visages
       │
       ▼ face_recognition.face_encodings() → encodages des visages détectés
       │
       ▼ face_recognition.face_distance()  → distances avec les encodages connus
       │
       ▼ Seuil (TOLERANCE = 0.50)
       │
       └─→ Nom affiché si distance < seuil
```

### Pourquoi un thread séparé ?

L'analyse d'une frame prend 200 à 800ms sur CPU.
Si on fait ça dans le thread UI (Tkinter), l'interface se fige.
On utilise donc `threading.Thread` pour la reconnaissance
et `self.after(0, callback)` pour mettre à jour l'UI depuis le thread principal.

### Pourquoi 1 frame sur N ?

Analyser chaque frame serait trop lent.
On analyse 1 frame sur `PROCESS_EVERY_N_FRAMES` (valeur par défaut : 3)
et on affiche le dernier résultat connu sur les frames intermédiaires.
Cela donne un affichage fluide même sur CPU lent.

---

## 🔨 Dépannage

### ❌ `ModuleNotFoundError: No module named 'dlib'`

dlib n'est pas installé. Suivez l'Étape 5 de l'installation.

### ❌ `No module named 'face_recognition'`

```bash
pip install face_recognition
```

### ❌ `Error: Couldn't connect to camera`

- Vérifiez que la webcam est branchée et non utilisée par une autre app
- Essayez de changer l'index : dans `home.py`, ligne `self._source = 0`, essayez `1` ou `2`

### ❌ L'IP Webcam ne se connecte pas

- Vérifiez que le téléphone et le PC sont sur le **même réseau Wi-Fi**
- Vérifiez l'URL exacte affichée dans l'app IP Webcam
- Essayez l'URL dans votre navigateur — vous devez voir le flux vidéo

### ❌ `face_recognition` est très lent

C'est normal sur Intel HD Graphics 620 (pas de CUDA).
Solutions :
1. Augmentez `PROCESS_EVERY_N_FRAMES` dans `core/recognizer.py` (ex: 5 ou 6)
2. Diminuez `FRAME_SCALE` (ex: 0.25 au lieu de 0.5)

### ❌ Erreur lors de l'encodage d'une photo

- La photo doit contenir **exactement 1 visage visible**
- Évitez les photos floues, trop petites, ou avec un visage de profil
- Recommandé : photo de face, bonne luminosité, 200×200 px minimum

### ❌ La personne n'est pas reconnue

- Ajoutez plus de photos (angles différents, éclairages variés)
- Diminuez la `TOLERANCE` dans `core/recognizer.py` (ex: 0.45)
- Vérifiez que la luminosité du flux vidéo est suffisante

---

## ⚙️ Paramètres avancés

Tous les paramètres de performance sont dans `core/recognizer.py` :

```python
PROCESS_EVERY_N_FRAMES = 3    # Analyser 1 frame sur N
                               # ↑ augmenter = plus rapide, moins précis

FRAME_SCALE = 0.5             # Réduction de la frame (0.25 = 4x plus rapide)
                               # ↓ diminuer = plus rapide, moins précis

TOLERANCE = 0.50              # Seuil de reconnaissance
                               # ↓ diminuer = plus strict (moins de faux positifs)
                               # ↑ augmenter = plus permissif (plus de détections)
```

La palette de couleurs et les dimensions de l'UI sont dans `ui/theme.py`.

---

## 📄 Licence

Projet académique et personnel — libre d'utilisation.

---

*VISIO·ID — Développé avec Python, face_recognition et CustomTkinter*
