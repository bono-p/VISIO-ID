"""
─────────────────────────────────────────────────────────────────
VISIO·ID — core/encoder.py
─────────────────────────────────────────────────────────────────
Rôle : Calculer les encodages faciaux à partir des photos uploadées
       et les persister en base de données.

Fonctionnement :
  1. On reçoit une image (chemin fichier)
  2. face_recognition détecte le(s) visage(s) dans l'image
  3. Si exactement 1 visage est trouvé → on calcule son encodage
     (vecteur de 128 valeurs float64 = "empreinte faciale")
  4. On copie la photo dans assets/photos/<person_id>/
  5. On sauvegarde l'encodage en base SQLite (BLOB)
─────────────────────────────────────────────────────────────────
"""

import os
import shutil
import face_recognition
import numpy as np
from database.db_manager import save_encoding


# ── Dossier de stockage des photos (relatif à la racine du projet) ─
PHOTOS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "assets", "photos"
)


def get_person_photo_dir(person_id: int) -> str:
    """
    Retourne (et crée si besoin) le dossier dédié à une personne.
    Structure : assets/photos/<person_id>/
    """
    folder = os.path.join(PHOTOS_DIR, str(person_id))
    os.makedirs(folder, exist_ok=True)
    return folder


def encode_and_save(person_id: int, source_image_path: str) -> dict:
    """
    Traite une photo et sauvegarde l'encodage en base.

    Args:
        person_id         : ID SQLite de la personne
        source_image_path : Chemin absolu vers la photo à encoder

    Returns:
        dict avec les clés :
          - success (bool)
          - message (str)  : description du résultat ou de l'erreur
          - dest_path (str): chemin de la photo copiée (si succès)
    """

    # ── Étape 1 : vérifier que le fichier existe ───────────────────
    if not os.path.exists(source_image_path):
        return {"success": False, "message": "Fichier introuvable.", "dest_path": None}

    # ── Étape 2 : charger l'image avec face_recognition ───────────
    # face_recognition.load_image_file lit l'image en RGB (numpy array)
    try:
        image = face_recognition.load_image_file(source_image_path)
    except Exception as e:
        return {"success": False, "message": f"Impossible de lire l'image : {e}", "dest_path": None}

    # ── Étape 3 : détecter les visages dans l'image ────────────────
    # face_locations retourne la liste des positions (top, right, bottom, left)
    # model="hog" = rapide sur CPU | model="cnn" = précis mais lent sans GPU
    face_locations = face_recognition.face_locations(image, model="hog")

    if len(face_locations) == 0:
        return {
            "success": False,
            "message": "Aucun visage détecté dans cette photo. Essayez une image plus nette.",
            "dest_path": None
        }

    if len(face_locations) > 1:
        return {
            "success": False,
            "message": f"{len(face_locations)} visages détectés. Utilisez une photo avec 1 seul visage.",
            "dest_path": None
        }

    # ── Étape 4 : calculer l'encodage du visage ────────────────────
    # face_encodings retourne une liste de vecteurs 128D (un par visage détecté)
    encodings = face_recognition.face_encodings(image, face_locations)

    if len(encodings) == 0:
        return {
            "success": False,
            "message": "Visage détecté mais encodage impossible. Photo trop floue ?",
            "dest_path": None
        }

    encoding = encodings[0]  # On prend le seul visage trouvé

    # ── Étape 5 : copier la photo dans le dossier assets/photos/ ───
    person_dir = get_person_photo_dir(person_id)
    filename   = os.path.basename(source_image_path)

    # Évite les collisions de noms : on préfixe avec un timestamp
    import time
    timestamp   = int(time.time() * 1000)
    dest_name   = f"{timestamp}_{filename}"
    dest_path   = os.path.join(person_dir, dest_name)
    shutil.copy2(source_image_path, dest_path)

    # ── Étape 6 : sauvegarder l'encodage en base SQLite ───────────
    save_encoding(person_id, encoding, dest_path)

    print(f"[Encoder] Encodage sauvegardé → person_id={person_id} | photo={dest_name}")

    return {
        "success": True,
        "message": "Encodage calculé et sauvegardé avec succès.",
        "dest_path": dest_path
    }


def encode_multiple(person_id: int, image_paths: list) -> list:
    """
    Encode une liste de photos pour une même personne.
    Retourne la liste des résultats (un dict par photo).

    Args:
        person_id   : ID SQLite de la personne
        image_paths : liste de chemins vers les photos

    Returns:
        Liste de dicts {success, message, dest_path}
    """
    results = []
    for path in image_paths:
        result = encode_and_save(person_id, path)
        results.append({"path": path, **result})
        if result["success"]:
            print(f"[Encoder] ✓ {os.path.basename(path)}")
        else:
            print(f"[Encoder] ✗ {os.path.basename(path)} → {result['message']}")
    return results
