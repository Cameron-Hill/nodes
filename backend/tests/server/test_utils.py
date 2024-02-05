import pytest
from server.utils import (
    get_literals_from_regex,
    _tokenize_grouped_char_operators,
)


x = ["abc\\abc", "ab[c\\a]bc", "ab\\", ""]


@pytest.mark.parametrize(
    "regex, expected",
    [
        (r"abc\abc", r"abc\abc"),
        (r"ab[c\a]bc", r"ab*****bc"),
        (r"abc[asd]=asd[abasd]l(as[asd])asd", r"abc*****=asd*******l*********asd"),
        (r"abc\[de]fg", r"abc\[de]fg"),
    ],
)
def test_tokenize_grouped_char_operators(regex, expected):
    assert _tokenize_grouped_char_operators(regex, token="*") == expected


@pytest.mark.parametrize(
    "regex, startswith, endswith, contains, literals",
    [
        (r"^abc", "abc", "abc", [], ["abc"]),
        (r"^a.b", "a", "b", [], ["a", "b"]),
        (r"^a.*b", "a", "b", [], ["a", "b"]),
        (r"^a.*?b", "a", "b", [], ["a", "b"]),
        (r"a.*?b", "a", "b", [], ["a", "b"]),
        (r"hello\-[a-z]", "hello-", None, [], ["hello-"]),
        (r"^hello\-[a-z]$", "hello-", None, [], ["hello-"]),
        (r"[a-z]", None, None, [], []),
        (r".*", None, None, [], []),
        (r"\d{4}-hello", None, "-hello", [], ["-hello"]),
        (r"\.\d{4}-hello", ".", "-hello", [], [".", "-hello"]),
        (r"^\.\*\?\-hello$", ".*?-hello", ".*?-hello", [], [".*?-hello"]),
        (r"abc[123]xyz", "abc", "xyz", [], ["abc", "xyz"]),
        (r"[123]abc[as]xyz", None, "xyz", ["abc"], ["abc", "xyz"]),
        # test backslash
        (r"abc\\abc", "abc\\abc", "abc\\abc", [], ["abc\\abc"]),
        (r"ab[c\\a]bc", "ab", "bc", [], ["ab", "bc"]),
        (r"ab\\", "ab\\", "ab\\", [], ["ab\\"]),
        (r"ab\d", "ab", None, [], ["ab"]),
        (r"", None, None, [], []),
    ],
)
def test_get_literals_from_regex(
    regex: str,
    startswith: str | None,
    endswith: str | None,
    contains: list[str],
    literals: list[str],
):
    literal = get_literals_from_regex(regex)
    assert literal.startswith == startswith
    assert literal.endswith == endswith
    assert literal.contains == contains
    assert literal.literals == literals
