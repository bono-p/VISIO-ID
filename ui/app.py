"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/app.py
─────────────────────────────────────────────────────────────────
Rôle : Fenêtre principale de l'application.
       Gère la navigation entre les pages (Accueil, Galerie, Ajouter).

Structure :
  ┌─────────────────────────────────────────────────────┐
  │  TOPBAR : Logo + Boutons de navigation              │
  ├─────────────────────────────────────────────────────┤
  │                                                     │
  │  CONTENT : Page active (Home / Gallery / AddPerson) │
  │                                                     │
  └─────────────────────────────────────────────────────┘
─────────────────────────────────────────────────────────────────
"""

import customtkinter as ctk
from ui.theme import *
from ui.pages.home       import HomePage
from ui.pages.gallery    import GalleryPage
from ui.pages.add_person import AddPersonPage


class App(ctk.CTk):
    """
    Fenêtre principale VISIO·ID.
    Hérite de CTk (CustomTkinter) pour le thème sombre natif.
    """

    def __init__(self):
        super().__init__()

        # ── Configuration de la fenêtre ────────────────────────────
        self.title("VISIO·ID — Identify what you see")
        self.geometry(f"{WINDOW_DEFAULT_W}x{WINDOW_DEFAULT_H}")
        self.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.configure(fg_color=BG_PRIMARY)

        # Thème global CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Référence vers la page active ─────────────────────────
        self._active_page = None
        self._nav_buttons = {}  # {page_name: CTkButton}

        # ── Construction de l'UI ───────────────────────────────────
        self._build_topbar()
        self._build_content_area()

        # ── Pages (créées une seule fois, affichées/cachées) ───────
        self._pages = {}
        self._init_pages()

        # ── Afficher la page d'accueil ────────────────────────────
        self._navigate("home")

        # ── Gestionnaire de fermeture propre ─────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────────────────────

    def _build_topbar(self):
        """Barre de navigation supérieure avec logo et onglets."""
        topbar = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            height=64
        )
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # ── Logo gauche ────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        logo_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            logo_frame,
            text=f"{ICON_LOGO}",
            font=ctk.CTkFont(size=26),
            text_color=ACCENT_PRIMARY
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            logo_frame,
            text="VISIO",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XL, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame,
            text="·ID",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XL, weight="bold"),
            text_color=ACCENT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame,
            text="  Identify what you see",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_MUTED
        ).pack(side="left", pady=(6, 0))

        # ── Boutons de navigation ─────────────────────────────────
        nav_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        nav_frame.pack(side="left", padx=40)

        nav_items = [
            ("home",       f"{ICON_HOME}  Accueil"),
            ("gallery",    f"{ICON_GALLERY}  Galerie"),
            ("add_person", f"{ICON_ADD}  Ajouter"),
        ]

        for page_name, label in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SM),
                fg_color="transparent",
                hover_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                height=40,
                width=130,
                corner_radius=BTN_RADIUS,
                command=lambda p=page_name: self._navigate(p)
            )
            btn.pack(side="left", padx=4)
            self._nav_buttons[page_name] = btn

        # ── Badge version ──────────────────────────────────────────
        ctk.CTkLabel(
            topbar,
            text="v1.0",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_XS),
            text_color=TEXT_MUTED
        ).pack(side="right", padx=20)

    def _build_content_area(self):
        """Zone principale où les pages sont affichées."""
        self._content = ctk.CTkFrame(self, fg_color=BG_PRIMARY, corner_radius=0)
        self._content.pack(fill="both", expand=True)
        self._content.columnconfigure(0, weight=1)
        self._content.rowconfigure(0, weight=1)

    def _init_pages(self):
        """
        Crée toutes les pages une seule fois.
        Les pages sont empilées dans le même espace et affichées/cachées
        selon la navigation (pattern "raise to front").
        """
        # Page Accueil
        home = HomePage(self._content)
        home.grid(row=0, column=0, sticky="nsew")
        self._pages["home"] = home

        # Page Galerie
        gallery = GalleryPage(
            self._content,
            on_profile_changed=self._on_profile_changed
        )
        gallery.grid(row=0, column=0, sticky="nsew")
        self._pages["gallery"] = gallery

        # Page Ajouter
        add = AddPersonPage(
            self._content,
            on_person_added=self._on_person_added
        )
        add.grid(row=0, column=0, sticky="nsew")
        self._pages["add_person"] = add

    # ──────────────────────────────────────────────────────────────
    #  Navigation
    # ──────────────────────────────────────────────────────────────

    def _navigate(self, page_name: str):
        """
        Affiche la page demandée et met à jour les boutons de navigation.

        Args:
            page_name : "home", "gallery", ou "add_person"
        """
        if page_name not in self._pages:
            print(f"[App] Page inconnue : {page_name}")
            return

        # ── Afficher la page (tkraise = mettre au premier plan) ────
        self._pages[page_name].tkraise()
        self._active_page = page_name

        # ── Mettre à jour le style des boutons de navigation ──────
        for name, btn in self._nav_buttons.items():
            if name == page_name:
                # Bouton actif : fond violet + texte blanc
                btn.configure(fg_color=ACCENT_PRIMARY, text_color=TEXT_PRIMARY)
            else:
                # Bouton inactif : transparent + texte gris
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

        print(f"[App] Navigation → {page_name}")

    # ──────────────────────────────────────────────────────────────
    #  Callbacks inter-pages
    # ──────────────────────────────────────────────────────────────

    def _on_person_added(self):
        """
        Appelé par AddPersonPage après l'ajout d'une personne.
        - Rafraîchit la galerie
        - Recharge les encodages dans la page Home
        - Redirige vers la galerie
        """
        self._pages["gallery"].refresh()
        self._pages["home"].reload_encodings()
        self._navigate("gallery")

    def _on_profile_changed(self):
        """
        Appelé par GalleryPage après modification/suppression d'un profil.
        Recharge les encodages dans la page Home.
        """
        self._pages["home"].reload_encodings()

    # ──────────────────────────────────────────────────────────────
    #  Fermeture propre
    # ──────────────────────────────────────────────────────────────

    def _on_close(self):
        """
        Arrête proprement le thread de reconnaissance avant de fermer.
        Sans ça, le thread daemon peut laisser OpenCV en état corrompu.
        """
        home_page = self._pages.get("home")
        if home_page and home_page._recognizer:
            print("[App] Arrêt du Recognizer avant fermeture...")
            home_page._recognizer.stop()

        self.destroy()
