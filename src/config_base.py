from pathlib import Path
from typing import Any, ClassVar, Self

import toml
from platformdirs import user_config_path
from pydantic import BaseModel


class ConfigBase(BaseModel):
    app_name: ClassVar[str]
    app_version: ClassVar[str | None] = None

    @classmethod
    def config_path(cls) -> Path:
        return user_config_path(appname=cls.app_name, version=cls.app_version) / "config.toml"

    @classmethod
    def exists(cls) -> bool:
        return cls.config_path().exists()

    @classmethod
    def load(cls) -> Self:
        """Load config from TOML or return defaults if file does not exist."""
        data = toml.load(cls.config_path())
        return cls(**data)

    def save(self) -> None:
        """Persist the config to TOML on disk."""
        self.config_path().parent.mkdir(parents=True, exist_ok=True)
        with self.config_path().open("w", encoding="utf-8") as f:
            toml.dump(self.model_dump(), f)

    @classmethod
    def update_on_disk(cls, **update: Any) -> Self:
        """Update and save to disk."""
        config = cls.load()
        update = {key: value for key, value in update.items() if value}
        updated_config = config.model_copy(update=update)
        updated_config.save()
