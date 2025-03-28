from typing import Any

import pytest
from syrupy import SnapshotAssertion

from typer_pydantic_config.dict_utils import flatten_dict, unflatten_dict


@pytest.fixture
def nested() -> dict[str, Any]:
    return {
        "user": {"name": "Alice", "location": {"city": "Wonderland", "zip": "12345"}},
        "active": True,
    }


@pytest.fixture
def flat() -> dict[str, str]:
    return {"test.xyz": "asdlfkj.", "xyz.test": ".asldfkj", "test.ab": "zsdf"}


def test_flatten(snapshot: SnapshotAssertion, nested: dict[str, Any]) -> None:
    snapshot.assert_match(flatten_dict(nested))


def test_unflatten(snapshot: SnapshotAssertion, flat: dict[str, Any]) -> None:
    snapshot.assert_match(unflatten_dict(flat))


def test_unflatten_deep(snapshot: dict[str, Any]) -> None:
    snapshot.assert_match(unflatten_dict({"a.s.df.a.gasdfg.a.s.d.f": "2"}))


def test_flatten_unflatten(nested: dict[str, Any]) -> None:
    assert nested == unflatten_dict(flatten_dict(nested))


def test_unflatten_flatten(flat: dict[str, Any]) -> None:
    assert flat == flatten_dict(unflatten_dict(flat))
