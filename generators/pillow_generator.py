import random
import secrets
import textwrap
import time
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from core.dto import GenerationRequest, GenerationResult
from generators.base import BaseGenerator
from core.models import ModelDefinition


class PillowGenerator(BaseGenerator):
    """
    Lightweight diagnostic generator based on Pillow.

    This backend does not use artificial intelligence. Its purpose is
    to verify backend registration, generator switching, seed handling,
    output saving, and application architecture.
    """

    def __init__(
        self,
        model: ModelDefinition,
    ) -> None:
        self.model = model

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        if request.width is None or request.height is None:
            raise ValueError(
                "Generation resolution has not been resolved."
            )

        used_seed = (
            int(request.seed)
            if request.seed is not None
            else secrets.randbelow(2_147_483_647)
        )

        random_generator = random.Random(used_seed)

        started_at = time.perf_counter()

        image = self._create_image(
            request=request,
            random_generator=random_generator,
            used_seed=used_seed,
        )

        duration_seconds = round(
            time.perf_counter() - started_at,
            3,
        )

        return GenerationResult(
            image=image,
            seed=used_seed,
            duration_seconds=duration_seconds,
            model_id=self.model.id,
            model_name=self.model.name,
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
        )

    def _create_image(
        self,
        request: GenerationRequest,
        random_generator: random.Random,
        used_seed: int,
    ) -> Image.Image:
        width = request.width
        height = request.height

        if width is None or height is None:
            raise ValueError(
                "Image dimensions are missing."
            )

        background = self._random_color(
            random_generator
        )

        image = Image.new(
            mode="RGB",
            size=(width, height),
            color=background,
        )

        draw = ImageDraw.Draw(
            image,
            mode="RGB",
        )

        self._draw_shapes(
            draw=draw,
            width=width,
            height=height,
            random_generator=random_generator,
        )

        self._draw_information(
            draw=draw,
            request=request,
            used_seed=used_seed,
            width=width,
            height=height,
        )

        return image

    def _draw_shapes(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
        random_generator: random.Random,
    ) -> None:
        shape_count = max(
            10,
            min(40, width // 32),
        )

        for _ in range(shape_count):
            x1 = random_generator.randint(
                0,
                max(0, width - 1),
            )

            y1 = random_generator.randint(
                0,
                max(0, height - 1),
            )

            shape_width = random_generator.randint(
                max(10, width // 20),
                max(20, width // 3),
            )

            shape_height = random_generator.randint(
                max(10, height // 20),
                max(20, height // 3),
            )

            x2 = min(
                width,
                x1 + shape_width,
            )

            y2 = min(
                height,
                y1 + shape_height,
            )

            color = self._random_color(
                random_generator
            )

            shape_type = random_generator.choice(
                [
                    "ellipse",
                    "rectangle",
                ]
            )

            if shape_type == "ellipse":
                draw.ellipse(
                    (x1, y1, x2, y2),
                    fill=color,
                )
            else:
                draw.rectangle(
                    (x1, y1, x2, y2),
                    fill=color,
                )

    def _draw_information(
        self,
        draw: ImageDraw.ImageDraw,
        request: GenerationRequest,
        used_seed: int,
        width: int,
        height: int,
    ) -> None:
        font = ImageFont.load_default()

        padding = max(
            12,
            width // 40,
        )

        panel_height = min(
            height // 2,
            170,
        )

        panel_top = height - panel_height

        draw.rectangle(
            (
                0,
                panel_top,
                width,
                height,
            ),
            fill=(20, 20, 20),
        )

        prompt_width = max(
            20,
            width // 11,
        )

        wrapped_prompt = textwrap.fill(
            request.prompt,
            width=prompt_width,
        )

        text = (
            f"HUU-AI-GEN diagnostic backend\n"
            f"Generator: PillowGenerator\n"
            f"Seed: {used_seed}\n"
            f"Resolution: {width} x {height}\n"
            f"Prompt: {wrapped_prompt}"
        )

        draw.multiline_text(
            (
                padding,
                panel_top + padding,
            ),
            text,
            fill=(255, 255, 255),
            font=font,
            spacing=5,
        )

    @staticmethod
    def _random_color(
        random_generator: random.Random,
    ) -> tuple[int, int, int]:
        return (
            random_generator.randint(20, 235),
            random_generator.randint(20, 235),
            random_generator.randint(20, 235),
        )