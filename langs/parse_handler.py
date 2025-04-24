
# import the build function of the docs parser
from docs.parser import build_parser as build_docs_parser
# import the build function of the commands parser
from commands.parser import build_parser as build_cmd_parser

from docs.lex import build_docs_lex
from commands.lex import build_command_lex

# build parsers
command_parser = build_cmd_parser()
docs_parser = build_docs_parser()

# build lexers
command_lexer = build_command_lex()
docs_lexer = build_docs_lex()


def docs_parse(docs_input: str):
    """
    Using docs parser to parse text.
    :param docs_input: text to parse
    :return: If the text is not empty, return the parse
    result, else return 'NA'
    """
    if not docs_input:
        docs_input = ""

    if docs_input == "":
        return {
            "help": "NA"
        }

    return docs_parser.parse(docs_input, lexer=docs_lexer)


def command_parse(command_input: str):
    """
    Using command parser to parse text
    :param command_input: text to parse
    :return: Result of the command parse
    """
    command_lexer.begin("INITIAL")
    return command_parser.parse(command_input, lexer=command_lexer)


if __name__ == "__main__":
    # parse using command parser
    process = command_parse("hhhh")
    print(process)
    # parse using docs parser
    process = docs_parse(
        """
        <help>
        Hola a todos
        </help>
        """
    )
    print(process)
