from pathlib import Path

import gradio as gr

from core.paths import ASSETS


CSS_FILES: tuple[str, ...] = (
    "tokens.css",
    "base.css",
    "layout.css",
    "components.css",
    "utilities.css",
    "app.css",
)


def create_theme():
    """
    Create the base Gradio theme.

    Most application styling is defined in
    the HUU design system CSS files.
    """
    return gr.themes.Soft(
        primary_hue="zinc",
        secondary_hue="gray",
        neutral_hue="slate",
        radius_size="lg",
        text_size="md",
    )


def load_css() -> str:
    """
    Load and combine the HUU design system
    stylesheets in a deterministic order.
    """
    css_directory = ASSETS / "css"

    stylesheets: list[str] = []

    for filename in CSS_FILES:
        file_path = css_directory / filename

        stylesheet = _read_optional_file(
            file_path=file_path,
        )

        if not stylesheet:
            continue

        stylesheets.append(
            _create_file_section(
                filename=filename,
                content=stylesheet,
            )
        )

    return "\n\n".join(stylesheets)


def load_js() -> str:
    """
    Load optional application JavaScript.
    """
    return _read_optional_file(
        file_path=ASSETS / "js" / "app.js",
    )


def _read_optional_file(
    file_path: Path,
) -> str:
    """
    Read an optional UTF-8 text file.
    """
    if not file_path.exists():
        return ""

    return file_path.read_text(
        encoding="utf-8",
    ).strip()


def _create_file_section(
    filename: str,
    content: str,
) -> str:
    """
    Add a visible separator between combined
    CSS files for easier browser inspection.
    """
    return (
        f"/* ========================================\n"
        f"   {filename}\n"
        f"======================================== */\n\n"
        f"{content}"
    )