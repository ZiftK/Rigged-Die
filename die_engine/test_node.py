from abc import abstractmethod
from data_engine.checks import dump_json_in_file, read_json_from_file
from die_engine.exceptions import (
    UnlinkingExceptionException,
    UninitializedNodeException)

from die_engine.command_handler import command

from die_engine.test_node_builder import TestNodeBuilder, persistent


class TestNode(metaclass=TestNodeBuilder):
    _prefix: str = ""
    _suffix: str = ""
    _sys_ns: str = "-"

    _build_params_file_name = ".bp"
    _status_values_file_name = ".sv"

    multi_content: bool = False
    regenerate_content: bool = False

    def __init__(self,
                 label: str,
                 **kwargs):
        """

        :param build_params:
        :param kwargs:
        """
        self.status_values: dict = {
            "is_init": False,
            "has_content": False
        }

        self._parent_build_params = None
        self._parent_content = None

        self._content = None
        self._content_stack: list = []
        self._build_params: dict = {}

        self._sys_path: str | None = kwargs.get("initial_path", None)
        self._label: str = label

        # build system name using prefix and suffix

        sn = self._prefix + self._sys_ns + label if self._prefix != "" else label
        sn = sn + self._sys_ns + self._suffix if self._suffix != "" else sn
        self._sys_name: str = sn

        # tree values
        self._children: list[TestNode] = []
        self._children_labels: set = set()

    # --------- Operator Override ---------

    def __str__(self):
        s = "**** Self values\n\n"
        s += f"Label: {self.label}\n"
        s += f"Prefix: {self.prefix}\n"
        s += f"Suffix: {self.suffix}\n"
        s += f"System name: {self.sys_name}\n"
        s += f"System path: {self.sys_path}\n"
        s += f"Status values: {self.status_values}\n"

        s += "\n\n**** Build params\n"
        s += str(self.build_params)

        if self._parent_build_params:
            s += "\n\n**** Parent build params\n"
            s += str(self._parent_build_params)

        return s

    # --------- Class methods ---------

    @classmethod
    def create(cls, label: str, **kwargs):
        """
        :return: An instance of TestNodePattern
        """
        return cls(label, **kwargs)

    # --------- Node methods ---------

    def add_child(self, child):

        if not self.check_is_init():
            raise UninitializedNodeException("The node must be initialized to create children")

        # typing parent
        child_node: TestNode = child

        # add child node to children list
        self._children.append(child_node)
        # merge self values with child values
        child_node.merge_values(self)

        # add label to children labels
        self._children_labels.add(child.label)

    def get_content_by_level(self, level: int):
        return self._content_stack[level]

    def set_content_stack(self, content_stack: list):
        self._content_stack = content_stack

    def merge_values(self, parent):
        """
            Fetches the transmission values from the parent node.
            :param parent: node parent
        """
        # typing parent
        parent_node: TestNode = parent

        self._parent_build_params = parent_node.build_params
        self._parent_content = parent_node.content

        # merge build params
        self._build_params = {**parent_node.build_params, **self.build_params}
        # extend system path
        self._sys_path = parent.sys_path + "\\" + self._sys_name

    # ------------ Check methods ------------

    def __check_path(self):
        if not self._sys_path:
            raise UnlinkingExceptionException("The current node is not linked to any path in the system.")

    def check_is_init(self):
        return self.status_values.get("is_init")

    def check_has_content(self):
        return self.status_values.get("has_content")

    # ------------ WR methods ------------
    def load_build_params(self):
        self.__check_path()
        path = f"{self._sys_path}\\{self._build_params_file_name}"
        self._build_params = read_json_from_file(path)

    def write_build_params(self):
        self.__check_path()
        path = f"{self._sys_path}\\{self._build_params_file_name}"
        dump_json_in_file(path, self._build_params)

    def load_status_values(self):
        self.__check_path()
        path = f"{self._sys_path}\\{self._status_values_file_name}"
        self.status_values = read_json_from_file(path)

    def write_status_values(self):
        self.__check_path()
        path = f"{self._sys_path}\\{self._status_values_file_name}"
        dump_json_in_file(path, self.status_values)

    def write_meta_data_files(self):
        self.write_status_values()
        self.write_build_params()

    def load_meta_data(self):
        self.load_status_values()
        self.load_build_params()

    def release_memory(self):
        self.status_values = None
        self._build_params = None
        self._content_stack = None

    # ------------ Abstract methods ------------
    @abstractmethod
    @persistent
    def load_content(self):
        """
        Loads node content into memory

        Warning
        ------
        This method is already decorated with @command,
        it is not necessary to decorate it again;
        however, it is recommended to document it using tag format.
        """

    @abstractmethod
    @persistent
    def save_content(self):
        """
        Dumps node content from memory to permanent file

        Warning
        ------
        This method is already decorated with @command,
        it is not necessary to decorate it again;
        however, it is recommended to document it using tag format.
        """

    def release_content(self):
        self._parent_build_params = None
        self._parent_content = None

        self._content = None
        self._build_params = None

    @abstractmethod
    @persistent
    @command("gen")
    def generate_content(self, *args, **kwargs):
        """
        Generate node content

        Warning
        ------
        This method is already decorated with @command,
        it is not necessary to decorate it again;
        however, it is recommended to document it using tag format.
        """

    @abstractmethod
    @persistent
    @command("init")
    def init_node(self, *args, **kwargs):
        """
        Initialize node. This method must take the
        initialization parameters as arguments.

        Warning
        ------
        This method is already decorated with @command,
        it is not necessary to decorate it again;
        however, it is recommended to document it using tag format.
        """

    @abstractmethod
    @persistent
    @command("sc")
    def show_content(self, *args, **kwargs):
        """
        Shows node content

        Warning
        ------
        This method is already decorated with @command,
        it is not necessary to decorate it again;
        however, it is recommended to document it using tag format.
        """

    # ------------ Switch between states ------------

    def on_enter_node(self, parent=None, load_content=True):

        try:
            self.load_meta_data()
        except FileNotFoundError:
            self.write_meta_data_files()
        pass
        if parent:
            self.merge_values(parent)

        if self.status_values.get("has_content", False) and load_content:
            self.load_content()

    def on_leave_node(self):
        self.release_memory()
        pass

    # ------------ Properties ------------
    @property
    def sys_path(self):
        """
            :return: Node path in the OS
            """
        return self._sys_path

    @property
    def sys_name(self):
        return self._sys_name

    @property
    def build_params(self):
        """
            :return: Build params of the node
            """
        return self._build_params

    @property
    def label(self):
        """
            :return: Label for the node path
            """
        return self._label

    @property
    def children(self):
        """
            :return: Node children
            """
        return self._children

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def sys_node_splitter(self) -> str:
        return self._sys_ns

    @property
    def content(self):
        return self._content

    @property
    def parent_content(self):
        return self._parent_content

    @property
    def parent_build_params(self):
        return self._parent_build_params

    @property
    def children_labels(self):
        return self._children_labels
