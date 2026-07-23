from typing import Any

from core.models import ModelManager


def register_model_events(
    sidebar: dict[str, Any],
    model_manager: ModelManager,
) -> None:
    """
    Register events triggered by model selection changes.
    """

    def resolve_generation_defaults(
        model_id: str,
    ) -> tuple[int, float]:
        model = model_manager.require(
            model_id
        )

        defaults = model.generation_defaults

        steps = int(
            defaults.get(
                "steps",
                20,
            )
        )

        guidance_scale = float(
            defaults.get(
                "guidance_scale",
                7.0,
            )
        )

        return (
            steps,
            guidance_scale,
        )

    sidebar["model"].change(
        fn=resolve_generation_defaults,
        inputs=[
            sidebar["model"],
        ],
        outputs=[
            sidebar["steps"],
            sidebar["guidance_scale"],
        ],
    )