"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/pages/add_person.py
─────────────────────────────────────────────────────────────────
Rôle : Page d'ajout d'une nouvelle personne.

Workflow :
  1. Saisir prénom + nom
  2. Uploader une ou plusieurs photos (drag ou bouton)
  3. VISIO·ID encode chaque photo et sauvegarde en base
  4. Feedback immédiat : ✓ succès ou ✗ erreur par photo
─────────────────────────────────────────────────────────────────
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from database.db_manager import add_person
from core.encoder import encode_multiple
from ui.theme import *


class AddPersonPage(ctk.CTkFrame):
    """Page d'ajout d'une nouvelle personne dans VISIO·ID."""

    def __init__(self, master, on_person_added=None, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)

        # Callback appelé après ajout réussi (pour rafraîchir la galerie)
        self.on_person_added = on_person_added

        # Liste des photos sélectionnées (chemins absolus)
        self._selected_photos = []

        self._build_ui()

    # ──────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construit la page d'ajout."""
        # Centrer le formulaire dans la page
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Conteneur centré
        container = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            corner_radius=16,
            width=560
        )
        container.grid(row=0, column=0, padx=60, pady=30, sticky="nsew")
        container.columnconfigure(0, weight=1)

        # ── Titre ──────────────────────────────────────────────────
        ctk.CTkLabel(
            container,
            text=f"{ICON_ADD}  Ajouter une personne",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XL, weight="bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, pady=(24, 4), padx=24, sticky="w")

        ctk.CTkLabel(
            container,
            text="Renseignez l'identité et uploadez les photos du visage.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            text_color=TEXT_SECONDARY
        ).grid(row=1, column=0, pady=(0, 20), padx=24, sticky="w")

        # Séparateur
        ctk.CTkFrame(container, fg_color=BORDER_COLOR, height=1).grid(
            row=2, column=0, padx=24, sticky="ew"
        )

        # ── Champ Prénom ───────────────────────────────────────────
        ctk.CTkLabel(
            container,
            text="Prénom *",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            text_color=TEXT_SECONDARY
        ).grid(row=3, column=0, pady=(16, 2), padx=24, sticky="w")

        self._entry_firstname = ctk.CTkEntry(
            container,
            placeholder_text="ex: Jean",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD),
            fg_color=BG_INPUT,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY,
            height=42,
            corner_radius=BTN_RADIUS
        )
        self._entry_firstname.grid(row=4, column=0, padx=24, sticky="ew", pady=(0, 12))

        # ── Champ Nom ──────────────────────────────────────────────
        ctk.CTkLabel(
            container,
            text="Nom *",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            text_color=TEXT_SECONDARY
        ).grid(row=5, column=0, pady=(0, 2), padx=24, sticky="w")

        self._entry_lastname = ctk.CTkEntry(
            container,
            placeholder_text="ex: Dupont",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD),
            fg_color=BG_INPUT,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY,
            height=42,
            corner_radius=BTN_RADIUS
        )
        self._entry_lastname.grid(row=6, column=0, padx=24, sticky="ew", pady=(0, 20))

        # ── Zone d'upload des photos ───────────────────────────────
        ctk.CTkLabel(
            container,
            text=f"{ICON_PHOTO}  Photos du visage *",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM, weight="bold"),
            text_color=TEXT_SECONDARY
        ).grid(row=7, column=0, pady=(0, 6), padx=24, sticky="w")

        # Zone de dépôt des photos (bouton + liste)
        self._upload_zone = ctk.CTkFrame(
            container,
            fg_color=BG_INPUT,
            corner_radius=10,
            border_width=2,
            border_color=BORDER_COLOR
        )
        self._upload_zone.grid(row=8, column=0, padx=24, sticky="ew", pady=(0, 8))
        self._upload_zone.columnconfigure(0, weight=1)

        # Bouton de sélection
        ctk.CTkButton(
            self._upload_zone,
            text=f"{ICON_UPLOAD}  Sélectionner des photos",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
            fg_color=BG_SECONDARY,
            hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self._browse_photos
        ).grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        # Compteur de photos sélectionnées
        self._photo_count_label = ctk.CTkLabel(
            self._upload_zone,
            text="Aucune photo sélectionnée",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_MUTED
        )
        self._photo_count_label.grid(row=1, column=0, pady=(0, 4))

        # Zone scrollable pour la liste des photos
        self._photos_scroll = ctk.CTkScrollableFrame(
            self._upload_zone,
            fg_color="transparent",
            height=100,
            scrollbar_button_color=BG_HOVER
        )
        self._photos_scroll.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="ew")
        self._photos_scroll.columnconfigure(0, weight=1)

        # ── Zone de résultats d'encodage ──────────────────────────
        self._results_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            height=90,
            scrollbar_button_color=BG_HOVER
        )
        self._results_frame.grid(row=9, column=0, padx=24, sticky="ew", pady=(0, 8))
        self._results_frame.grid_remove()  # Cachée au départ

        # ── Bouton Enregistrer ─────────────────────────────────────
        self._btn_save = ctk.CTkButton(
            container,
            text=f"💾  Enregistrer le profil",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_MD, weight="bold"),
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            height=44,
            corner_radius=BTN_RADIUS,
            command=self._save_person
        )
        self._btn_save.grid(row=10, column=0, padx=24, pady=(4, 8), sticky="ew")

        # Bouton Réinitialiser
        ctk.CTkButton(
            container,
            text="🔄  Réinitialiser le formulaire",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            fg_color="transparent",
            hover_color=BG_HOVER,
            text_color=TEXT_MUTED,
            height=30,
            corner_radius=BTN_RADIUS,
            command=self._reset_form
        ).grid(row=11, column=0, padx=24, pady=(0, 20))

    # ──────────────────────────────────────────────────────────────
    #  Gestion des photos
    # ──────────────────────────────────────────────────────────────

    def _browse_photos(self):
        """Ouvre un dialogue multi-sélection pour les photos."""
        paths = filedialog.askopenfilenames(
            title="Sélectionner des photos",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if not paths:
            return

        # Ajouter sans doublons
        added = 0
        for path in paths:
            if path not in self._selected_photos:
                self._selected_photos.append(path)
                added += 1

        self._refresh_photo_list()
        print(f"[AddPerson] {added} photo(s) ajoutée(s) → total : {len(self._selected_photos)}")

    def _refresh_photo_list(self):
        """Rafraîchit l'affichage de la liste des photos sélectionnées."""
        # Vider la liste
        for w in self._photos_scroll.winfo_children():
            w.destroy()

        n = len(self._selected_photos)
        self._photo_count_label.configure(
            text=f"{n} photo{'s' if n > 1 else ''} sélectionnée{'s' if n > 1 else ''}",
            text_color=TEXT_PRIMARY if n > 0 else TEXT_MUTED
        )

        # Afficher chaque photo avec un bouton de suppression
        for i, path in enumerate(self._selected_photos):
            row_frame = ctk.CTkFrame(self._photos_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)

            ctk.CTkLabel(
                row_frame,
                text=f"  {ICON_PHOTO}  {os.path.basename(path)}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
                text_color=TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            # Bouton retirer
            idx = i  # Capture de l'index pour le lambda
            ctk.CTkButton(
                row_frame,
                text="✕",
                width=24,
                height=20,
                font=ctk.CTkFont(size=FONT_SIZE_XS),
                fg_color="transparent",
                hover_color="#3D1A22",
                text_color=ACCENT_DANGER,
                corner_radius=4,
                command=lambda i=idx: self._remove_photo(i)
            ).pack(side="right", padx=4)

    def _remove_photo(self, index: int):
        """Retire une photo de la sélection."""
        if 0 <= index < len(self._selected_photos):
            self._selected_photos.pop(index)
            self._refresh_photo_list()

    # ──────────────────────────────────────────────────────────────
    #  Sauvegarde
    # ──────────────────────────────────────────────────────────────

    def _save_person(self):
        """Valide le formulaire, crée la personne et encode les photos."""

        # ── Validation ────────────────────────────────────────────
        first_name = self._entry_firstname.get().strip()
        last_name  = self._entry_lastname.get().strip()

        if not first_name or not last_name:
            CTkMessagebox(
                title="Champs manquants",
                message="Le prénom et le nom sont obligatoires.",
                icon="warning"
            )
            return

        if not self._selected_photos:
            CTkMessagebox(
                title="Aucune photo",
                message="Veuillez sélectionner au moins une photo.",
                icon="warning"
            )
            return

        # ── Désactiver le bouton pendant le traitement ─────────────
        self._btn_save.configure(
            state="disabled",
            text="⏳  Encodage en cours...",
            fg_color=BG_HOVER
        )
        self.update()

        # ── Créer la personne en base ──────────────────────────────
        person_id = add_person(first_name, last_name)

        # ── Encoder toutes les photos ──────────────────────────────
        results = encode_multiple(person_id, self._selected_photos)

        # ── Afficher les résultats ─────────────────────────────────
        self._show_results(results)

        # ── Réactiver le bouton ────────────────────────────────────
        self._btn_save.configure(
            state="normal",
            text="💾  Enregistrer le profil",
            fg_color=ACCENT_PRIMARY
        )

        # ── Compter les succès ─────────────────────────────────────
        success_count = sum(1 for r in results if r["success"])
        fail_count    = len(results) - success_count

        if success_count == 0:
            # Aucun encodage réussi → supprimer la personne créée
            from database.db_manager import delete_person
            delete_person(person_id)
            CTkMessagebox(
                title="Échec",
                message="Aucune photo n'a pu être encodée.\nLa personne n'a pas été ajoutée.\nVérifiez que les photos contiennent un visage visible.",
                icon="cancel"
            )
        else:
            msg = f"✓ {first_name} {last_name.upper()} ajouté(e) avec succès !\n\n"
            msg += f"{success_count} photo(s) encodée(s)"
            if fail_count > 0:
                msg += f"\n{fail_count} photo(s) ignorée(s) (aucun visage détecté)"

            CTkMessagebox(title="Profil ajouté", message=msg, icon="check")

            # Notifier la page Home et la galerie
            if self.on_person_added:
                self.on_person_added()

            # Réinitialiser le formulaire
            self._reset_form()

    def _show_results(self, results: list):
        """Affiche le résultat d'encodage pour chaque photo."""
        self._results_frame.grid()

        # Vider les anciens résultats
        for w in self._results_frame.winfo_children():
            w.destroy()

        for r in results:
            color = ACCENT_SUCCESS if r["success"] else ACCENT_DANGER
            icon  = ICON_CHECK if r["success"] else "✗"
            name  = os.path.basename(r["path"])
            msg   = r["message"]

            ctk.CTkLabel(
                self._results_frame,
                text=f"  {icon}  {name}  —  {msg}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
                text_color=color,
                anchor="w"
            ).pack(fill="x", pady=1)

    def _reset_form(self):
        """Réinitialise tous les champs du formulaire."""
        self._entry_firstname.delete(0, "end")
        self._entry_lastname.delete(0, "end")
        self._selected_photos.clear()
        self._refresh_photo_list()

        # Cacher les résultats
        self._results_frame.grid_remove()
        for w in self._results_frame.winfo_children():
            w.destroy()
