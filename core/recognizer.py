"""
─────────────────────────────────────────────────────────────────
VISIO·ID — core/recognizer.py
─────────────────────────────────────────────────────────────────
Rôle : Moteur de reconnaissance faciale en temps réel.
       Fonctionne dans un thread séparé pour ne pas bloquer l'UI.

Fonctionnement :
  1. On charge tous les encodages depuis la base SQLite (en RAM)
  2. On ouvre le flux vidéo (webcam, IP, ou fichier)
  3. Chaque N frames (PROCESS_EVERY_N_FRAMES), on :
     a. Réduit la frame pour accélérer la détection
     b. Détecte les visages
     c. Compare avec les encodages connus
     d. Retourne les résultats via callback
  4. Entre deux analyses, on affiche le dernier résultat connu
     (les rectangles "persistent" = pas de clignotement)

Tolérance (TOLERANCE) :
  Valeur entre 0.0 et 1.0.
  Plus elle est basse, plus la reconnaissance est stricte.
  0.5 = équilibre précision/rappel recommandé.
─────────────────────────────────────────────────────────────────
"""

import threading
import time
import cv2
import face_recognition
import numpy as np
from database.db_manager import load_all_encodings


# ── Paramètres de performance ──────────────────────────────────────
PROCESS_EVERY_N_FRAMES = 3    # Analyser 1 frame sur 3 (compromis vitesse/précision)
FRAME_SCALE            = 0.5  # Réduire la frame à 50% pour accélérer la détection
TOLERANCE              = 0.50  # Seuil de similarité (plus bas = plus strict)


class Recognizer:
    """
    Moteur de reconnaissance faciale asynchrone.

    Usage typique :
        rec = Recognizer(source=0)           # Webcam par défaut
        rec.start(frame_callback, done_callback)
        # ... plus tard ...
        rec.stop()
    """

    def __init__(self, source):
        """
        Args:
            source : int (indice webcam), str (URL IP ou chemin fichier)
        """
        self.source        = source
        self._thread       = None
        self._running      = False

        # ── Données de reconnaissance (chargées depuis SQLite) ─────
        self.known_encodings = []  # Liste de np.ndarray (128D)
        self.known_labels    = []  # Liste de str "Prénom NOM"

        # ── État courant (persisté entre frames) ──────────────────
        self._face_locations = []  # Positions des visages détectés
        self._face_names     = []  # Noms correspondants
        self._frame_count    = 0   # Compteur de frames

    # ──────────────────────────────────────────────────────────────
    #  Interface publique
    # ──────────────────────────────────────────────────────────────

    def reload_encodings(self):
        """
        (Re)charge les encodages depuis la base SQLite.
        À appeler après l'ajout ou la suppression d'un profil.
        """
        self.known_encodings, self.known_labels = load_all_encodings()
        print(f"[Recognizer] {len(self.known_encodings)} encodage(s) chargé(s).")

    def start(self, frame_callback, done_callback=None, error_callback=None):
        """
        Démarre la capture et la reconnaissance dans un thread séparé.

        Args:
            frame_callback  : fonction appelée à chaque frame traitée.
                              Signature : callback(frame_bgr, face_data)
                              face_data = liste de dicts {name, top, right, bottom, left}
            done_callback   : appelée quand le flux se termine naturellement (fin de vidéo)
            error_callback  : appelée en cas d'erreur. Signature : callback(message)
        """
        if self._running:
            print("[Recognizer] Déjà en cours d'exécution.")
            return

        self.reload_encodings()
        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            args=(frame_callback, done_callback, error_callback),
            daemon=True  # Thread daemon = s'arrête automatiquement si l'app se ferme
        )
        self._thread.start()
        print(f"[Recognizer] Démarré → source={self.source}")

    def stop(self):
        """Arrête proprement la capture vidéo."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
        self._thread = None
        print("[Recognizer] Arrêté.")

    def is_running(self) -> bool:
        return self._running

    # ──────────────────────────────────────────────────────────────
    #  Boucle principale (exécutée dans le thread)
    # ──────────────────────────────────────────────────────────────

    def _run(self, frame_callback, done_callback, error_callback):
        """
        Boucle de capture et de reconnaissance.
        Tourne dans son propre thread pour ne pas bloquer l'UI.
        """
        # ── Ouverture du flux vidéo ────────────────────────────────
        cap = cv2.VideoCapture(self.source)

        if not cap.isOpened():
            self._running = False
            if error_callback:
                error_callback(f"Impossible d'ouvrir la source : {self.source}")
            return

        self._frame_count = 0

        while self._running:
            ret, frame = cap.read()

            if not ret:
                # Fin du fichier vidéo ou perte du flux
                break

            self._frame_count += 1

            # ── Analyse partielle (1 frame sur N) ─────────────────
            if self._frame_count % PROCESS_EVERY_N_FRAMES == 0:
                self._process_frame(frame)

            # ── Construire les données de visages pour le callback ─
            face_data = self._build_face_data()

            # ── Appeler le callback UI avec la frame annotée ───────
            if frame_callback:
                frame_callback(frame.copy(), face_data)

            # ── Petite pause pour ne pas saturer le CPU ────────────
            time.sleep(0.01)

        # ── Libération des ressources ─────────────────────────────
        cap.release()
        self._running = False

        if done_callback:
            done_callback()

        print("[Recognizer] Flux terminé.")

    def _process_frame(self, frame):
        """
        Détecte et reconnaît les visages dans une frame.
        Met à jour self._face_locations et self._face_names.

        Optimisation :
          - On réduit la frame (FRAME_SCALE) avant la détection
          - On remet à l'échelle originale pour l'affichage
        """
        # ── Réduction de la frame pour accélérer la détection ─────
        small_frame = cv2.resize(
            frame,
            (0, 0),
            fx=FRAME_SCALE,
            fy=FRAME_SCALE
        )

        # OpenCV utilise BGR, face_recognition utilise RGB → conversion
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # ── Détection des visages ──────────────────────────────────
        # model="hog" = plus rapide sur CPU (vs "cnn" qui nécessite GPU)
        locations = face_recognition.face_locations(rgb_small_frame, model="hog")

        if not locations:
            self._face_locations = []
            self._face_names     = []
            return

        # ── Calcul des encodages des visages détectés ─────────────
        encodings = face_recognition.face_encodings(rgb_small_frame, locations)

        names = []
        for enc in encodings:
            name = self._identify(enc)
            names.append(name)

        # ── Remettre à l'échelle (FRAME_SCALE → taille originale) ─
        scale = 1.0 / FRAME_SCALE
        self._face_locations = [
            (
                int(top    * scale),
                int(right  * scale),
                int(bottom * scale),
                int(left   * scale)
            )
            for (top, right, bottom, left) in locations
        ]
        self._face_names = names

    def _identify(self, encoding: np.ndarray) -> str:
        """
        Compare un encodage avec tous les encodages connus.

        Algorithme :
          1. Calcule les distances euclidiennes avec tous les encodages connus
          2. Trouve la distance minimale
          3. Si cette distance < TOLERANCE → c'est la personne correspondante
          4. Sinon → "Inconnu" (mais on n'affiche rien pour les inconnus)

        Args:
            encoding : vecteur 128D du visage à identifier

        Returns:
            str : nom de la personne ou chaîne vide si inconnu
        """
        if not self.known_encodings:
            return ""

        # face_distance retourne un tableau de distances (0.0 = identique)
        distances = face_recognition.face_distance(self.known_encodings, encoding)

        # Trouver l'index du plus proche
        best_idx      = np.argmin(distances)
        best_distance = distances[best_idx]

        if best_distance < TOLERANCE:
            return self.known_labels[best_idx]

        # Visage inconnu → on ne l'affiche pas (comme convenu)
        return ""

    def _build_face_data(self) -> list:
        """
        Construit la liste des données de visages pour le callback UI.

        Returns:
            Liste de dicts :
            [
              { "name": "Jean DUPONT", "top": 100, "right": 200, "bottom": 180, "left": 120 },
              ...
            ]
        """
        face_data = []
        for (top, right, bottom, left), name in zip(
            self._face_locations,
            self._face_names
        ):
            # On n'inclut que les visages avec un nom reconnu
            if name:
                face_data.append({
                    "name"  : name,
                    "top"   : top,
                    "right" : right,
                    "bottom": bottom,
                    "left"  : left
                })
        return face_data
