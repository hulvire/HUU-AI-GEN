from pathlib import Path

import gradio as gr

from core.dto import HistoryItem
from core.history import HistoryManager


DEFAULT_HISTORY_LIMIT = 16


def create_history(
    history_manager: HistoryManager,
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> dict:
    """
    Create the generation history panel.
    """
    items = history_manager.get_latest(
        limit=limit,
    )

    with gr.Column(
        elem_id="history",
        elem_classes=["huu-panel"],
    ):
        gr.HTML(
            """
            <div class="panel-heading">
                <span class="panel-heading__eyebrow">
                    Archive
                </span>

                <h2 class="panel-heading__title">
                    Generation history
                </h2>
            </div>
            """
        )

        gallery = gr.Gallery(
            value=create_gallery_value(items),
            label="Recent generations",
            columns=4,
            rows=4,
            height="auto",
            object_fit="cover",
            allow_preview=True,
            elem_classes=[
                "history-gallery",
            ],
        )

        refresh = gr.Button(
            value="Refresh history",
            variant="secondary",
            elem_classes=[
                "history-refresh",
            ],
        )

        gr.HTML(
            """
            <div class="panel-heading history-details-heading">
                <span class="panel-heading__eyebrow">
                    Selection
                </span>

                <h3 class="panel-heading__title">
                    Generation details
                </h3>
            </div>
            """
        )

        details = gr.Markdown(
            value=create_empty_details(),
            elem_classes=[
                "history-details",
            ],
        )

    item_paths = gr.State(
        value=create_metadata_paths(items),
    )

    selected_metadata_path = gr.State(
        value=None,
    )

    return {
        "gallery": gallery,
        "refresh": refresh,
        "details": details,
        "item_paths": item_paths,
        "selected_metadata_path": selected_metadata_path,
        "limit": limit,
    }


def create_gallery_value(
    items: list[HistoryItem],
) -> list[tuple[str, str]]:
    """
    Convert history items into Gradio Gallery values.
    """
    return [
        (
            str(item.image_path),
            create_caption(item),
        )
        for item in items
    ]


def create_metadata_paths(
    items: list[HistoryItem],
) -> list[str]:
    """
    Return metadata paths in the same order as gallery items.
    """
    return [
        str(item.metadata_path)
        for item in items
    ]


def create_caption(
    item: HistoryItem,
) -> str:
    """
    Create a compact gallery image caption.
    """
    details = [
        item.model,
        f"{item.width} × {item.height}",
        f"Seed {item.seed}",
    ]

    return " · ".join(
        detail
        for detail in details
        if detail
    )


def create_empty_details() -> str:
    """
    Create the default details panel content.
    """
    return """
Select an image from the generation history to display its metadata.
"""


def normalize_metadata_path(
    value: str,
) -> Path:
    """
    Convert a serialized metadata path back into Path.
    """
    return Path(value)