# Changelog

## [0.5.0] - 2026-07-21

### Added

- PipelineCache for centralized pipeline caching.
- CheckpointManager for managing local checkpoint files.
- Support for validated local checkpoint resolution.
- ResolvedModelSource abstraction describing runtime model sources.
- ModelAssetResolver integration with CheckpointManager.
- Dependency injection for CheckpointManager.
- Runtime model source validation before generation.
- Source-aware pipeline loading.
- Asset-based model loading support.

### Changed

- Refactored PipelineManager to consume ResolvedModelSource instead of raw model configuration.
- Refactored GenerationEngine to resolve model sources before generator creation.
- GeneratorRegistry now passes resolved runtime sources to generators.
- DiffusersGenerator now consumes validated runtime model sources.
- Bootstrap updated with CheckpointManager dependency.
- ModelAssetResolver became the single authority responsible for model source resolution.

### Fixed

- Eliminated duplicate model path resolution.
- Eliminated duplicated checkpoint validation.
- Eliminated duplicated filesystem checks.
- Unified repository, local path and asset loading workflow.
- Improved dependency separation between model resolution and pipeline loading.

### Architecture

Application

↓

ApplicationContext

↓

GenerationEngine

↓

ModelAssetResolver

↓

ResolvedModelSource

↓

GeneratorRegistry

↓

DiffusersGenerator

↓

PipelineManager

↓

PipelineCache

↓

Diffusers Pipeline


## [0.4.0] - 2026-07-20

### Added

- Fully modular application bootstrap.
- ApplicationContext for dependency management.
- Dependency Injection architecture.
- ModelManager for loading and validating model definitions.
- ModelAssetResolver for resolving model sources.
- AssetManager for future local AI assets.
- Strongly typed `ModelDefinition`.
- Support for `repository_id`, local model paths and checkpoint assets.
- Stable Diffusion 1.5 integration using Hugging Face Diffusers.
- Automatic Stable Diffusion pipeline loading.
- Pipeline validation for Stable Diffusion 1.5.
- Automatic generation metadata using `ModelDefinition`.
- Generator caching inside `GenerationEngine`.

### Changed

- Replaced legacy `repository` with `repository_id`.
- Unified model handling around `ModelDefinition`.
- Refactored `GenerationEngine` into a fully modular workflow.
- Improved model validation before generation.
- Improved bootstrap and dependency registration.
- Output metadata now uses strongly typed models instead of dictionaries.

### Fixed

- Fixed generator registry integration.
- Fixed model serialization inconsistencies.
- Fixed Stable Diffusion pipeline initialization.
- Fixed metadata generation.
- Fixed image output saving.
- Fixed JSON model configuration validation.
- Fixed repository naming consistency across the project.

### Architecture

✔ Bootstrap architecture

✔ ApplicationContext

✔ Dependency Injection

✔ Generator Registry

✔ ModelManager

✔ ModelAssetResolver

✔ AssetManager

✔ Multi-backend architecture

✔ Modular GenerationEngine

✔ Stable Diffusion 1.5 backend

✔ Automatic metadata generation

✔ Generator caching

---

## [0.3.0] - 2026-07-20

### Added

- Generator backend registry.
- Support for multiple generator implementations.
- Pillow diagnostic generator.
- Backend selection through model configuration.
- Generator instance caching by model ID.

### Changed

- `GenerationEngine` no longer depends directly on `DiffusersGenerator`.
- Generator creation is now handled by `GeneratorRegistry`.
- Built-in generators are registered during application bootstrap.

---

## [0.2.0] - 2026-07-19

### Added

- Central `GenerationEngine`.
- `GenerationRequest` DTO.
- `GenerationResult` DTO.
- Automatic image output saving.
- JSON generation metadata.
- Seed, inference steps and guidance scale controls.

### Changed

- Gradio callback became an adapter for the application engine.
- Generators now use structured request and result objects.

---

## [0.1.0] - 2026-07-18

### Added

- Initial Gradio interface.
- Diffusers image generator.
- Stable Diffusion model configuration.
- Resolution configuration.
- First successful local image generation.