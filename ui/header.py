import html

import gradio as gr

from core.application import Application


def create_header(
    application: Application,
) -> gr.HTML:
    """
    Create the main application header.
    """
    name = html.escape(application.name)
    description = html.escape(
        application.description
    )
    version = html.escape(
        application.get_display_version()
    )
    release_date = html.escape(
        str(application.release_date)
    )

    return gr.HTML(
        f"""
        <header class="app-header">
            <div class="app-header__glow"></div>

            <div class="app-header__content">
                <p class="app-header__eyebrow">
                    Local AI image generation
                </p>

                <h1 class="app-header__title">
                    {name}
                </h1>

                <p class="app-header__description">
                    {description}
                </p>

                <div class="app-header__meta">
                    <span class="app-header__badge">
                        <span class="app-header__badge-label">
                            Version
                        </span>

                        <strong>
                            {version}
                        </strong>
                    </span>

                    <span class="app-header__badge">
                        <span class="app-header__badge-label">
                            Released
                        </span>

                        <strong>
                            {release_date}
                        </strong>
                    </span>
                </div>
            </div>
        </header>
        """,
        elem_id="app-header",
    )