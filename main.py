"""
─────────────────────────────────────────────────────────────────
VISIO·ID — main.py
─────────────────────────────────────────────────────────────────
Point d'entrée de l'application.

Rôle :
  1. Initialise la base de données SQLite (création des tables)
  2. Lance la fenêtre principale CustomTkinter

Lancement :
  python main.py

Compilation avec PyInstaller :
  pyinstaller --onefile --windowed --name VISIO-ID main.py
  (voir README.md pour les instructions complètes)
─────────────────────────────────────────────────────────────────
"""

import sys
import os

# ── Garantir que le dossier racine est dans le sys.path ───────────
# Nécessaire pour les imports absolus (database, core, ui)
# quand on lance depuis un autre répertoire ou via PyInstaller
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ── Imports applicatifs ───────────────────────────────────────────
from database.db_manager import initialize_database
from ui.app import App


def main():
    """Fonction principale — initialisation et lancement de l'app."""

    print("=" * 55)
    print("  👁  VISIO·ID — Identify what you see")
    print("  Démarrage en cours...")
    print("=" * 55)

    # ── Étape 1 : Initialiser la base de données ──────────────────
    # Crée les tables si elles n'existent pas encore
    # (idempotent : sans effet si déjà créées)
    initialize_database()

    # ── Étape 2 : Lancer l'interface graphique ────────────────────
    app = App()
    app.mainloop()  # Boucle principale Tkinter

    print("[Main] Application fermée proprement.")


if __name__ == "__main__":
    main()
