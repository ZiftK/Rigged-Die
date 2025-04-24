import inspect

from langs.parse_handler import docs_parse


def command(command_name: str):
    """
    Register the function as a command for TestConsole
    :param command_name: name of the command
    :return: function
    """

    def decorator(func):
        set_command_params(command_name, func)
        return func

    return decorator


def set_command_params(command_name: str, function: callable):
    function.is_command = True
    function.command_name = command_name


def compare_args(function: callable, args: tuple):
    """
    Check that the length of the parameter list being
    passed to a function is equal to the length of the
    parameter list the function receives
    :param function: function to compare args
    :param args: The args being passed
    :return: Difference between real args count and passed args
    count
    """
    args = list(args)
    real_args = []
    # count mandatory params
    for param_name, param in inspect.signature(function).parameters.items():
        if param.default != param.empty:
            continue
        real_args.append(param_name)

    s = {"args", "kwargs"}
    for i, arg in enumerate(real_args):
        if arg in s:
            real_args.pop(i)

    args.pop(0)
    real_args.pop(0)
    return len(real_args) - len(args), real_args, args


# TODO: refact this shit
def compare_args_types(function: callable, args: tuple):
    real_types: list[tuple[str:type]] = []
    wrong_types: list[tuple[str:type:type]] = []
    for param_name, param in inspect.signature(function).parameters.items():
        if param.default != param.empty:
            continue
        real_types.append((param_name, param.annotation))

    if real_types[0][0] == "self":
        real_types = real_types[1:]
        args = args[1:]

    for i, a in enumerate(args):
        if not isinstance(a, real_types[i][1]):
            # add: real param name, passed argument type, real param type
            wrong_types.append((real_types[i][0], a.__class__, real_types[i][1]))

    return wrong_types


# TODO: refact this shit
def compare_kwargs_types(function: callable, kwargs: dict):
    real_types: dict = {}
    wrong_types: list[tuple[str:type:type]] = []
    for param_name, param in inspect.signature(function).parameters.items():
        if param.default == param.empty:
            continue
        real_types[param_name] = param.annotation

    for key, value in kwargs.items():
        if not isinstance(value, real_types.get(key)):
            # add: real param name, passed argument type, real param type
            wrong_types.append((key, value.__class__, real_types[key]))

    return wrong_types


def compare_kwargs(function: callable, kwargs: dict):
    """
    Check that the passed kwargs match the kwargs that the function receives
    :param function: function to check
    :param kwargs: key word arguments
    :return: True if each kwarg passed is in the function options, and
    returns the wrong kwargs passed.
    """

    # real kwargs passed
    real_kwargs = []
    for param_name, param in inspect.signature(function).parameters.items():
        if param.default == param.empty:
            continue
        real_kwargs.append(param_name)

    real_kwargs = set(real_kwargs)
    wrong_kwargs = [passed_arg for passed_arg in kwargs if not (passed_arg in real_kwargs)]
    return not len(wrong_kwargs) > 0, wrong_kwargs


def collect_commands(hierarchy: list):
    """
        Recovery all functions that use the command decorator
        """

    commands = {}

    for clss in hierarchy:
        # get commands of each class in hierarchy

        # inspect class methods
        class_methods = inspect.getmembers(clss, inspect.isfunction)

        # for each method
        for method in class_methods:

            call = method[1]

            # if is decorated using @command
            if hasattr(call, "command_name"):
                docs = call.__doc__
                docs = docs_parse(docs)

                class_name = str(clss.__name__)
                commands.setdefault(class_name, {})
                commands.get(class_name).setdefault(
                    call.command_name,
                    {
                        "callable": call,
                        "docs": docs
                    }
                )

    return commands
