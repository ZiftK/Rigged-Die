import inspect
from types import UnionType

from exceptions import (NodeAlreadyInitializedException,
                                                  NodeAlreadyHasContentException,
                                                  UninitializedNodeException,
                                                  SaveContentException,
                                                  ArgsCountDifferenceException,
                                                  KwArgsDifferenceException,
                                                  InitializeNodeException,
                                                  GenerateContentException, WrongTypesException
                                                  )

from command_handler import compare_args, compare_kwargs, set_command_params, compare_kwargs_types, \
    compare_args_types


def persistent(function):
    """
    Marking any method as persistent makes the
    TestNodeBuilder class interpret it as a persistent special method.
    """
    function.is_persistent = True
    return function


def update_wrapper(wrapper, function):
    for attr_name, attr_val in vars(function).items():
        setattr(wrapper, attr_name, attr_val)


def set_init_to_true(function):
    def init_node(*args, **kwargs):
        instance = args[0]

        if instance.check_is_init():
            raise NodeAlreadyInitializedException()

        val = function(*args, **kwargs)

        if not isinstance(val, dict):
            raise InitializeNodeException("The initialize_node method must return the build "
                                          "parameters set by the user, and it must also be a dictionary ")

        instance_build_params = getattr(instance, "_build_params", {})
        setattr(instance, f"_build_params", {**instance_build_params, **val})

        instance.status_values["is_init"] = True
        instance.write_meta_data_files()

        return val

    return init_node


def set_generate_to_true(function):
    def generate_content(*args, **kwargs):
        instance = args[0]

        conditional = instance.check_has_content()
        conditional = conditional and not instance.multi_content
        conditional = conditional and not instance.regenerate_content
        if conditional:
            raise NodeAlreadyHasContentException()

        if not instance.check_is_init():
            raise UninitializedNodeException()

        val = function(*args, **kwargs)

        if val is None or val is False:
            raise GenerateContentException()

        instance.status_values["has_content"] = True
        instance.write_status_values()

        instance._content = val
        instance.save_content()

        return val

    return generate_content


def set_content_load_field(function):
    def load_content(*args, **kwargs):
        instance = args[0]

        val = function(*args, **kwargs)

        if val is None or val is False:
            raise SaveContentException()

        setattr(instance, f"_content", val)
        return val

    return load_content


def add_compare_args(function):
    def wrapper(*args, **kwargs):

        difference, real_args, passed_args = compare_args(function, args)
        args_text = "'" + "', '".join(real_args) + "'"
        if difference > 0:
            raise ArgsCountDifferenceException(f"The following arguments are mandatory: {args_text}"
                                               f". Only {len(passed_args)} of {len(real_args)} were passed.")

        if difference < 0:
            difference = abs(difference)
            txt = "argument was" if difference == 1 else "arguments were"
            raise ArgsCountDifferenceException(f"Only the following arguments were expected: {args_text},"
                                               f" but {difference} extra {txt} passed.")

        # ------- Keyword Arguments compare
        check, wrong_kwargs = compare_kwargs(function, kwargs)

        if not check:
            raise KwArgsDifferenceException(f"The following kwargs were not expected: {wrong_kwargs}")

        wrong_types = compare_args_types(function, args)
        wrong_types += compare_kwargs_types(function, kwargs)

        if wrong_types:
            ex_string = "The following arguments have an incorrect type: "
            for real_param_name, passed_argument_type, real_param_type in wrong_types:
                ex_string += f"'{real_param_name}' is {passed_argument_type} "
                ex_string += f"and should be {real_param_type}, "

            ex_string = ex_string[:-2]

            raise WrongTypesException(ex_string)

        val = function(*args, **kwargs)
        return val

    return wrapper


def set_persistent_methods(function, name):
    wrapper = function
    if name == "init_node":
        wrapper = set_init_to_true(function)

    elif name == "generate_content":
        wrapper = set_generate_to_true(function)

    elif name == "load_content":
        wrapper = set_content_load_field(function)
    return wrapper


class TestNodeBuilder(type):

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if bases:  # if class have any base class
            # recovery last class in hierarchy
            parent_namespace = vars(bases[-1])

            # conserve command decorations
            for attr_name, attr_value in parent_namespace.items():

                if callable(attr_value) and getattr(attr_value, "is_persistent", False):

                    method = namespace[attr_name]
                    docs = method.__doc__

                    if getattr(attr_value, "is_command", False):
                        method = add_compare_args(method)

                    method = set_persistent_methods(method, attr_name)

                    # dump function content in wrapper
                    update_wrapper(method, attr_value)  # copy fields
                    method.__signature__ = inspect.signature(attr_value)

                    method.__doc__ = docs
                    setattr(cls, attr_name, method)

            for attr_name, attr_value in namespace.items():

                if getattr(attr_value, "is_command", False):
                    method = add_compare_args(attr_value)
                    # dump function content in wrapper
                    update_wrapper(method, attr_value)  # copy fields
                    method.__signature__ = inspect.signature(attr_value)

                    method.__doc__ = attr_value.__doc__
                    setattr(cls, attr_name, method)