from ply import yacc
from lex import (
    delete_duplicate_ws,
    state_stack,
    param_assigns,
    choice_assigns,
    get_pre_label_state,
    tokens)


def sign(p, flag):
    print("-" * 5, " ", flag, " ", "-" * 5, end="\n\n")
    print("State: ", p.lexer.current_state())
    print("\nasignado: ", p[0], "\n")
    for i in range(1, len(p)):
        print(f"p[{i}]= {p[i]}", f" - {p.slice[i].type}", end="\n")
    print("\n")
    print("-" * (12 + len(flag)))
    print()


param_count = 0

current_rule = ""


def p_docs(p):
    """docs : helplabel
            | helplabel params
            | params helplabel
            | params
            | helplabel optionals params
            | params helplabel optionals
            | optionals params helplabel
            | helplabel params optionals
            | params optionals helplabel
            | optionals helplabel params
            | optionals helplabel
            | helplabel optionals
            | optionals params
            | params optionals
            | optionals"""
    global current_rule
    current_rule = "docs"
    p[0] = {}

    for t in p[1:]:
        p[0] = {**p[0], **t}


def p_optionals(p):
    """optionals : optionals optional
                | optional"""
    global current_rule
    current_rule = "optionals"

    dct = p[1]

    for t in p[2:]:
        dct = {**dct, **t}

    dct = {**dct.pop("optionals", {}), **dct}
    p[0] = {
        "optionals": dct
    }


def p_optional(p):
    """optional : openoptionallabel paramcontent closeoptionallabel"""
    global current_rule
    current_rule = "optional"

    name = p[2].pop("name", None)
    if not name:
        raise Exception("Option label must contain name assigment")

    p[0] = {
        name: p[2]
    }


def p_openoptionallabel(p):
    """openoptionallabel : LEFTLABEL OPTIONLABEL RIGHTLABEL"""
    p[0] = p[2]


def p_closeoptionallabel(p):
    """closeoptionallabel : LEFTLABEL TMLABEL OPTIONLABEL RIGHTLABEL"""
    p[0] = p[2]


def p_params(p):
    """params : params paramlabel
            | paramlabel"""
    global current_rule
    current_rule = "params"

    dct = p[1]

    for t in p[2:]:
        dct = {**dct, **t}

    dct = {**dct.pop("params", {}), **dct}
    p[0] = {
        "params": dct
    }


def p_paramlabel(p):
    """paramlabel : openparamlabel paramcontent closeparamlabel"""
    global current_rule
    current_rule = "paramlabel"

    name = p[2].pop("name", None)

    if not name:
        raise Exception("Param label must contain name assigment")

    p[0] = {
        name: p[2]
    }


def p_openparamlabel(p):
    """openparamlabel : LEFTLABEL PARAMLABEL RIGHTLABEL"""
    global current_rule
    current_rule = "openparamlabel"

    p[0] = p[2]


def p_closeparamlabel(p):
    """closeparamlabel : LEFTLABEL TMLABEL PARAMLABEL RIGHTLABEL"""
    global current_rule
    current_rule = "closeparamlabel"
    p[0] = p[3]


# param label content
def p_paramcontent(p):
    """paramcontent : paramcontent paramcontentvalues
                    | paramcontentvalues"""
    global current_rule
    current_rule = "paramcontent"

    p[0] = {}
    choices = {}

    for t in p[1:]:
        p[0] = {**p[0], **t}

    # ------------ unpacking choices
    # type parser assigment as a dictionary
    dct: dict = p[0]

    # recovery choices and the choices descriptions
    cd = [(choice, dct[choice]) for choice in dct.keys() if choice.count("choice-") > 0]

    # delete the original choice in parser assigment
    # and create new dictionary using the new choices keys
    for choice, description in cd:
        dct.pop(choice)
        choice = choice.replace("choice-", "")
        choices[choice] = description

    # the first time, "choices" not exists in parser assigment, also
    # we need to set empty dictionary as default value of
    # "choices" key
    p[0].setdefault("choices", {})

    # apply union operation to new choices and old
    # choices
    p[0]["choices"] = {**p[0]["choices"], **choices}

    if len(p[0].get("choices")) == 0:
        p[0].pop("choices")


def p_paramcontentvalues(p):
    """paramcontentvalues : assigns
                            | helplabel
                            | choicelabel"""
    global current_rule
    current_rule = "paramcontentvalues"

    p[0] = p[1]


def p_choicelabel(p):
    """choicelabel : openchoicelabel choicelabelcontent closechoicelabel"""
    global current_rule
    current_rule = "choicelabel"

    p[0] = p[2]


def p_openchoicelabel(p):
    """openchoicelabel : LEFTLABEL CHOICELABEL RIGHTLABEL"""
    global current_rule
    current_rule = "openchoicelabel"

    p[0] = p[2]


def p_closechoicelabel(p):
    """closechoicelabel : LEFTLABEL TMLABEL CHOICELABEL RIGHTLABEL"""
    global current_rule
    current_rule = "closechoicelabel"

    p[0] = p[3]


# choice label content
def p_choicelabelcontent(p):
    """choicelabelcontent : choicelabelcontent choicelabelcontentvalues
                            | choicelabelcontentvalues"""
    global current_rule
    current_rule = "choicelabelcontent"

    dct: dict = {}

    for t in p[1:]:
        dct = {**dct, **t}

    h = dct.pop("help", None)
    if h:
        dct[list(dct.keys())[0]] = h
    p[0] = dct


def p_choicelabelcontentvalues(p):
    """choicelabelcontentvalues : assigns
                                | helplabel"""
    global current_rule
    current_rule = "choicelabelcontentvalues"

    p[0] = p[1]


def p_assigns(p):
    """assigns : assigns assign
                    | assign"""
    global current_rule
    current_rule = "assigns"

    dct = {}
    for t in p[1:]:
        t = {} if not t else t
        dct = {**dct, **t}

    p[0] = dct


def p_assign(p):
    """assign : LEFTASSIGNLABEL assignlabel SPLITASSIGNLABEL assignvalue RIGHTASSIGNLABEL"""
    global current_rule
    current_rule = "assign"

    current_state = get_pre_label_state()
    assign = p[2]

    if current_state == "param":
        if not (assign in param_assigns):
            raise Exception(f"Invalid assigment {assign}, must be the following{', '.join(list(param_assigns.keys()))}")

        p[0] = {p[2]: p[4]}

    if current_state == "optional":
        if not (assign in param_assigns):
            raise Exception(f"Invalid assigment {assign}, must be the following{', '.join(list(param_assigns.keys()))}")

        p[0] = {p[2]: p[4]}

    if current_state == "choice":
        if not (assign in choice_assigns):
            raise Exception(
                f"Invalid assigment {assign}, must be the following{', '.join(list(choice_assigns.keys()))}")

        p[0] = {"choice-" + p[4]: ""}



def p_assignlabel(p):
    """assignlabel : NAMEASSIGN
                    | TYPEASSIGN
                    | CHOICEASSIGNVALUE"""
    global current_rule
    current_rule = "assignlabel"

    p[0] = p[1]


def p_assignvalue(p):
    """assignvalue : FLOAT
                        | INTEGER
                        | WORD"""
    global current_rule
    current_rule = "assignvalue"

    p[0] = p[1]


def p_helplabel(p):
    """helplabel : openhelplabel multitext closehelplabel"""
    global current_rule
    current_rule = "helplabel"

    p[0] = {
        "help": p[2]
    }


def p_openhelplabel(p):
    """openhelplabel : LEFTLABEL HELPLABEL RIGHTLABEL"""
    global current_rule
    current_rule = "openhelplabel"

    p[0] = p[2]


def p_closehelplabel(p):
    """closehelplabel : LEFTLABEL TMLABEL HELPLABEL RIGHTLABEL"""
    global current_rule
    current_rule = "closehelplabel"

    p[0] = p[3]


def p_multitext(p):
    """multitext : multitext TEXT
                | TEXT"""
    global current_rule
    current_rule = "multitext"

    p[0] = delete_duplicate_ws(" ".join(p[1:]))


# syntax error
def p_error(p):
    global current_rule
    if p:
        if p.type == "LOPEN":
            print(f"Unexpected label <{p.value}>")
            print(p.lexer.lexdata[:p.lexpos + 1] + f"<{p.value}> <---")
        else:
            print("ERROR INFO")
            print(f"Execute rule: {current_rule}")
            print(f"Last label state: {get_pre_label_state()}")
            print(f"State: {p.lexer.current_state()}")
            print(f"VALUE: {p.value}")
            print(f"STACK: {state_stack}")
            lines = [f"{i + 1}\t{line}" for i, line in enumerate(p.lexer.lexdata[:p.lexpos].split("\n"))]
            lines = "\n".join(lines)
            print("\n" + lines + f"{p.value} <--- {p.type}")
            print(f"\nline {p.lineno}\n")
    else:
        print(f"Execute rule: {current_rule}")
        print(f"Last label state: {get_pre_label_state()}")
        print(f"STACK: {state_stack}")
        print("Syntax error at EOF")


def build_parser():
    return yacc.yacc()


if __name__ == "__main__":
    # data = """
    #     <help>
    #         Prueba
    #         de
    #         ayuda 1
    #     </help>
        
    #     <optional>
    #         :<name: cname>:
    #         :<type: string>:
    #     </optional>
    #     """
    # from test_console.lenguages.docs_lenguage.docs_lex import build_docs_lex

    # print(data)
    # out = build_parser().parse(data, lexer=build_docs_lex())
    # print(out)
    pass