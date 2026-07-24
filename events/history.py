from pathlib import Path
from typing import Any

import gradio as gr

from core.dto import HistoryDetails
from core.history import HistoryManager
from ui.history import (
    create_empty_details,
    create_gallery_value,
    create_metadata_paths,
)


def register_history_events(
    history: dict[str, Any],
    history_manager: HistoryManager,
) -> None:
    """
    Register history UI events.
    """
    history["refresh"].click(
        fn=lambda: refresh_history(
            history_manager=history_manager,
            limit=history["limit"],
        ),
        outputs=[
            history["gallery"],
            history["item_paths"],
            history["details"],
            history["selected_metadata_path"],
        ],
    )

    history["gallery"].select(
        fn=select_history_item,
        inputs=[
            history["item_paths"],
        ],
        outputs=[
            history["details"],
            history["selected_metadata_path"],
        ],
    )


def refresh_history(
    history_manager: HistoryManager,
    limit: int,
) -> tuple[
    list[tuple[str, str]],
    list[str],
    str,
    None,
]:
    """
    Reload gallery items and reset the active selection.
    """
    items = history_manager.get_latest(
        limit=limit,
    )

    return (
        create_gallery_value(items),
        create_metadata_paths(items),
        create_empty_details(),
        None,
    )


def select_history_item(
    item_paths: list[str] | None,
    event: gr.SelectData,
    history_manager: HistoryManager,
) -> tuple[str, str | None]:
    """
    Load details for the selected history item.
    """
    if not item_paths:
        return (
            create_error_details(
                "The history is empty.",
            ),
            None,
        )

    selected_index = get_selected_index(
        event=event,
    )

    if selected_index is None:
        return (
            create_error_details(
                "The selected gallery item could not be identified.",
            ),
            None,
        )

    if selected_index < 0 or selected_index >= len(item_paths):
        return (
            create_error_details(
                "The selected history item is no longer available.",
            ),
            None,
        )

    metadata_path = Path(
        item_paths[selected_index],
    )

    details = history_manager.get_details(
        metadata_path=metadata_path,
    )

    if details is None:
        return (
            create_error_details(
                "Generation metadata could not be loaded.",
            ),
            None,
        )

    return (
        create_details_markdown(details),
        str(metadata_path),
    )


def get_selected_index(
    event: gr.SelectData,
) -> int | None:
    """
    Normalize the gallery selection index.
    """
    index = event.index

    if isinstance(index, int):
        return index

    if (
        isinstance(index, tuple)
        and index
        and isinstance(index[0], int)
    ):
        return index[0]

    return None


def create_details_markdown(
    details: HistoryDetails,
) -> str:
    """
    Convert complete history details into Markdown.
    """
    model = details.model_name or details.model_id or "—"
    preset = details.preset_name or details.preset_id or "—"
    scheduler = (
        details.scheduler_name
        or details.scheduler_id
        or "—"
    )

    repository = details.repository_id or "—"
    backend = details.backend or "—"
    mode = details.mode or "—"
    created_at = details.created_at or "—"

    lora_summary = create_lora_summary(
        details.loras,
    )

    input_summary = create_input_summary(
        details,
    )

    prompt = escape_code_block(
        details.prompt or "—",
    )

    negative_prompt = escape_code_block(
        details.negative_prompt or "—",
    )

    return f"""
### Generation

| Property | Value |
|---|---|
| **Created** | {created_at} |
| **Model** | {model} |
| **Repository** | `{repository}` |
| **Backend** | {backend} |
| **Mode** | {mode} |
| **Preset** | {preset} |
| **Scheduler** | {scheduler} |
| **Resolution** | {details.width} × {details.height} |
| **Steps** | {details.steps} |
| **Guidance scale** | {details.guidance_scale:g} |
| **Seed** | `{details.seed}` |
| **Duration** | {details.duration_seconds:.2f} s |
| **LoRA** | {lora_summary} |
| **Input image** | {input_summary} |

### Prompt

```text
{prompt}
```

### Negative prompt

```text
{negative_prompt}
```

### Application

| Property | Value |
|---|---|
| **Name** | {details.application_name or "—"} |
| **Version** | {details.application_version or "—"} |
| **Environment** | {details.application_environment or "—"} |
"""


def create_lora_summary(
    loras: tuple[dict[str, Any], ...],
) -> str:
    """
    Create a readable summary of active LoRAs.
    """
    if not loras:
        return "None"

    summaries: list[str] = []

    for lora in loras:
        name = str(
            lora.get("name")
            or lora.get("id")
            or "Unknown LoRA"
        )

        weight = lora.get(
            "weight",
            lora.get("scale"),
        )

        if weight is None:
            summaries.append(name)
            continue

        summaries.append(
            f"{name} ({weight})",
        )

    return "<br>".join(summaries)


def create_input_summary(
    details: HistoryDetails,
) -> str:
    """
    Create a readable input-image summary.
    """
    if not details.input_used:
        return "Not used"

    summary = "Used"

    if details.strength is not None:
        summary += f", strength {details.strength:g}"

    if details.input_image_path is not None:
        summary += (
            f"<br>`{details.input_image_path.name}`"
        )

    return summary


def create_error_details(
    message: str,
) -> str:
    """
    Create an error message for the details panel.
    """
    return f"""
### Generation details

⚠️ {message}
"""


def escape_code_block(
    value: str,
) -> str:
    """
    Prevent text from prematurely closing a Markdown code block.
    """
    return value.replace(
        "```",
        "``\\`",
    )