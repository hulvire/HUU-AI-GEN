from collections.abc import Iterator
from contextlib import contextmanager
from html import escape

import gradio as gr


@contextmanager
def collapsible_section(
    section_id: str,
    title: str,
    *,
    open_by_default: bool = False,
) -> Iterator[None]:
    """
    Create a custom collapsible sidebar section.

    Unlike gr.Accordion, the section content remains
    inside a regular Gradio Column.
    """
    section_classes = [
        "huu-collapsible",
    ]

    if open_by_default:
        section_classes.append(
            "is-open"
        )

    safe_title = escape(title)

    with gr.Column(
        elem_id=f"{section_id}-section",
        elem_classes=section_classes,
    ):
        gr.HTML(
            f"""
            <button
                type="button"
                class="huu-collapsible__trigger"
                aria-expanded="{
                    str(open_by_default).lower()
                }"
            >
                <span class="huu-collapsible__title">
                    {safe_title}
                </span>

                <span
                    class="huu-collapsible__icon"
                    aria-hidden="true"
                >
                    <svg
                        viewBox="0 0 24 24"
                        width="18"
                        height="18"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="m6 9 6 6 6-6"></path>
                    </svg>
                </span>
            </button>
            """
        )

        with gr.Column(
            elem_id=f"{section_id}-content",
            elem_classes=[
                "huu-collapsible__content",
            ],
        ):
            yield