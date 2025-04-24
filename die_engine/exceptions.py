class NodeIsNotInitException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnlinkingExceptionException(Exception):

    def __init__(self, message):
        super().__init__(message)


class UninitializedNodeException(Exception):

    def __init__(self, message="The node must be initialized before generating its content"):
        super().__init__(message)


class NodeAlreadyInitializedException(Exception):

    def __init__(self, message="The node is already initialized"):
        super().__init__(message)


class NodeAlreadyHasContentException(Exception):

    def __init__(self, message="The node already has content"):
        super().__init__(message)


class SaveContentException(Exception):

    def __init__(self, message="The node content can't be null. The generate_content method must return the generated "
                               "content."):
        super().__init__(message)


class ArgsCountDifferenceException(Exception):
    def __init__(self, message="There is a difference in the count of arguments"):
        super().__init__(message)


class KwArgsDifferenceException(Exception):
    def __init__(self, message="There is a difference between the kwargs passed and those expected"):
        super().__init__(message)


class InitializeNodeException(Exception):
    def __init__(self, message="The method init_node must return a True value to confirm that "
                               "the initialization has been successful"):
        super().__init__(message)


class GenerateContentException(Exception):
    def __init__(self, message="The method generate_content must return a content object to confirm that "
                               "the initialization has been successful"):
        super().__init__(message)
        
    
class WrongTypesException(Exception):
    def __init__(self, message):
        super().__init__(message)
