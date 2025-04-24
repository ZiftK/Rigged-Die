from ply import lex

from langs.commands.exceptions import CommandSyntaxException

tokens = [
    "VNAME",
    "KWSIGN",
    "INTEGER",
    "FLOAT",
    "STRING",
    "OPENRANGE",
    "CLOSERANGE",
    "OPENINTERVAL",
    "GOPENINTERVAL",
    "CLOSEINTERVAL",
    "GROUPSPLITTER",
    "MINUS"
]

t_INITIAL_command_ignore_WS = r"[\s\t]+"
t_range_interval_GROUPSPLITTER = r":"
states = [
    ("command", "exclusive"),
    ("range", "exclusive"),
    ("interval", "exclusive")

]

last_state = "INITIAL"


def t_command_range_OPENINTERVAL(t):
    r"""\("""
    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("interval")
    return t


def t_command_range_GOPENINTERVAL(t):
    r"""g\("""
    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("interval")
    return t


def t_interval_CLOSEINTERVAL(t):
    r"""\)"""
    global last_state
    aux = last_state
    last_state = t.lexer.current_state()
    t.lexer.begin(aux)
    return t


def t_command_OPENRANGE(t):
    r"""\["""
    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("range")
    return t


def t_range_CLOSERANGE(t):
    r"""\]"""
    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("command")
    return t


def t_INITIAL_VNAME(t):
    r"""[A-Za-z_][A-Za-z\-0-9_]*"""
    t.value = t.value.replace("-", "_")

    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("command")
    return t


def t_command_KWSIGN(t):
    r"""--"""
    global last_state
    last_state = t.lexer.current_state()
    t.lexer.begin("INITIAL")
    return t


def t_command_range_interval_INTEGER(t):
    r"""(?<!\.)\b\d+\b(?!\.)|(?<!\.)-\b\d+\b(?!\.)"""
    t.value = int(t.value)
    return t


def t_command_range_interval_FLOAT(t):
    r"""\d+\.\d+|\.\d+|\-\d+\.\d+ |\-\.\d+|\d+f"""
    t.value = t.value.replace("f", "") if t.value.count("f") > 0 else t.value
    t.value = float(t.value)
    return t


def t_command_STRING(t):
    r"""[\w\.,:/\?\¿\!\¡_]+|\"[\w\.,:/\?\¿\!\¡_\s]*\"|\'[\w\.,:/\?\¿\!\¡_\s]*\'"""
    t.value = t.value.replace("\"", "")
    t.value = t.value.replace("'", "")
    return t


def t_INITIAL_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_ANY_error(t):
    line = f"{t.lexer.lexdata[:t.lexpos]} ----> {t.lexer.lexdata[t.lexpos:].strip()} <----"
    raise CommandSyntaxException(f"There is a unexpected token at: {line}")


def build_command_lex():
    return lex.lex()


lexer = build_command_lex()

if __name__ == "__main__":
    data = "mvt p1 (0:1) [1:0]"
    lexer.input(data)
    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
    pass
