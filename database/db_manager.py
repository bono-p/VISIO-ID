"""
─────────────────────────────────────────────────────────────────
VISIO·ID — database/db_manager.py
─────────────────────────────────────────────────────────────────
Rôle : Gérer toutes les opérations SQLite (CRUD).
       Création des tables, ajout/suppression de personnes,
       sauvegarde et chargement des encodages faciaux.

Tables :
  - persons        : identité (prénom, nom, date d'ajout)
  - face_encodings : encodages numpy sérialisés par photo
─────────────────────────────────────────────────────────────────
"""

import sqlite3
import pickle
import os
import numpy as np
from datetime import datetime


# ── Chemin vers la base de données (à côté de ce fichier) ─────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_recog.db")


def get_connection():
    """
    Crée et retourne une connexion SQLite.
    check_same_thread=False permet l'accès depuis plusieurs threads
    (nécessaire pour le thread de reconnaissance vidéo).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Les résultats sont accessibles par nom de colonne
    return conn


def initialize_database():
    """
    Crée les tables si elles n'existent pas encore.
    Appelé une seule fois au démarrage de l'application.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Table des personnes ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT    NOT NULL,
            last_name  TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )
    """)

    # ── Table des encodages faciaux ────────────────────────────────
    # Un encodage = un vecteur numpy de 128 dimensions, sérialisé en BLOB
    # Une personne peut avoir plusieurs encodages (plusieurs photos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_encodings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id  INTEGER NOT NULL,
            encoding   BLOB    NOT NULL,
            photo_path TEXT    NOT NULL,
            FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Base de données initialisée.")


# ══════════════════════════════════════════════════════════════════
#  CRUD — Personnes
# ══════════════════════════════════════════════════════════════════

def add_person(first_name: str, last_name: str) -> int:
    """
    Ajoute une nouvelle personne dans la base.
    Retourne l'ID auto-généré de la personne.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO persons (first_name, last_name, created_at) VALUES (?, ?, ?)",
        (first_name.strip(), last_name.strip(), datetime.now().isoformat())
    )
    person_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"[DB] Personne ajoutée → ID={person_id} | {first_name} {last_name}")
    return person_id


def get_all_persons() -> list:
    """
    Retourne la liste de toutes les personnes enregistrées.
    Chaque élément est un dict-like sqlite3.Row :
    { id, first_name, last_name, created_at }
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons ORDER BY last_name, first_name")
    persons = cursor.fetchall()
    conn.close()
    return persons


def get_person_by_id(person_id: int):
    """Retourne une personne par son ID, ou None si introuvable."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    person = cursor.fetchone()
    conn.close()
    return person


def update_person(person_id: int, first_name: str, last_name: str):
    """Met à jour le prénom et nom d'une personne existante."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE persons SET first_name = ?, last_name = ? WHERE id = ?",
        (first_name.strip(), last_name.strip(), person_id)
    )
    conn.commit()
    conn.close()
    print(f"[DB] Personne mise à jour → ID={person_id}")


def delete_person(person_id: int):
    """
    Supprime une personne et TOUS ses encodages (CASCADE).
    Les fichiers photos sur disque ne sont PAS supprimés ici
    (géré séparément dans encoder.py).
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Récupérer les chemins photos avant suppression
    cursor.execute(
        "SELECT photo_path FROM face_encodings WHERE person_id = ?", (person_id,)
    )
    paths = [row["photo_path"] for row in cursor.fetchall()]

    # Suppression (CASCADE supprime aussi les encodages liés)
    cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()

    # Supprimer les fichiers photos du disque
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
            print(f"[DB] Fichier supprimé : {path}")

    print(f"[DB] Personne supprimée → ID={person_id}")


def count_photos_for_person(person_id: int) -> int:
    """Retourne le nombre de photos enregistrées pour une personne."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM face_encodings WHERE person_id = ?", (person_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ══════════════════════════════════════════════════════════════════
#  CRUD — Encodages faciaux
# ══════════════════════════════════════════════════════════════════

def save_encoding(person_id: int, encoding: np.ndarray, photo_path: str):
    """
    Sérialise un encodage numpy (128 valeurs float64) en BLOB
    et le sauvegarde dans la base avec le chemin de la photo source.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # pickle.dumps → convertit le tableau numpy en bytes
    encoding_blob = pickle.dumps(encoding)
    cursor.execute(
        "INSERT INTO face_encodings (person_id, encoding, photo_path) VALUES (?, ?, ?)",
        (person_id, encoding_blob, photo_path)
    )
    conn.commit()
    conn.close()


def load_all_encodings() -> tuple[list, list]:
    """
    Charge TOUS les encodages depuis la base en mémoire RAM.
    Retourne un tuple (encodings, labels) où :
      - encodings : liste de np.ndarray (vecteurs 128D)
      - labels    : liste de str "Prénom NOM" correspondants

    Ces deux listes sont alignées par index :
    encodings[i] correspond à labels[i]
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fe.encoding, p.first_name, p.last_name
        FROM face_encodings fe
        JOIN persons p ON fe.person_id = p.id
    """)
    rows = cursor.fetchall()
    conn.close()

    encodings = []
    labels    = []

    for row in rows:
        # pickle.loads → reconvertit les bytes en tableau numpy
        enc = pickle.loads(row["encoding"])
        encodings.append(enc)
        labels.append(f"{row['first_name']} {row['last_name'].upper()}")

    print(f"[DB] {len(encodings)} encodage(s) chargé(s) en mémoire.")
    return encodings, labels


def get_encodings_for_person(person_id: int) -> list:
    """
    Retourne les encodages d'une personne spécifique.
    Utile pour vérifier ou déboguer un profil.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT encoding FROM face_encodings WHERE person_id = ?", (person_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [pickle.loads(row["encoding"]) for row in rows]
