"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/pages/gallery.py
─────────────────────────────────────────────────────────────────
Rôle : Page galerie — affiche toutes les personnes enregistrées
       sous forme de cartes avec miniature, nom et actions.

Fonctionnalités :
  - Grille de ProfileCard (une par personne)
  - Bouton de rafraîchissement
  - Gestion suppression avec confirmation
  - Bouton modifier qui ouvre un dialogue d'édition inline
─────────────────────────────────────────────────────────────────
"""

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from database.db_manager import (
    get_all_persons,
    delete_person,
    update_person,
    count_photos_for_person
)
from ui.components.profile_card import ProfileCard
from ui.theme import *


class GalleryPage(ctk.CTkFrame):
    """Page galerie des profils enregistrés."""

    def __init__(self, master, on_profile_changed=None, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)

        # Callback appelé quand un profil est modifié ou supprimé
        # Permet à la page Home de recharger ses encodages
        self.on_profile_changed = on_profile_changed

        self._build_ui()
        self.refresh()

    # ──────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construit la structure de la page."""
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # ── En-tête ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(
            header,
            text=f"{ICON_GALLERY}  Galerie des profils",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XL, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        # Compteur de profils
        self._count_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            text_color=TEXT_SECONDARY
        )
        self._count_label.pack(side="left", padx=(12, 0))

        # Bouton rafraîchir
        ctk.CTkButton(
            header,
            text="↻  Rafraîchir",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_INPUT,
            hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY,
            height=BTN_HEIGHT,
            width=120,
            corner_radius=BTN_RADIUS,
            command=self.refresh
        ).pack(side="right")

        # ── Zone de grille scrollable ─────────────────────────────
        self._scroll_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BG_HOVER,
            scrollbar_button_hover_color=ACCENT_PRIMARY
        )
        self._scroll_area.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

    # ──────────────────────────────────────────────────────────────
    #  Chargement et affichage
    # ──────────────────────────────────────────────────────────────

    def refresh(self):
        """Recharge et réaffiche toutes les cartes de profil."""
        # ── Vider la grille actuelle ──────────────────────────────
        for widget in self._scroll_area.winfo_children():
            widget.destroy()

        persons = get_all_persons()

        # ── Mettre à jour le compteur ─────────────────────────────
        n = len(persons)
        self._count_label.configure(
            text=f"— {n} profil{'s' if n > 1 else ''} enregistré{'s' if n > 1 else ''}"
        )

        if not persons:
            # Message vide
            ctk.CTkLabel(
                self._scroll_area,
                text=f"{ICON_PERSON}\n\nAucun profil enregistré.\nAjoutez des personnes via l'onglet ➕",
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD),
                text_color=TEXT_MUTED,
                justify="center"
            ).pack(pady=80)
            return

        # ── Construire la grille de cartes ────────────────────────
        # Calcul dynamique du nombre de colonnes selon la largeur
        COLS = 4  # Valeur par défaut
        row = 0
        col = 0

        for person in persons:
            photo_count = count_photos_for_person(person["id"])

            card = ProfileCard(
                self._scroll_area,
                person_data=person,
                photo_count=photo_count,
                on_edit=self._on_edit,
                on_delete=self._on_delete,
                width=CARD_W,
                height=CARD_H
            )
            card.grid(
                row=row, column=col,
                padx=8, pady=8,
                sticky="n"
            )

            col += 1
            if col >= COLS:
                col = 0
                row += 1

    # ──────────────────────────────────────────────────────────────
    #  Actions sur les profils
    # ──────────────────────────────────────────────────────────────

    def _on_edit(self, person_id: int):
        """Ouvre un dialogue pour modifier le nom d'une personne."""
        from database.db_manager import get_person_by_id
        person = get_person_by_id(person_id)
        if not person:
            return

        # ── Fenêtre de modification ────────────────────────────────
        dialog = ctk.CTkToplevel(self)
        dialog.title("Modifier le profil")
        dialog.geometry("380x260")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_PRIMARY)
        dialog.grab_set()  # Modal
        dialog.focus()

        ctk.CTkLabel(
            dialog,
            text=f"{ICON_EDIT}  Modifier le profil",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_LG, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(20, 16), padx=20, anchor="w")

        # Champs prénom / nom
        ctk.CTkLabel(dialog, text="Prénom", font=ctk.CTkFont(size=FONT_SIZE_SM),
                     text_color=TEXT_SECONDARY).pack(padx=20, anchor="w")
        entry_first = ctk.CTkEntry(
            dialog,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS
        )
        entry_first.insert(0, person["first_name"])
        entry_first.pack(padx=20, fill="x", pady=(2, 8))

        ctk.CTkLabel(dialog, text="Nom", font=ctk.CTkFont(size=FONT_SIZE_SM),
                     text_color=TEXT_SECONDARY).pack(padx=20, anchor="w")
        entry_last = ctk.CTkEntry(
            dialog,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_INPUT, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS
        )
        entry_last.insert(0, person["last_name"])
        entry_last.pack(padx=20, fill="x", pady=(2, 16))

        def _save():
            fn = entry_first.get().strip()
            ln = entry_last.get().strip()
            if not fn or not ln:
                CTkMessagebox(title="Champs vides",
                              message="Le prénom et le nom sont obligatoires.", icon="warning")
                return
            update_person(person_id, fn, ln)
            dialog.destroy()
            self.refresh()
            if self.on_profile_changed:
                self.on_profile_changed()

        ctk.CTkButton(
            dialog,
            text="💾  Enregistrer",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            fg_color=ACCENT_PRIMARY, hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY, height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=_save
        ).pack(padx=20, fill="x")

    def _on_delete(self, person_id: int):
        """Demande confirmation avant de supprimer un profil."""
        from database.db_manager import get_person_by_id
        person = get_person_by_id(person_id)
        if not person:
            return

        name = f"{person['first_name']} {person['last_name'].upper()}"

        confirm = CTkMessagebox(
            title="Confirmer la suppression",
            message=f"Supprimer le profil de {name} ?\n\nToutes ses photos et encodages seront supprimés définitivement.",
            icon="warning",
            option_1="Annuler",
            option_2="Supprimer"
        )

        if confirm.get() == "Supprimer":
            delete_person(person_id)
            self.refresh()
            if self.on_profile_changed:
                self.on_profile_changed()
            print(f"[Gallery] Profil supprimé : {name}")
