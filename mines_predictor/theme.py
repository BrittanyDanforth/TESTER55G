"""Visual theme for the Mines Detector GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# Stake-inspired dark palette
COLORS = {
    "bg": "#0f212e",
    "bg_deep": "#0a1620",
    "panel": "#1a2c38",
    "panel_elevated": "#213743",
    "border": "#2f4553",
    "border_focus": "#557086",
    "text": "#ffffff",
    "text_secondary": "#b1bad3",
    "muted": "#6b7c8f",
    "accent": "#00e700",
    "accent_hover": "#1fff20",
    "accent_dim": "#0d3314",
    "danger": "#ff4d4d",
    "demo": "#ffb800",
    "demo_bg": "#2a2208",
    "cell_hidden": "#2f4553",
    "cell_hidden_fg": "#6b7c8f",
    "cell_mine_bg": "#3d1a1a",
    "cell_mine_border": "#ff4d4d",
    "cell_safe_bg": "#0d2818",
    "cell_safe_border": "#00e700",
    "input_bg": "#0f212e",
    "input_disabled": "#1a2c38",
    "pill_bg": "#0f212e",
    "primary_btn_fg": "#0f212e",
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 10),
    "section": ("Segoe UI", 11, "bold"),
    "label": ("Segoe UI", 9),
    "body": ("Segoe UI", 10),
    "mono": ("Consolas", 10),
    "cell": ("Segoe UI", 16, "bold"),
    "stat_big": ("Segoe UI", 22, "bold"),
    "button": ("Segoe UI", 11, "bold"),
    "button_sm": ("Segoe UI", 9),
}

CELL_GAP = 5
CELL_PAD = 14
LEFT_PANEL_WIDTH = 320


def configure_styles(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["panel"])

    style.configure(
        "Card.TLabelframe",
        background=COLORS["panel"],
        foreground=COLORS["text_secondary"],
        bordercolor=COLORS["border"],
        borderwidth=1,
        relief="flat",
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=FONTS["section"],
        padding=(4, 0, 4, 6),
    )

    style.configure("TLabel", background=COLORS["panel"], foreground=COLORS["text_secondary"])
    style.configure("Bg.TLabel", background=COLORS["bg"], foreground=COLORS["text_secondary"])
    style.configure("Field.TLabel", background=COLORS["panel"], foreground=COLORS["muted"], font=FONTS["label"])

    style.configure(
        "Primary.TButton",
        font=FONTS["button"],
        padding=(12, 10),
        background=COLORS["accent"],
        foreground=COLORS["primary_btn_fg"],
        borderwidth=0,
        focuscolor=COLORS["accent"],
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["accent_hover"]), ("disabled", COLORS["border"])],
        foreground=[("disabled", COLORS["muted"])],
    )

    style.configure(
        "Ghost.TButton",
        font=FONTS["button_sm"],
        padding=(10, 8),
        background=COLORS["panel_elevated"],
        foreground=COLORS["text_secondary"],
        borderwidth=0,
    )
    style.map(
        "Ghost.TButton",
        background=[("active", COLORS["border"])],
        foreground=[("active", COLORS["text"])],
    )

    style.configure(
        "Demo.TCheckbutton",
        background=COLORS["bg"],
        foreground=COLORS["demo"],
        font=FONTS["body"],
        padding=(8, 4),
    )
    style.map("Demo.TCheckbutton", background=[("active", COLORS["bg"])])

    return style
