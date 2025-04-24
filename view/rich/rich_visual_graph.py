from collections import deque

from rich.console import RenderableType
from rich.tree import Tree

from adapters.observer import event


class VGraph:

    def __init__(self,
                 label: RenderableType,
                 guide_style: str = "white",
                 node_style: str = "white",
                 current_node_style: str = "cyan",
                 ):

        self._guide_style: str = guide_style
        self._node_style: str = node_style
        self._current_node_style: str = current_node_style

        self._root: Tree = Tree(
            label,
            guide_style=self._guide_style,
            style=node_style
        )
        self._dummy = self._root

    def add_child(self, child_label: str, goto=False):

        child = Tree(
            child_label,
            style=self._node_style,
            guide_style=self._guide_style
        )

        self._dummy.children.append(child)

    def create_node_as_child(self, label: str):
        return Tree(
            label,
            style=self._node_style,
            guide_style=self._guide_style
        )

    def __set_dummy_default_style(self):
        self._dummy.style = self._node_style

    def set_dummy_highlight_style(self):
        self._dummy.style = self._current_node_style
        for child in self._dummy.children:
            child.style = self._node_style

    @event("update_dummy")
    def move_to(self, node_index_path: list[int]):
        """
        """

        # check out 1
        if not node_index_path:
            return

        self.__set_dummy_default_style()

        # check out 2
        if node_index_path == "root":
            self._dummy = self._root
            self.set_dummy_highlight_style()  # todo: implementar protocolo (estos son los casos de protocolo)
            return

        # move to node
        while node_index_path:
            index = node_index_path.pop(0)
            self._dummy = self._dummy.children[index]

        self.set_dummy_highlight_style()

    @property
    def root(self):
        return self._root

    @property
    def dummy(self):
        return self._dummy

#
# a = Tree("r", style="cyan bold")
# a.add("c", highlight=True)
# a.add("b")
# a.children[0].add("d")
#
# console = Console()
# console.print(a)
