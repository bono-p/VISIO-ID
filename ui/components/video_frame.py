"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/components/video_frame.py
─────────────────────────────────────────────────────────────────
Rôle : Widget CustomTkinter qui affiche le flux vidéo annoté
       (rectangles + noms des personnes reconnues).

Fonctionnement :
  - Reçoit une frame OpenCV (BGR numpy array) + les données visages
  - Dessine les rectangles et labels sur la frame
  - Convertit la frame en image Tkinter
  - Met à jour le label CTk qui l'affiche

Thread-safety :
  - La frame arrive depuis le thread Recognizer
  - L'affichage doit être fait dans le thread UI (Tkinter)
  - On utilise self.after() pour planifier la mise à jour dans l'UI
─────────────────────────────────────────────────────────────────
"""

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
from ui.theme import *


class VideoFrame(ctk.CTkFrame):
    """
    Widget d'affichage du flux vidéo annoté.
    S'intègre directement dans la page principale.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            corner_radius=12,
            **kwargs
        )

        # ── Label qui affiche la frame vidéo ──────────────────────
        self._video_label = ctk.CTkLabel(
            self,
            text="",
            fg_color="transparent"
        )
        self._video_label.pack(expand=True, fill="both", padx=4, pady=4)

        # ── Placeholder quand aucun flux n'est actif ──────────────
        self._show_placeholder()

        # ── Dernière image Tkinter (référence pour éviter le GC) ──
        self._current_image = None

        # ── Dimensions courantes du widget ────────────────────────
        self._display_w = 640
        self._display_h = 480

        # Bind pour détecter les changements de taille
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Met à jour les dimensions cibles lors d'un redimensionnement."""
        self._display_w = max(320, event.width  - 8)
        self._display_h = max(240, event.height - 8)

    def _show_placeholder(self):
        """
        Affiche un écran vide avec instructions
        quand aucune source vidéo n'est active.
        """
        placeholder = ctk.CTkLabel(
            self._video_label,
            text=f"{ICON_WEBCAM}\n\nAucune source active\nSélectionnez une source et appuyez sur ▶",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD),
            text_color=TEXT_MUTED,
            fg_color="transparent"
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self._placeholder = placeholder

    def _hide_placeholder(self):
        """Cache le placeholder dès qu'une frame arrive."""
        if hasattr(self, "_placeholder") and self._placeholder.winfo_exists():
            self._placeholder.destroy()

    def update_frame(self, frame_bgr: np.ndarray, face_data: list):
        """
        Met à jour l'affichage avec une nouvelle frame annotée.
        Doit être appelé depuis n'importe quel thread.

        Args:
            frame_bgr : frame OpenCV en BGR
            face_data : liste de dicts {name, top, right, bottom, left}
        """
        # Planifier l'affichage dans le thread UI
        self.after(0, self._render, frame_bgr, face_data)

    def _render(self, frame_bgr: np.ndarray, face_data: list):
        """
        Dessine les annotations et met à jour le label Tkinter.
        Exécuté dans le thread UI (via self.after).
        """
        try:
            self._hide_placeholder()

            # ── Copie pour ne pas modifier la frame originale ──────
            annotated = frame_bgr.copy()

            # ── Dessiner les annotations sur la frame ─────────────
            for face in face_data:
                self._draw_face_annotation(
                    annotated,
                    face["name"],
                    face["top"],
                    face["right"],
                    face["bottom"],
                    face["left"]
                )

            # ── Redimensionner la frame pour l'affichage ──────────
            frame_resized = self._resize_to_fit(annotated)

            # ── Convertir BGR → RGB → PIL → ImageTk ───────────────
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            tk_image  = ImageTk.PhotoImage(image=pil_image)

            # ── Mettre à jour le label ─────────────────────────────
            # IMPORTANT : garder une référence pour éviter le garbage collector
            self._current_image = tk_image
            self._video_label.configure(image=tk_image, text="")

        except Exception as e:
            print(f"[VideoFrame] Erreur rendu : {e}")

    def _draw_face_annotation(
        self,
        frame: np.ndarray,
        name: str,
        top: int, right: int, bottom: int, left: int
    ):
        """
        Dessine un rectangle et un label nom sur la frame.

        Style VISIO·ID :
          - Rectangle violet avec coins arrondis (simulés)
          - Label nom sur fond semi-transparent en dessous
        """
        # ── Rectangle autour du visage ────────────────────────────
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            RECT_COLOR_BGR,
            RECT_THICKNESS
        )

        # ── Coins décoratifs (style scan) ─────────────────────────
        corner_len = min(15, (right - left) // 4)
        thickness  = RECT_THICKNESS + 1

        # Coin haut-gauche
        cv2.line(frame, (left, top), (left + corner_len, top), RECT_COLOR_BGR, thickness)
        cv2.line(frame, (left, top), (left, top + corner_len), RECT_COLOR_BGR, thickness)
        # Coin haut-droit
        cv2.line(frame, (right, top), (right - corner_len, top), RECT_COLOR_BGR, thickness)
        cv2.line(frame, (right, top), (right, top + corner_len), RECT_COLOR_BGR, thickness)
        # Coin bas-gauche
        cv2.line(frame, (left, bottom), (left + corner_len, bottom), RECT_COLOR_BGR, thickness)
        cv2.line(frame, (left, bottom), (left, bottom - corner_len), RECT_COLOR_BGR, thickness)
        # Coin bas-droit
        cv2.line(frame, (right, bottom), (right - corner_len, bottom), RECT_COLOR_BGR, thickness)
        cv2.line(frame, (right, bottom), (right, bottom - corner_len), RECT_COLOR_BGR, thickness)

        # ── Label avec le nom ─────────────────────────────────────
        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = FONT_SCALE_VIDEO
        thickness  = FONT_THICKNESS

        (text_w, text_h), baseline = cv2.getTextSize(name, font, font_scale, thickness)

        # Fond du label (rectangle plein sous le visage)
        label_top    = bottom
        label_bottom = bottom + text_h + LABEL_PADDING * 2
        label_right  = left + text_w + LABEL_PADDING * 2

        cv2.rectangle(
            frame,
            (left, label_top),
            (label_right, label_bottom),
            RECT_COLOR_BGR,  # Fond violet
            cv2.FILLED
        )

        # Texte blanc
        cv2.putText(
            frame,
            name,
            (left + LABEL_PADDING, label_bottom - LABEL_PADDING),
            font,
            font_scale,
            TEXT_COLOR_BGR,
            thickness,
            cv2.LINE_AA
        )

    def _resize_to_fit(self, frame: np.ndarray) -> np.ndarray:
        """
        Redimensionne la frame pour s'adapter au widget
        en conservant le ratio d'aspect.
        """
        h, w = frame.shape[:2]
        target_w = self._display_w
        target_h = self._display_h

        # Calcul du ratio pour tenir dans le widget
        ratio  = min(target_w / w, target_h / h)
        new_w  = int(w * ratio)
        new_h  = int(h * ratio)

        return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def show_placeholder(self):
        """Remet le placeholder (appelé après l'arrêt du flux)."""
        self._video_label.configure(image="", text="")
        self._current_image = None
        self._show_placeholder()
