from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SchedulerDefinition:
    """
    Describes one available diffusion scheduler.
    """

    id: str
    name: str

    class_name: str

    enabled: bool = True
    default: bool = False

    description: str = ""

    configuration: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "SchedulerDefinition":
        """
        Create a scheduler definition from JSON data.
        """
        scheduler = cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            class_name=str(
                data.get("class_name", "")
            ).strip(),
            enabled=bool(
                data.get("enabled", True)
            ),
            default=bool(
                data.get("default", False)
            ),
            description=str(
                data.get("description", "")
            ).strip(),
            configuration=dict(
                data.get("configuration", {})
            ),
            metadata=dict(
                data.get("metadata", {})
            ),
        )

        scheduler.validate()

        return scheduler

    def validate(self) -> None:
        """
        Validate scheduler configuration.
        """
        if not self.id:
            raise ValueError(
                "Scheduler ID cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "Scheduler name cannot be empty."
            )

        if not self.class_name:
            raise ValueError(
                "Scheduler class name cannot be empty."
            )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the definition into JSON-compatible data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "class_name": self.class_name,
            "enabled": self.enabled,
            "default": self.default,
            "description": self.description,
            "configuration": dict(
                self.configuration
            ),
            "metadata": dict(
                self.metadata
            ),
        }