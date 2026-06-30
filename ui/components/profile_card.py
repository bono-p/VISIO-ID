"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/components/profile_card.py
─────────────────────────────────────────────────────────────────
Rôle : Widget carte de profil pour la galerie.
       Affiche la photo miniature, le nom et le nombre de photos.
       Boutons Modifier et Supprimer intégrés.
─────────────────────────────────────────────────────────────────
"""

import os
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from ui.theme import *


def _get_first_photo_path(person_id: int) -> str | None:
    """
    Cherche la première photo disponible pour une personne
    dans assets/photos/<person_id>/.
    Retourne le chemin ou None si aucune photo trouvée.
    """
    photos_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "assets", "photos", str(person_id)
    )
    if not os.path.isdir(photos_dir):
        return None

    for f in os.listdir(photos_dir):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            return os.path.join(photos_dir, f)
    return None


def _load_thumbnail(person_id: int, size: int) -> ctk.CTkImage | None:
    """
    Charge et redimensionne la photo d'une personne en miniature carrée.
    Retourne un CTkImage ou None si aucune photo disponible.
    """
    path = _get_first_photo_path(person_id)
    if not path:
        return None

    try:
        img = Image.open(path).convert("RGB")

        # ── Crop carré centré ─────────────────────────────────────
        w, h   = img.size
        min_dim = min(w, h)
        left   = (w - min_dim) // 2
        top    = (h - min_dim) // 2
        img    = img.crop((left, top, left + min_dim, top + min_dim))
        img    = img.resize((size, size), Image.LANCZOS)

        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))

    except Exception as e:
        print(f"[ProfileCard] Erreur chargement photo : {e}")
        return None


class ProfileCard(ctk.CTkFrame):
    """
    Carte de profil affichée dans la galerie.

    Args:
        master       : widget parent
        person_data  : sqlite3.Row avec {id, first_name, last_name, created_at}
        photo_count  : nombre de photos enregistrées
        on_edit      : callback appelé au clic sur "Modifier" → fn(person_id)
        on_delete    : callback appelé au clic sur "Supprimer" → fn(person_id)
    """

    def __init__(
        self,
        master,
        person_data,
        photo_count: int,
        on_edit=None,
        on_delete=None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
            **kwargs
        )

        self.person_id = person_data["id"]
        self.on_edit   = on_edit
        self.on_delete = on_delete

        self._build_ui(person_data, photo_count)
        self._bind_hover()

    def _build_ui(self, person_data, photo_count: int):
        """Construit les widgets de la carte."""

        # ── Photo miniature ────────────────────────────────────────
        thumb = _load_thumbnail(self.person_id, CARD_THUMB_SIZE)

        if thumb:
            photo_label = ctk.CTkLabel(self, image=thumb, text="")
        else:
            # Placeholder icône si pas de photo
            photo_label = ctk.CTkLabel(
                self,
                text=ICON_PERSON,
                font=ctk.CTkFont(size=40),
                text_color=TEXT_MUTED,
                fg_color=BG_INPUT,
                corner_radius=CARD_THUMB_SIZE // 2,
                width=CARD_THUMB_SIZE,
                height=CARD_THUMB_SIZE
            )

        photo_label.pack(pady=(16, 8))

        # ── Nom complet ────────────────────────────────────────────
        full_name = f"{person_data['first_name']}\n{person_data['last_name'].upper()}"
        ctk.CTkLabel(
            self,
            text=full_name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            text_color=TEXT_PRIMARY,
            justify="center"
        ).pack(pady=(0, 4))

        # ── Nombre de photos ───────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=f"{ICON_PHOTO} {photo_count} photo{'s' if photo_count > 1 else ''}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_SECONDARY
        ).pack(pady=(0, 10))

        # ── Boutons actions ────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 14), padx=12, fill="x")
        btn_frame.columnconfigure((0, 1), weight=1)

        # Bouton Modifier
        ctk.CTkButton(
            btn_frame,
            text=f"{ICON_EDIT}",
            width=60,
            height=28,
            font=ctk.CTkFont(size=FONT_SIZE_XS),
            fg_color=BG_INPUT,
            hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY,
            corner_radius=6,
            command=self._on_edit_click
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        # Bouton Supprimer
        ctk.CTkButton(
            btn_frame,
            text=f"{ICON_DELETE}",
            width=60,
            height=28,
            font=ctk.CTkFont(size=FONT_SIZE_XS),
            fg_color=BG_INPUT,
            hover_color="#3D1A22",
            text_color=ACCENT_DANGER,
            corner_radius=6,
            command=self._on_delete_click
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

    def _bind_hover(self):
        """Effet de hover sur toute la carte."""
        self.bind("<Enter>", lambda e: self.configure(border_color=ACCENT_PRIMARY))
        self.bind("<Leave>", lambda e: self.configure(border_color=BORDER_COLOR))

    def _on_edit_click(self):
        if self.on_edit:
            self.on_edit(self.person_id)

    def _on_delete_click(self):
        if self.on_delete:
            self.on_delete(self.person_id)
