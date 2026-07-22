from pathlib import Path

import gradio as gr

from core.paths import ASSETS


def create_theme() -> gr.Theme:
    """
    Create the visual theme used by HUU-AI-GEN.
    """
    return gr.themes.Soft(
        primary_hue="zinc",
        secondary_hue="gray",
        neutral_hue="slate",
        radius_size="lg",
    )


def load_css() -> str:
    """
    Load the application CSS from assets/css/app.css.

    Returns an empty string when the stylesheet does not exist,
    so the application can still start.
    """
    css_path: Path = ASSETS / "css" / "app.css"

    if not css_path.exists():
        return ""

    return css_path.read_text(
        encoding="utf-8",
    )

    