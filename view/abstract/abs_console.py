from abc import ABC, abstractmethod
from logging import Logger

from adapters.observer import Observer
from die_engine.interaction_graph import IGraph
from view.abstract.catcher import Catcher
from view.abstract.renderer import Renderer


class AbsConsole(Observer, Catcher, Renderer, ABC):

    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger

    def catch_loop(self, valid_options: list, prompt: str):
        """
        This method takes a list of options to be accepted and a prompt to get input from the user.
        If the user inputs any of the provided options, the method will return the input.
        In any other case, the method will remain in a loop, waiting for a valid option
        """

        choices = "(" + "/".join(valid_options) + ")"
        valid_options = set(valid_options)

        while True:
            inp = self.catch(prompt=prompt + f" {choices}")
            if inp in valid_options:
                return inp

    @abstractmethod
    def build_visual_graph_struct(self, interaction_graph: IGraph, *args, **kwargs):
        """
        This method is designed to be used when it is necessary
        to build a visual representation of the interaction graph
        """
        pass

    @abstractmethod
    def render_graph(self, *args, **kwargs):
        """
        This method is designed to be used when the interaction graph needs to be visualized
        """
        pass

    @abstractmethod
    def render_dictionary(self, dct: dict, *args, **kwargs):
        """
        This method is designed to be used when the user needs to render
        a dictionary using a specific format through the console.
        """

    @abstractmethod
    def render_list(self, lst: list, *args, **kwargs):
        """
        This method is designed to be used when the user needs to render
        a list using a specific format through the console.
        """

    @property
    def logger(self):
        return self._logger
