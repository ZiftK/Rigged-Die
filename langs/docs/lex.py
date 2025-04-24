from collections import deque

import re

from ply import lex

from enum import Enum


def delete_duplicate_ws(string: str):
    """
    :param string: string to clear
    :return: string without duplicate withe spaces
    """
    string = string.strip()

    string = " ".join(string.split())
    return string


state_stack = []

is_open_label = True
next_state = ""
pre_label_state = ""


def get_pre_label_state() -> str:
    return pre_label_state


labels = {
    "help": "HELPLABEL",
    "param": "PARAMLABEL",
    "optional": "OPTIONLABEL",
    "choice": "CHOICELABEL"
}

param_assigns = {
    "name": "NAMEASSIGN",
    "type": "TYPEASSIGN",
}


choice_assigns = {
    "cvalue": "CHOICEASSIGNVALUE"
}

assigns = {
    **param_assigns,
    **choice_assigns
}

reserved = {
    **labels,
    **assigns
}

states = (
    ("terminator", "exclusive"),
    ("label", "exclusive"),
    ("help", "exclusive"),
    ("param", "inclusive"),
    ("optional", "inclusive"),
    ("assign", "inclusive"),
    ("choice", "inclusive")
)

tokens = [
             "LEFTLABEL",
             "RIGHTLABEL",
             "TMLABEL",
             "WORD",
             "TEXT",
             "LEFTASSIGNLABEL",
             "SPLITASSIGNLABEL",
             "RIGHTASSIGNLABEL",
             "FLOAT",
             "INTEGER",
         ] + list(reserved.values())

t_INITIAL_terminator_label_ignore = "[ ]+"
t_help_ignore = ""


def t_label_terminator_assign_WORD(t):
    r"""[a-zA-Z_][a-zA-Z_\d]+"""

    # if the match word is reserved
    if t.value in reserved:
        # switch token type
        t.type = reserved.get(t.value)

    # select the global var
    global next_state

    # set the next state as the label
    if t.value in labels:
        next_state = t.value

    # if is a label terminator
    if t.lexer.current_state() == "terminator":
        next_state = state_stack.pop()

    return t


def t_ANY_LEFTLABEL(t):
    r"""<"""
    global pre_label_state

    # recovery the lexer state before
    # enter in label state
    pre_label_state = t.lexer.current_state()

    t.lexer.begin("label")
    return t


def t_label_terminator_RIGHTLABEL(t):
    r""">"""

    # if the lexer is in the label state
    # add current label state to stack
    if t.lexer.current_state() == "label":
        state_stack.append(pre_label_state)

    t.lexer.begin(next_state)

    return t


def t_label_TMLABEL(t):
    r"""/"""
    t.lexer.begin("terminator")
    return t


def t_param_optional_choice_LEFTASSIGNLABEL(t):
    r""":<"""
    global pre_label_state
    pre_label_state = t.lexer.current_state()

    t.lexer.begin("assign")

    return t


def t_assign_SPLITASSIGNLABEL(t):
    r""":"""
    return t


def t_assign_RIGHTASSIGNLABEL(t):
    r""">:"""
    t.lexer.begin(pre_label_state)
    return t


def t_assign_FLOAT(t):
    r"""\d+\.\d+|\.\d+"""
    t.value = float(t.value)
    return t


def t_assign_INTEGER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


def t_assign_LOR(t):
    r"""\|"""
    return t


def t_help_TEXT(t):
    r"""[\w\.,:/\?\¿\!\¡_\s\"\';\-\{\}\[\]\%&$#\+\*\(\)\|\\=^~]+"""
    t.value = delete_duplicate_ws(t.value)
    return t


def t_ANY_NEWLINE(t):
    r"""\n+"""
    t.lexer.lineno += 1


def t_ANY_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    return t


def build_docs_lex():
    return lex.lex()



