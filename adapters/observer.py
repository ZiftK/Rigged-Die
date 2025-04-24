import inspect
from abc import ABC, abstractmethod


def event(event_name: str):
    """
    Register the function as an event for Observer
    :param event_name: name of the event
    :return: function
    """

    def decorator(func):
        func._is_event = True
        func.event_name = event_name
        return func

    return decorator


def collect_events(observer):
    """
    Recovery all functions that use the command decorator
    """

    events = {}

    clss = observer.__class__

    # inspect class methods
    class_events = inspect.getmembers(clss, inspect.isfunction)

    # for each method
    for method in class_events:

        call = method[1]

        # if is decorated using @command
        if hasattr(call, "event_name"):
            events.setdefault(call.event_name, [])
            events.get(call.event_name).append(call)

    return events


class Observer(ABC):

    def __init__(self):
        self._events = collect_events(self)

    def update(self, event_name: str, *args, **kwargs):
        """
        Update using update data
        """
        calls = self._events.get(event_name, [])
        for call in calls:
            call(self, *args, **kwargs)


class Observable:

    def __init__(self, observers: list[Observer] | Observer | None = None):
        observers = [] if not observers else observers
        observers = [observers] if not (observers.__class__ is list) else observers
        self._observers: list = observers

    def add_observer(self, observer: Observer):
        """
        Add specified observer to observers list
        :param observer: observable
        """
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """
        Remove specified observer to observers list
        :param observer: observer
        """
        self._observers.remove(observer)

    def notify_observers(self, event_name: str, *args, **kwargs):
        """
        Notify each observer to observer list
        """
        for observer in self._observers:
            observer.update(event_name, *args, **kwargs)
