from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import toml
from pydantic import BaseModel


class PydanticWriter[PydanticModel: BaseModel](ABC):
    path: Path
    pydantic_cls: type[PydanticModel]

    def __init__(self, path: Path, pydantic_cls: type[PydanticModel]) -> None:
        self.path = path
        self.pydantic_cls = pydantic_cls

    def delete(self) -> None:
        self.path.unlink()

    def exists(self) -> bool:
        """Return if path already exists."""
        return self.path.exists()

    def update_on_disk(self, **update: Any) -> PydanticModel:
        """Update and save to disk."""
        config = self.load()
        update = {key: value for key, value in update.items() if value}
        updated_config = config.model_copy(update=update)
        self.save(updated_config)
        return updated_config

    @abstractmethod
    def load(self) -> PydanticModel: ...

    @abstractmethod
    def save(self, config: PydanticModel) -> None: ...

    def get_str_repr(self) -> str:
        """Return string representation of config."""
        return f"# {self.path}\n{self.path.read_text()}"


class ConfigTomlWriter[PydanticModel: BaseModel](PydanticWriter[PydanticModel]):
    def load(self) -> PydanticModel:
        """Load config from TOML or return defaults if file does not exist."""
        data = toml.load(self.path)
        return self.pydantic_cls(**data)

    def save(self, config: PydanticModel) -> None:
        """Persist the config to TOML on disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            toml.dump(config.model_dump(), f)
