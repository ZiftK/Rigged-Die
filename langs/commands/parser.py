from ply import yacc
from lex import tokens
from exceptions import CommandSyntaxException
from .types import CRange, IntervalTypes, CInterval


def p_sentence(p):
    """sentence : VNAME
                | VNAME args
                | VNAME kwargs
                | VNAME args kwargs"""

    p.lexer.begin("INITIAL")
    rtn_dict = {
        "command": p[1],
        "args": [],
        "kwargs": {}
    }

    if len(p) >= 3:

        if type(p[2]) is list:
            rtn_dict["args"] = p[2]
        else:
            rtn_dict["kwargs"] = p[2]

    if len(p) >= 4:
        rtn_dict["kwargs"] = p[3]

    p[0] = rtn_dict

    return p


def p_kwargs(p):
    """kwargs : kwargs kwarg
            | kwarg"""

    kwargs = p[1]

    if len(p) == 3:
        kwargs = {**kwargs, **p[2]}

    p[0] = kwargs

    return p


def p_kwarg(p):
    """kwarg : kwflag
            | kwflag arg"""

    kwarg = {}
    if len(p) == 2:
        kwarg[p[1]] = True

    if len(p) == 3:
        kwarg[p[1]] = p[2]

    p[0] = kwarg

    return p


def p_kwflag(p):
    """kwflag : KWSIGN VNAME"""
    p[0] = p[2]
    return p


def p_args(p):
    """args : args arg
            | arg"""

    args = []
    if len(p) == 2:
        args.append(p[1])

    else:
        args = p[1] + [p[2]]

    p[0] = args

    return p


def p_arg(p):
    """arg : STRING
            | number
            | crange
            | rinterval
            | grinterval"""

    p[0] = p[1]
    return p


def p_crange(p):
    """crange : OPENRANGE number GROUPSPLITTER number GROUPSPLITTER rinterval CLOSERANGE
                | OPENRANGE number GROUPSPLITTER number GROUPSPLITTER number CLOSERANGE
                | OPENRANGE number GROUPSPLITTER number CLOSERANGE"""
    initial_value = p[2]
    final_value = p[4]

    step = p[6] if len(p) > 6 else 1
    p[0] = CRange(initial_value, final_value, step)


def p_grinterval(p):
    """grinterval : GOPENINTERVAL number GROUPSPLITTER number CLOSEINTERVAL"""
    print("Gaaaauuus")
    tp = IntervalTypes.GAUSSIAN
    p[0] = CInterval(p[2], p[4], tp)


def p_rinterval(p):
    """rinterval : OPENINTERVAL number GROUPSPLITTER number CLOSEINTERVAL"""

    is_real = isinstance(p[2], float) or isinstance(p[4], float)
    tp = IntervalTypes.REAL if is_real else IntervalTypes.INTEGER

    p[0] = CInterval(p[2], p[4], tp)


def p_number(p):
    """number : INTEGER
                | FLOAT"""
    p[0] = p[1]


# Error rule for syntax errors
def p_error(p):
    raise CommandSyntaxException("There is a syntax error at the end of the command.")


def build_parser():
    return yacc.yacc()


if __name__ == "__main__":
    pass

    # from test_console.lenguages.command_lenguage.command_lex import lexer

    # data = "val1 g(1:2)"

    # parser = build_parser()
    # res = parser.parse(data, lexer=lexer)
    # print(res)
    # print(res.get("args")[0].generate())
