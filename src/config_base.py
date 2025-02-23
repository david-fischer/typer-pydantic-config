from pathlib import Path
from typing import Any, ClassVar, Self

import toml
from pydantic import BaseModel


class ConfigBase(BaseModel):
    config_path: ClassVar[Path]

    @classmethod
    def load(cls) -> Self:
        """Load config from TOML or return defaults if file does not exist."""
        data = toml.load(cls.config_path)
        return cls(**data)

    def save(self) -> None:
        """Persist the config to TOML on disk."""
        with self.config_path.open("w", encoding="utf-8") as f:
            toml.dump(self.model_dump(), f)

    @classmethod
    def update_on_disk(cls, **update: Any) -> Self:
        """Update and save to disk."""
        config = cls.load()
        update = {key: value for key, value in update.items() if value}
        updated_config = config.model_copy(update=update)
        updated_config.save()
