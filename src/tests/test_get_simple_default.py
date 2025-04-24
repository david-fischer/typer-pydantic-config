from typing import Any

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from typer_pydantic_config.prompt_utils import get_simple_default


def get_field_info(model_cls: BaseModel, field_name: str) -> FieldInfo:
    return model_cls.model_fields[field_name]


def test_returns_equals_default() -> None:
    class ModelWithEqualsDefault(BaseModel):
        a: int = 10

    field_info = get_field_info(ModelWithEqualsDefault, "a")
    assert get_simple_default(field_info) == snapshot(10)


def test_calls_default_factory() -> None:
    class ModelWithFactory(BaseModel):
        b: list = Field(default_factory=list)

    field_info = get_field_info(ModelWithFactory, "b")
    result = get_simple_default(field_info)
    assert isinstance(result, list)
    assert result == []


def test_returns_none_when_no_default() -> None:
    class ModelWithoutDefault(BaseModel):
        c: str

    field_info = get_field_info(ModelWithoutDefault, "c")
    assert get_simple_default(field_info) is None


def test_raises_on_validated_factory() -> None:
    def factory_with_validated_data(values: dict[str, Any]) -> str:
        return values.get("something", "fallback")

    class ModelWithValidatedFactory(BaseModel):
        d: str = Field(default_factory=factory_with_validated_data)

    field_info = get_field_info(ModelWithValidatedFactory, "d")
    with pytest.raises(NotImplementedError) as e:
        get_simple_default(field_info)
    assert e.type == snapshot(NotImplementedError)
    assert str(e.value) == snapshot(
        "Default factories with arguments are not supported in typer-pydantic-config."
    )


def test_field_default_is_respected() -> None:
    class ModelWithFieldDefault(BaseModel):
        e: str = Field(default="explicit")

    field_info = get_field_info(ModelWithFieldDefault, "e")
    assert get_simple_default(field_info) == "explicit"
