"""
─────────────────────────────────────────────────────────────────
VISIO·ID — ui/theme.py
─────────────────────────────────────────────────────────────────
Rôle : Centraliser toutes les constantes visuelles de l'application.
       Palette de couleurs, polices, dimensions, etc.
       Modifier ici pour changer l'apparence globale.
─────────────────────────────────────────────────────────────────
"""

# ══════════════════════════════════════════════════════════════════
#  PALETTE DE COULEURS — Thème Sombre VISIO·ID
# ══════════════════════════════════════════════════════════════════

# Fonds
BG_PRIMARY       = "#0F1117"   # Fond principal (noir profond)
BG_SECONDARY     = "#1A1D27"   # Cartes, sidebar, panneaux
BG_CARD          = "#1E2130"   # Cartes de profil
BG_INPUT         = "#252838"   # Champs de saisie
BG_HOVER         = "#2A2D3E"   # Survol de boutons

# Accents
ACCENT_PRIMARY   = "#6C63FF"   # Violet électrique (boutons principaux)
ACCENT_HOVER     = "#7B74FF"   # Hover bouton principal
ACCENT_SUCCESS   = "#00D4AA"   # Vert-cyan (détection OK, succès)
ACCENT_WARNING   = "#FFB347"   # Orange (avertissement)
ACCENT_DANGER    = "#FF5C7A"   # Rouge-rose (suppression, erreur)

# Textes
TEXT_PRIMARY     = "#FFFFFF"   # Texte principal
TEXT_SECONDARY   = "#8B8FA8"   # Texte secondaire, labels
TEXT_MUTED       = "#4A4E6A"   # Texte désactivé, placeholder

# Bordures
BORDER_COLOR     = "#2A2D3E"   # Bordure standard
BORDER_FOCUS     = "#6C63FF"   # Bordure focus (accent)

# Annotations vidéo (rectangles sur les visages)
RECT_COLOR_BGR   = (108, 99, 255)   # Violet électrique en BGR (pour OpenCV)
TEXT_COLOR_BGR   = (255, 255, 255)  # Blanc en BGR
LABEL_BG_BGR     = (26, 29, 39)     # Fond du label nom en BGR


# ══════════════════════════════════════════════════════════════════
#  TYPOGRAPHIE
# ══════════════════════════════════════════════════════════════════

FONT_FAMILY      = "Segoe UI"    # Police principale Windows
FONT_MONO        = "Consolas"    # Police monospace (debug, IP)

FONT_SIZE_XS     = 10
FONT_SIZE_SM     = 12
FONT_SIZE_MD     = 14
FONT_SIZE_LG     = 16
FONT_SIZE_XL     = 20
FONT_SIZE_TITLE  = 28


# ══════════════════════════════════════════════════════════════════
#  DIMENSIONS
# ══════════════════════════════════════════════════════════════════

# Fenêtre principale
WINDOW_MIN_W     = 1100
WINDOW_MIN_H     = 700
WINDOW_DEFAULT_W = 1280
WINDOW_DEFAULT_H = 780

# Sidebar (liste profils reconnus, droite)
SIDEBAR_WIDTH    = 260

# Cartes de profil dans la galerie
CARD_W           = 180
CARD_H           = 220
CARD_THUMB_SIZE  = 100   # Taille de la miniature de la photo

# Boutons
BTN_HEIGHT       = 38
BTN_RADIUS       = 8

# Annotations vidéo
RECT_THICKNESS   = 2
FONT_SCALE_VIDEO = 0.6
FONT_THICKNESS   = 2
LABEL_PADDING    = 6     # Padding autour du texte du label nom


# ══════════════════════════════════════════════════════════════════
#  ICÔNES (texte unicode — fallback si Lucide non disponible)
# ══════════════════════════════════════════════════════════════════

ICON_HOME        = "🎬"
ICON_GALLERY     = "👥"
ICON_ADD         = "➕"
ICON_PLAY        = "▶"
ICON_STOP        = "⏹"
ICON_WEBCAM      = "📷"
ICON_WIFI        = "📡"
ICON_FILE        = "📁"
ICON_PHOTO       = "🖼"
ICON_DELETE      = "🗑"
ICON_EDIT        = "✏"
ICON_CHECK       = "✓"
ICON_UPLOAD      = "⬆"
ICON_PERSON      = "👤"
ICON_LOGO        = "👁"
