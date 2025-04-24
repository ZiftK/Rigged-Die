from typing import Type

from die_engine.test_node import TestNode

from adapters.observer import Observable, Observer


class IGraphEvents:
    UPDATE_PROMPT = "update_prompt"
    UPDATE_DUMMY = "update_dummy"
    ADD_CHILD_TO_DUMMY = "add_child_to_dummy"


class IGraph(Observable):

    def __init__(self,
                 label: str,
                 hierarchy: list[Type[TestNode]],
                 stg_path: str,
                 observers: list[Observer] | Observer | None = None
                 ):
        """
        """
        super().__init__(observers)

        self._hierarchy = hierarchy
        self._root: TestNode = self._hierarchy[0].create(label, initial_path=stg_path)

        # init valid properties
        self._init_hierarchy_level: int = 1
        self._init_current_path: list = [self.root.label]
        self._init_dummy: TestNode = self._root

        # interaction state
        self._hierarchy_level: int = self._init_hierarchy_level
        self._current_path: list = self._init_current_path[:]
        self._dummy: TestNode = self._init_dummy

        # last valid properties
        self._last_hierarchy_level: int | None = None
        self._last_dummy: TestNode | None = None
        self._last_current_path: list | None = None
        self._last_content_stac: list | None = None

        # super content stack
        self._content_stack = []

        # throw events
        self.notify_observers(IGraphEvents.UPDATE_PROMPT, self._current_path)

    def __check_next_node_hierarchy(self):
        """
        Check if the next level of hierarchy is valid
        """
        if self._hierarchy_level < len(self._hierarchy):
            return
        raise IndexError("Maximum hierarchy level reached")

    def __save_interaction_state(self):
        self._last_hierarchy_level = self._hierarchy_level
        self._last_current_path = self._current_path[:]
        self._last_dummy = self._dummy
        self._last_content_stack = self._content_stack

    def __recovery_last_interaction_state(self):
        self._hierarchy_level = self._last_hierarchy_level
        self._current_path = self._last_current_path
        self._dummy = self._last_dummy
        self._content_stack = self._last_content_stack

        # clear state
        self._last_dummy = None
        self._last_hierarchy_level = None
        self._last_current_path = None
        self._last_content_stack = None

        # notify
        self.notify_observers(IGraphEvents.UPDATE_PROMPT, self._current_path)

    def __recovery_init_interaction_state(self):
        self._dummy = self._init_dummy
        self._current_path = self._init_current_path[:]
        self._hierarchy_level = self._init_hierarchy_level
        self._content_stack.clear()

        # notify
        self.notify_observers(IGraphEvents.UPDATE_PROMPT, self._current_path)
        self.notify_observers(IGraphEvents.UPDATE_DUMMY, "root")

    def __get_child_class(self):
        # recovery dummy class
        clss = self._dummy.__class__
        index = self._hierarchy.index(clss) + 1

        return self._hierarchy[index]

    def add_child_to_dummy(self, child_name: str):

        # exceptions
        self.__check_next_node_hierarchy()

        clss = self.__get_child_class()

        child = clss.create(child_name)
        self._dummy.add_child(child)

        self.notify_observers(IGraphEvents.ADD_CHILD_TO_DUMMY, child_name)
        return child

    def move_to_node(self, path: str):
        """

        """

        # check out 1
        if path.strip().lower() == "root":
            self.__recovery_init_interaction_state()
            self._dummy.on_enter_node()
            return True

        index_list = []
        path = path.split(".")

        self.__save_interaction_state()  # last valid state
        while path:
            p = path.pop(0)
            self._current_path.append(p)
            try:
                child, index = next(((item, i) for i, item in enumerate(self._dummy.children) if item.label == p))

                # update state
                index_list.append(index)
                self._hierarchy_level += 1

            except StopIteration:
                self.__recovery_last_interaction_state()
                return

            self._content_stack.append(self._dummy.content)
            child.on_enter_node(self._dummy)
            self._dummy.on_leave_node()
            self._dummy = child
            self._dummy.set_content_stack(self._content_stack)
        # throw events
        self.notify_observers(IGraphEvents.UPDATE_PROMPT, self._current_path)
        self.notify_observers(IGraphEvents.UPDATE_DUMMY, index_list)
        return True

    @property
    def root(self):
        return self._root

    @property
    def dummy(self):
        return self._dummy
