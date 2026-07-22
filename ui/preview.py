import gradio as gr


def create_preview() -> dict:
    with gr.Column(scale=7, elem_id="preview"):
        gr.Markdown("## 🖼️ Preview")

        image = gr.Image(
            label="Generated Image",
            height=700,
        )

        status = gr.Textbox(
            label="Generation Status",
            lines=6,
            interactive=False,
        )

    return {
        "image": image,
        "status": status,
    }