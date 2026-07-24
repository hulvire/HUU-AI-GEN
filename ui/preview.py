import gradio as gr


def create_preview() -> dict:
    """
    Create the generated image preview panel.
    """
    with gr.Column(
        scale=7,
        elem_id="preview",
        elem_classes=["huu-panel"],
    ):
        gr.HTML(
            """
            <div class="panel-heading">
                <span class="panel-heading__eyebrow">
                    Output
                </span>

                <h2 class="panel-heading__title">
                    Preview
                </h2>
            </div>
            """
        )

        image = gr.Image(
            label="Generated image",
            height=700,
            elem_classes=[
                    "preview-image",
                ],
        )

        status = gr.Textbox(
            label="Generation status",
            lines=6,
            interactive=False,
            elem_classes=[
                    "preview-image-status",
                ],
        )

    return {
        "image": image,
        "status": status,
    }