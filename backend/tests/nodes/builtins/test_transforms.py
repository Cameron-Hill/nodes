from nodes.builtins import transforms
from contextlib import contextmanager
from inspect import isclass
from typing import Any
import pytest
from pydantic import ValidationError


@contextmanager
def expect_exception(exception_or_any):
    exception_class = isclass(exception_or_any) and (
        issubclass(exception_or_any, Exception) or exception_or_any == Exception
    )
    if exception_class or isinstance(exception_or_any, Exception):
        with pytest.raises(exception_or_any) as e:  # type: ignore
            yield e
    else:
        yield None


@pytest.mark.parametrize(
    "kwargs, expected_output",
    [
        [
            {"string_a": "abc", "string_b": "xyz", "options": {"delimiter": ""}},
            "abcxyz",
        ],
        [
            {"string_a": "abc", "string_b": "xyz", "options": {"delimiter": "-"}},
            "abc-xyz",
        ],
        [
            {"string_a": "abc", "string_b": "xyz"},
            "abcxyz",
        ],
        [
            {"string_a": "abc", "string_b": "xyz", "options": {}},
            "abcxyz",
        ],
        [
            {"string_a": "abc", "string_b": "xyz", "options": None},
            "abcxyz",
        ],
        [{"string_a": None, "string_b": "xyz", "options": None}, ValidationError],
    ],
)
def test_string_concat_transform(kwargs: dict, expected_output: str | Exception):
    with expect_exception(expected_output):
        string_concat = transforms.StringConcat()
        assert string_concat.call(**kwargs) == expected_output
