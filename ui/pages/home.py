"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/pages/home.py
─────────────────────────────────────────────────────────────────
Rôle : Page principale — flux vidéo en temps réel avec
       reconnaissance faciale et liste des personnes détectées.

Layout :
  ┌─────────────────────────────┬──────────────────┐
  │                             │  Profils détectés │
  │     FLUX VIDÉO ANNOTÉ       │  ┌─────────────┐ │
  │                             │  │ ✓ Jean D.   │ │
  │  [Source] [▶ Start] [⏹ Stop]│  └─────────────┘ │
  └─────────────────────────────┴──────────────────┘
─────────────────────────────────────────────────────────────────
"""

import os
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from core.recognizer import Recognizer
from core.video_processor import process_photo
from ui.components.video_frame import VideoFrame
from ui.theme import *


class HomePage(ctk.CTkFrame):
    """Page principale avec le flux vidéo et la reconnaissance."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)

        self._recognizer = None   # Instance du moteur de reconnaissance
        self._source     = None   # Source courante (int ou str)

        self._build_ui()

    # ──────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construit tous les widgets de la page."""
        self.columnconfigure(0, weight=1)    # Colonne vidéo (extensible)
        self.columnconfigure(1, weight=0)    # Sidebar (largeur fixe)
        self.rowconfigure(0, weight=0)       # Barre de contrôle
        self.rowconfigure(1, weight=1)       # Zone vidéo + sidebar

        # ── Barre de contrôle ──────────────────────────────────────
        self._build_control_bar()

        # ── Zone vidéo ────────────────────────────────────────────
        self._video_frame = VideoFrame(self)
        self._video_frame.grid(row=1, column=0, padx=(16, 8), pady=(0, 16), sticky="nsew")

        # ── Sidebar droite ────────────────────────────────────────
        self._build_sidebar()

    def _build_control_bar(self):
        """Barre horizontale avec sélection de source et boutons Play/Stop."""
        bar = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=10, height=60)
        bar.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 8), sticky="ew")
        bar.pack_propagate(False)
        bar.grid_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=16, pady=8)

        # ── Sélection de la source ─────────────────────────────────
        ctk.CTkLabel(
            inner,
            text="Source :",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=(0, 8))

        # Menu déroulant
        self._source_var = ctk.StringVar(value="Webcam")
        self._source_menu = ctk.CTkOptionMenu(
            inner,
            values=["Webcam", "IP Webcam", "Fichier vidéo", "Photo"],
            variable=self._source_var,
            command=self._on_source_change,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_INPUT,
            button_color=ACCENT_PRIMARY,
            button_hover_color=ACCENT_HOVER,
            width=140,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS
        )
        self._source_menu.pack(side="left", padx=(0, 12))

        # ── Champ IP (affiché seulement si "IP Webcam" sélectionné) ─
        self._ip_frame = ctk.CTkFrame(inner, fg_color="transparent")

        ctk.CTkLabel(
            self._ip_frame,
            text="URL :",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=(0, 4))

        self._ip_entry = ctk.CTkEntry(
            self._ip_frame,
            placeholder_text="http://192.168.1.x:8080/video",
            font=ctk.CTkFont(family=FONT_MONO, size=FONT_SIZE_XS),
            fg_color=BG_INPUT,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY,
            width=230,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS
        )
        self._ip_entry.pack(side="left")

        # ── Champ fichier ──────────────────────────────────────────
        self._file_frame = ctk.CTkFrame(inner, fg_color="transparent")

        self._file_label = ctk.CTkLabel(
            self._file_frame,
            text="Aucun fichier",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_MUTED,
            width=180
        )
        self._file_label.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            self._file_frame,
            text=f"{ICON_FILE} Parcourir",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            fg_color=BG_INPUT,
            hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self._browse_file
        ).pack(side="left")

        # ── Boutons Play / Stop ────────────────────────────────────
        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=8)

        self._btn_play = ctk.CTkButton(
            btn_frame,
            text=f"{ICON_PLAY}  Démarrer",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            height=BTN_HEIGHT,
            width=130,
            corner_radius=BTN_RADIUS,
            command=self._start_stream
        )
        self._btn_play.pack(side="left", padx=(0, 8))

        self._btn_stop = ctk.CTkButton(
            btn_frame,
            text=f"{ICON_STOP}  Arrêter",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_INPUT,
            hover_color="#3D1A22",
            text_color=ACCENT_DANGER,
            height=BTN_HEIGHT,
            width=110,
            corner_radius=BTN_RADIUS,
            state="disabled",
            command=self._stop_stream
        )
        self._btn_stop.pack(side="left")

        self._selected_file = None

    def _build_sidebar(self):
        """Panneau latéral droit : liste des personnes reconnues."""
        self._sidebar = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            corner_radius=12,
            width=SIDEBAR_WIDTH
        )
        self._sidebar.grid(row=1, column=1, padx=(0, 16), pady=(0, 16), sticky="nsew")
        self._sidebar.grid_propagate(False)

        # Titre
        ctk.CTkLabel(
            self._sidebar,
            text=f"{ICON_GALLERY} Détections",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(16, 4), padx=16, anchor="w")

        # Compteur
        self._detection_count_label = ctk.CTkLabel(
            self._sidebar,
            text="0 personne(s) détectée(s)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_SECONDARY
        )
        self._detection_count_label.pack(padx=16, anchor="w")

        ctk.CTkFrame(self._sidebar, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=16, pady=10
        )

        # Zone scrollable pour les détections
        self._detections_scroll = ctk.CTkScrollableFrame(
            self._sidebar,
            fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_PRIMARY
        )
        self._detections_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Dictionnaire {name: widget} pour éviter les doublons à l'affichage
        self._detection_widgets = {}

    # ──────────────────────────────────────────────────────────────
    #  Gestion des sources
    # ──────────────────────────────────────────────────────────────

    def _on_source_change(self, value: str):
        """Affiche/cache les champs selon la source sélectionnée."""
        self._ip_frame.pack_forget()
        self._file_frame.pack_forget()

        if value == "IP Webcam":
            self._ip_frame.pack(side="left")
        elif value in ("Fichier vidéo", "Photo"):
            self._file_frame.pack(side="left")

    def _browse_file(self):
        """Ouvre un dialogue pour choisir un fichier vidéo ou photo."""
        from tkinter import filedialog

        source_type = self._source_var.get()

        if source_type == "Photo":
            filetypes = [
                ("Images", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("Tous", "*.*")
            ]
        else:
            filetypes = [
                ("Vidéos", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("Tous", "*.*")
            ]

        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self._selected_file = path
            # Afficher juste le nom du fichier (pas le chemin complet)
            self._file_label.configure(
                text=os.path.basename(path),
                text_color=TEXT_PRIMARY
            )

    # ──────────────────────────────────────────────────────────────
    #  Démarrage / Arrêt du flux
    # ──────────────────────────────────────────────────────────────

    def _start_stream(self):
        """Démarre la reconnaissance selon la source sélectionnée."""
        source_type = self._source_var.get()

        # ── Déterminer la source ───────────────────────────────────
        if source_type == "Webcam":
            self._source = 0  # Index webcam par défaut

        elif source_type == "IP Webcam":
            url = self._ip_entry.get().strip()
            if not url:
                CTkMessagebox(
                    title="Source manquante",
                    message="Veuillez entrer l'URL de la caméra IP.\nEx: http://192.168.1.x:8080/video",
                    icon="warning"
                )
                return
            self._source = url

        elif source_type in ("Fichier vidéo", "Photo"):
            if not self._selected_file:
                CTkMessagebox(
                    title="Fichier manquant",
                    message="Veuillez sélectionner un fichier.",
                    icon="warning"
                )
                return
            self._source = self._selected_file

        # ── Cas spécial : Photo statique ──────────────────────────
        if source_type == "Photo":
            self._process_photo()
            return

        # ── Démarrer le Recognizer ────────────────────────────────
        self._recognizer = Recognizer(source=self._source)
        self._recognizer.start(
            frame_callback=self._on_frame,
            done_callback=self._on_stream_done,
            error_callback=self._on_stream_error
        )

        self._set_streaming_state(True)

    def _stop_stream(self):
        """Arrête proprement le flux en cours."""
        if self._recognizer:
            self._recognizer.stop()
            self._recognizer = None

        self._set_streaming_state(False)
        self._video_frame.show_placeholder()
        self._clear_detections()

    def _set_streaming_state(self, streaming: bool):
        """Active/désactive les boutons selon l'état du flux."""
        if streaming:
            self._btn_play.configure(state="disabled", fg_color=BG_HOVER)
            self._btn_stop.configure(state="normal")
            self._source_menu.configure(state="disabled")
        else:
            self._btn_play.configure(state="normal", fg_color=ACCENT_PRIMARY)
            self._btn_stop.configure(state="disabled")
            self._source_menu.configure(state="normal")

    # ──────────────────────────────────────────────────────────────
    #  Callbacks du Recognizer
    # ──────────────────────────────────────────────────────────────

    def _on_frame(self, frame_bgr, face_data: list):
        """
        Appelé depuis le thread Recognizer à chaque frame.
        Met à jour le widget vidéo et la sidebar.
        """
        self._video_frame.update_frame(frame_bgr, face_data)
        self.after(0, self._update_detections, face_data)

    def _on_stream_done(self):
        """Appelé quand la vidéo fichier se termine."""
        self.after(0, self._stop_stream)

    def _on_stream_error(self, message: str):
        """Appelé en cas d'erreur d'ouverture de la source."""
        self.after(0, lambda: CTkMessagebox(
            title="Erreur de source",
            message=f"Impossible d'ouvrir la source :\n{message}",
            icon="cancel"
        ))
        self.after(0, self._set_streaming_state, False)

    # ──────────────────────────────────────────────────────────────
    #  Traitement photo statique
    # ──────────────────────────────────────────────────────────────

    def _process_photo(self):
        """Traite une photo statique et affiche le résultat."""
        try:
            frame, face_data = process_photo(self._source)
            self._video_frame.update_frame(frame, face_data)
            self._update_detections(face_data)

            if not face_data:
                CTkMessagebox(
                    title="Résultat",
                    message="Aucune personne connue détectée dans cette photo.",
                    icon="info"
                )
        except Exception as e:
            CTkMessagebox(
                title="Erreur",
                message=f"Erreur lors du traitement de la photo :\n{e}",
                icon="cancel"
            )

    # ──────────────────────────────────────────────────────────────
    #  Sidebar — mise à jour des détections
    # ──────────────────────────────────────────────────────────────

    def _update_detections(self, face_data: list):
        """
        Met à jour la liste des personnes détectées dans la sidebar.
        Évite les doublons si la même personne est présente plusieurs fois.
        """
        # Collecter les noms uniques détectés
        current_names = set(face["name"] for face in face_data)

        # ── Ajouter les nouveaux noms ──────────────────────────────
        for name in current_names:
            if name not in self._detection_widgets:
                widget = self._create_detection_widget(name)
                self._detection_widgets[name] = widget

        # ── Supprimer les noms qui ne sont plus détectés ──────────
        names_to_remove = [
            n for n in list(self._detection_widgets.keys())
            if n not in current_names
        ]
        for name in names_to_remove:
            self._detection_widgets[name].destroy()
            del self._detection_widgets[name]

        # ── Mettre à jour le compteur ─────────────────────────────
        count = len(current_names)
        self._detection_count_label.configure(
            text=f"{count} personne{'s' if count > 1 else ''} détectée{'s' if count > 1 else ''}"
        )

    def _create_detection_widget(self, name: str) -> ctk.CTkFrame:
        """Crée un widget pour une personne détectée dans la sidebar."""
        frame = ctk.CTkFrame(
            self._detections_scroll,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=ACCENT_SUCCESS
        )
        frame.pack(fill="x", pady=4, padx=4)

        ctk.CTkLabel(
            frame,
            text=f"  {ICON_CHECK}  {name}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            text_color=ACCENT_SUCCESS,
            anchor="w"
        ).pack(fill="x", padx=8, pady=8)

        return frame

    def _clear_detections(self):
        """Vide la liste des détections."""
        for widget in self._detection_widgets.values():
            widget.destroy()
        self._detection_widgets.clear()
        self._detection_count_label.configure(text="0 personne(s) détectée(s)")

    def reload_encodings(self):
        """
        Recharge les encodages si un Recognizer est actif.
        Appelé après l'ajout ou la suppression d'un profil.
        """
        if self._recognizer and self._recognizer.is_running():
            self._recognizer.reload_encodings()
