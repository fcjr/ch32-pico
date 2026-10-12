# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""Small S-expression reader for auditing generated KiCad data."""
import json
import re


class Atom(str):
    pass


def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack = [[]]
    for token in tokens:
        if token == '(':
            child = []
            stack[-1].append(child)
            stack.append(child)
        elif token == ')':
            if len(stack) == 1:
                raise ValueError('Unexpected closing parenthesis')
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else Atom(token))
    if len(stack) != 1 or len(stack[0]) != 1:
        raise ValueError('Unbalanced or multiple S-expressions')
    return stack[0][0]


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def one(node, key):
    values = children(node, key)
    if len(values) != 1:
        raise ValueError(f'Expected one {key}, got {len(values)}')
    return values[0]


def dump(node):
    if isinstance(node, list):
        # KiCad node keys and enum values are atoms. Pad numbers are strings.
        return '(' + str(node[0]) + ''.join(' ' + dump(x) for x in node[1:]) + ')'
    if isinstance(node, Atom):
        return str(node)
    return json.dumps(node)
