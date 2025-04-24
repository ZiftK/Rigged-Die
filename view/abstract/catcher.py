from abc import ABC, abstractmethod


class Catcher:

    @abstractmethod
    def catch(self, *args, **kwargs):
        """
        Catch a command input
        """
