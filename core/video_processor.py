"""
─────────────────────────────────────────────────────────────────
VISIO·ID — core/video_processor.py
─────────────────────────────────────────────────────────────────
Rôle : Traitement de fichiers vidéo et de photos statiques.

Pour les photos :
  - Analyse l'image une seule fois
  - Retourne la frame annotée directement

Pour les vidéos :
  - Lit le fichier frame par frame (comme un flux)
  - Utilise le même moteur Recognizer
  - Passe par les mêmes callbacks que la webcam

Ce module est un wrapper léger : il prépare la source
et délègue la logique de reconnaissance à Recognizer.
─────────────────────────────────────────────────────────────────
"""

import cv2
import numpy as np
import face_recognition
from database.db_manager import load_all_encodings
from core.recognizer import TOLERANCE, FRAME_SCALE


def process_photo(image_path: str) -> tuple:
    """
    Analyse une photo statique et retourne la frame annotée
    avec les rectangles et noms des personnes reconnues.

    Args:
        image_path : chemin absolu vers la photo

    Returns:
        Tuple (annotated_frame_bgr, face_data)
        - annotated_frame_bgr : np.ndarray BGR prêt pour affichage
        - face_data : liste de dicts {name, top, right, bottom, left}
    """
    # ── Chargement des encodages depuis la base ────────────────────
    known_encodings, known_labels = load_all_encodings()

    # ── Lecture de l'image avec OpenCV ────────────────────────────
    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError(f"Impossible de lire l'image : {image_path}")

    # ── Redimensionner si trop grande (performances) ───────────────
    h, w = frame.shape[:2]
    max_dim = 1280
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))

    # ── Conversion BGR → RGB pour face_recognition ────────────────
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ── Détection et encodage des visages ─────────────────────────
    locations = face_recognition.face_locations(rgb_frame, model="hog")
    encodings = face_recognition.face_encodings(rgb_frame, locations)

    face_data = []

    for (top, right, bottom, left), enc in zip(locations, encodings):
        name = _identify(enc, known_encodings, known_labels)
        if name:
            face_data.append({
                "name"  : name,
                "top"   : top,
                "right" : right,
                "bottom": bottom,
                "left"  : left
            })

    return frame, face_data


def _identify(encoding, known_encodings, known_labels) -> str:
    """
    Identifie un visage en comparant avec les encodages connus.
    (Identique à Recognizer._identify mais en fonction standalone)
    """
    if not known_encodings:
        return ""

    distances = face_recognition.face_distance(known_encodings, encoding)
    best_idx  = np.argmin(distances)

    if distances[best_idx] < TOLERANCE:
        return known_labels[best_idx]

    return ""  # Inconnu → on ne fait rien
