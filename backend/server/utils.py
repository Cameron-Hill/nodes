import re
from typing import TypedDict
from dataclasses import dataclass

REGEX_OPERATORS = ["^", "$", "*", "+", "?", "{", "}", "[", "]", "(", ")", "|", "."]
SINGE_CHAR_REGEX_OPERATORS = ["*", "+", "?", "."]
GROUPED_CHAR_REGEX_OPERATORS = {"{": "}", "[": "]", "(": ")"}
SPREAD_CHAR_REGEX_OPERATORS = ["|"]
REGEX_ESCAPE_CHAR = "\\"
REGEX_META_CHARS = "AbBdDfnrsStvwWzZ"


def _tokenize_single_char_operators(regex: str, token: str) -> str:
    pattern = r"(?<!\\)[\.\*\?\+]"  # Match any of the single char operators if they do not precede a backslash
    return re.sub(pattern, token, regex)


def _tokenize_meta_chars(regex: str, token: str) -> str:
    pattern = r"(?<!\\)\\[AbBdDfnrsStvwWzZ]"  # Match any of the single char operators if they do not precede a backslash
    return re.sub(pattern, token, regex)


def _tokenize_grouped_char_operators(regex: str, token: str) -> str:
    chars = list(regex)
    escaped = False
    target: str | None = None
    for i, char in enumerate(chars):
        if target:
            chars[i] = token
            if char == target:
                target = None
        elif not escaped and char in GROUPED_CHAR_REGEX_OPERATORS:
            chars[i] = token
            target = GROUPED_CHAR_REGEX_OPERATORS[char]

        elif char == REGEX_ESCAPE_CHAR:
            escaped = True
        else:
            escaped = False
    return "".join(chars)


def _tokenize_spread_operator(regex: str, token: str) -> str:
    """If all groups have already been remove, then we refuse to take into account any spread operator."""
    if any(x in regex for x in SPREAD_CHAR_REGEX_OPERATORS):
        return token * len(regex)
    return regex


def tokenize_regex_operators(regex: str, token: str) -> str:
    regex = _tokenize_grouped_char_operators(regex, token)
    regex = _tokenize_single_char_operators(regex, token)
    regex = _tokenize_meta_chars(regex, token)
    regex = _tokenize_spread_operator(regex, token)
    return regex


def regex_escape(regex: str) -> str:
    regex = regex.replace(r"\\", "~escaped~backslash~")
    regex = regex.replace("\\", "")
    regex = regex.replace("~escaped~backslash~", "\\")
    return regex


@dataclass
class RegexLiterals:
    literals: list[str]
    startswith: str | None
    endswith: str | None
    contains: list[str]


def get_literals_from_regex(regex: str) -> RegexLiterals:
    regex = regex.lstrip("^").rstrip("$")
    tokenized = tokenize_regex_operators(regex, "@@@")
    regex = regex_escape(regex)
    tokenized = regex_escape(tokenized)
    literals = [x for x in tokenized.split("@@@") if x]
    startswith = literals[0] if literals and regex.startswith(literals[0]) else None
    endswith = literals[-1] if literals and regex.endswith(literals[-1]) else None
    contains = literals.copy()
    if startswith:
        contains.pop(0)
    if endswith and contains:
        contains.pop(-1)

    return RegexLiterals(
        literals=literals,
        startswith=startswith,
        endswith=endswith,
        contains=contains,
    )
