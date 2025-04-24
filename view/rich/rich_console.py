from logging import Logger

import rich.tree
from rich.console import Console as rConsole

from die_engine.interaction_graph import IGraph
from die_engine.test_node import TestNode
from view.rich.rich_visual_graph import VGraph
from view.abstract.abs_console import AbsConsole

from adapters.observer import event

from view.rich.rich_formatter import format_dict, format_list


class RichConsole(AbsConsole):

    def __init__(self, logger: Logger):
        super().__init__(logger)
        self.__console = rConsole()
        self.__node_path: list = []

        self._v_graph: VGraph | None = None

    @event("update_prompt")
    def update_prompt(self, node_path: list[str]):
        self.__node_path = node_path

    @event("update_dummy")
    def update_dummy(self, index_path: list[int]):
        self._v_graph.move_to(index_path)

    @event("add_child_to_dummy")
    def add_child_to_dummy(self, label: str):
        self._v_graph.add_child(label)

    def render(self, renderable, **config):
        self.__console.print(renderable, **config)
        pass

    def render_dictionary(self,
                          dct: dict,
                          title: str = "",
                          title_style: str = "",
                          jumps_before_title: int = 1,
                          jumps_after_title: int = 2,
                          key_styles: list[str] | None = None,
                          default_text="NA",
                          ident_level: int = 0,
                          jumps_count_after_key: int = 1,
                          ):
        result = format_dict(dct,
                             title=title,
                             title_style=title_style,
                             jumps_before_title=jumps_before_title,
                             jumps_after_title=jumps_after_title,
                             key_styles=key_styles,
                             default_text=default_text,
                             ident_level=ident_level,
                             jump_count_after_key=jumps_count_after_key
                             )
        self.render(result)

    def render_list(self, lst: list,
                    title: str = "",
                    title_style: str = "",
                    jumps_before_title: int = 1,
                    jumps_after_title: int = 2,
                    val_styles: list | None = None,
                    ident_level: int = 0,
                    jumps_after_value: int = 1):

        if not val_styles:
            val_styles = ["white"]

        result = format_list(lst,
                             title=title,
                             title_style=title_style,
                             jumps_before_title=jumps_before_title,
                             jumps_after_title=jumps_after_title,
                             val_styles=val_styles,
                             ident_level=ident_level,
                             jumps_after_value=jumps_after_value)
        self.render(result)

    def catch(self, **kwargs):
        prompt = "[yellow]>[/yellow]".join(self.__node_path)
        prompt = kwargs.pop("prompt", prompt)
        prompt += "[yellow]>[/yellow] "

        return self.__console.input(prompt, **kwargs)

    def build_visual_graph_struct(self, interaction_graph: IGraph, *args, **kwargs):

        self._v_graph = VGraph(interaction_graph.root.sys_name)

        def load_children(t_node: TestNode, r_node: rich.tree.Tree):
            for child in t_node.children:
                label = child.sys_name
                v_child = self._v_graph.create_node_as_child(label)
                r_node.children.append(v_child)
                load_children(child, v_child)

        load_children(interaction_graph.root, self._v_graph.root)

        self._v_graph.set_dummy_highlight_style()

    def render_graph(self, *args, **kwargs):
        current_branch = kwargs.pop("cb", False)

        self.__console.print()
        if current_branch:
            self.render(self._v_graph.dummy)
            self.__console.print()
            return
        self.render(self._v_graph.root)
        self.__console.print()
