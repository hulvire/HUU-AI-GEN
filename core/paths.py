from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "config"

MODELS = ROOT / "models"
PRESETS = ROOT / "presets"

OUTPUTS = ROOT / "outputs"
ASSETS = ROOT / "assets"
LOGS = ROOT / "logs"

RESOLUTION_CONFIGS = CONFIG / "resolutions"

SCHEDULER_CONFIGS = CONFIG / "schedulers"

MODEL_ASSETS = ASSETS / "models"

LORAS = ROOT / "loras"

CHECKPOINTS = MODEL_ASSETS / "checkpoints"
LORAS = MODEL_ASSETS / "loras"
VAE = MODEL_ASSETS / "vae"
EMBEDDINGS = MODEL_ASSETS / "embeddings"
CONTROLNET = MODEL_ASSETS / "controlnet"
UPSCALERS = MODEL_ASSETS / "upscalers"
MODEL_CACHE = MODEL_ASSETS / "cache"