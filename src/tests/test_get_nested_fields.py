from pydantic import BaseModel
from syrupy import SnapshotAssertion

from typer_pydantic_config.click_utils import (
    get_flat_fields,
    get_nested_fields,
    update_pydantic_model_command,
)


class Inner(BaseModel):
    value: int
    name: str


class NestedModel(BaseModel):
    some_bool: bool
    value: int
    inner: Inner


def test_nested_pydantic_model(snapshot: SnapshotAssertion) -> None:
    snapshot.assert_match(get_nested_fields(NestedModel))


def test_nested_pydantic_model_flattened(snapshot: SnapshotAssertion) -> None:
    snapshot.assert_match(get_flat_fields(NestedModel))


def test_nested_pydantic_model_flattened_(snapshot: SnapshotAssertion) -> None:
    snapshot.assert_match(
        update_pydantic_model_command(NestedModel, lambda _: None).params
    )
