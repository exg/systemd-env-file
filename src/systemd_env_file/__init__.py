# SPDX-License-Identifier: LGPL-2.1-or-later

import re
from enum import Enum, auto
from io import StringIO
from typing import IO, Final

KEY_RE: Final = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
NEWLINE: Final = "\n\r"
WHITESPACE: Final = " \t\n\r"


class State(Enum):
    PRE_KEY = auto()
    KEY = auto()
    PRE_VALUE = auto()
    VALUE = auto()
    VALUE_ESCAPE = auto()
    SINGLE_QUOTE_VALUE = auto()
    DOUBLE_QUOTE_VALUE = auto()
    DOUBLE_QUOTE_VALUE_ESCAPE = auto()
    COMMENT = auto()
    COMMENT_ESCAPE = auto()


def load(f: IO[str]) -> dict[str, str]:
    env = {}
    state = State.PRE_KEY
    key = ""
    key_has_trailing_ws = False
    value = ""
    value_has_trailing_ws = False
    while True:
        c = f.read(1)
        if not c:
            break

        match state:
            case State.PRE_KEY:
                if c in "#;":
                    state = State.COMMENT
                elif c not in WHITESPACE:
                    state = State.KEY
                    key = c

            case State.KEY:
                if c in NEWLINE:
                    state = State.PRE_KEY
                    key = ""
                elif c == "=":
                    state = State.PRE_VALUE
                else:
                    key += c
                    key_has_trailing_ws = c in WHITESPACE

            case State.PRE_VALUE:
                if c in NEWLINE:
                    state = State.PRE_KEY
                    if key_has_trailing_ws:
                        key_has_trailing_ws = False
                        key = key.rstrip()
                    if value_has_trailing_ws:
                        value_has_trailing_ws = False
                        value = value.rstrip()
                    env[key] = value
                    key = ""
                    value = ""
                elif c == "'":
                    state = State.SINGLE_QUOTE_VALUE
                elif c == '"':
                    state = State.DOUBLE_QUOTE_VALUE
                elif c == "\\":
                    state = State.VALUE_ESCAPE
                elif c not in WHITESPACE:
                    state = State.VALUE
                    value = c

            case State.VALUE:
                if c in NEWLINE:
                    state = State.PRE_KEY
                    if key_has_trailing_ws:
                        key_has_trailing_ws = False
                        key = key.rstrip()
                    if value_has_trailing_ws:
                        value_has_trailing_ws = False
                        value = value.rstrip()
                    env[key] = value
                    key = ""
                    value = ""
                elif c == "\\":
                    state = State.VALUE_ESCAPE
                else:
                    value += c
                    value_has_trailing_ws = c in WHITESPACE

            case State.VALUE_ESCAPE:
                state = State.VALUE
                if c not in NEWLINE:
                    value += c

            case State.SINGLE_QUOTE_VALUE:
                if c == "'":
                    state = State.PRE_VALUE
                else:
                    value += c

            case State.DOUBLE_QUOTE_VALUE:
                if c == '"':
                    state = State.PRE_VALUE
                elif c == "\\":
                    state = State.DOUBLE_QUOTE_VALUE_ESCAPE
                else:
                    value += c

            case State.DOUBLE_QUOTE_VALUE_ESCAPE:
                state = State.DOUBLE_QUOTE_VALUE
                if c in '"\\`$':
                    value += c
                elif c != "\n":
                    value += "\\"
                    value += c

            case State.COMMENT:
                if c == "\\":
                    state = State.COMMENT_ESCAPE
                elif c in NEWLINE:
                    state = State.PRE_KEY

            case State.COMMENT_ESCAPE:
                if c in NEWLINE:
                    state = State.PRE_KEY
                else:
                    state = State.COMMENT

    if state in {
        State.PRE_VALUE,
        State.VALUE,
        State.VALUE_ESCAPE,
        State.SINGLE_QUOTE_VALUE,
        State.DOUBLE_QUOTE_VALUE,
        State.DOUBLE_QUOTE_VALUE_ESCAPE,
    }:
        if key_has_trailing_ws:
            key = key.rstrip()
        if state == State.VALUE and value_has_trailing_ws:
            value = value.rstrip()
        env[key] = value

    for key in env:
        if not KEY_RE.match(key):
            raise ValueError(f"Invalid variable name: {key}")

    return env


def loads(s: str) -> dict[str, str]:
    f = StringIO(s)
    f.seek(0)
    return load(f)
