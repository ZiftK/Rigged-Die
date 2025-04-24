import random
from enum import Enum


class IntervalTypes(Enum):
    REAL = "minterval"
    INTEGER = "iinterval"
    GAUSSIAN = "ginterval"


class CInterval:

    @classmethod
    def build_from_dictionary(cls, dictionary: dict):

        checks = ("initial", "final", "type")

        for check in checks:
            if not (check in dictionary.keys()):
                return None

        initial = dictionary.get("initial")
        final = dictionary.get("final")
        interval_type = dictionary.get("type")

        return CInterval(initial, final, interval_type)

    def __init__(self,
                 initial: int | float,
                 final: int | float,
                 itype: IntervalTypes = IntervalTypes.REAL):

        self._initial: int | float = initial
        self._final: int | float = final
        self._type = itype

    def __str__(self):
        string = f"({self._initial}:{self._final})"

        if self._type == IntervalTypes.REAL:
            string += " as R "
        elif self._type == IntervalTypes.INTEGER:
            string += " as Z "
        elif self._type == IntervalTypes.GAUSSIAN:
            string += " as Gaussian"
        return string

    def generate(self):
        if self._type == IntervalTypes.REAL:
            return random.uniform(self._initial, self._final)
        elif self._type == IntervalTypes.INTEGER:
            return random.randrange(self._initial, self._final)
        elif self._type == IntervalTypes.GAUSSIAN:
            return random.gauss(self._initial, self._final)

    def get_in_dictionary(self):
        return {
            "compact": str(self),
            "initial": self.initial,
            "final": self._final,
            "type": self._type
        }

    @property
    def initial(self):
        return self._initial

    @property
    def final(self):
        return self._final

    @property
    def type(self):
        return self._type


class CRange:

    @classmethod
    def build_from_dictionary(cls, dictionary: dict):

        checks = ("initial", "final", "step")

        for check in checks:
            if not (check in dictionary.keys()):
                return None

        initial = dictionary.get("initial")
        final = dictionary.get("final")
        step = dictionary.get("step")

        if isinstance(step, dict):
            step = CInterval.build_from_dictionary(step)

        return CRange(initial, final, step)

    def __init__(self,
                 initial: int | float,
                 final: int | float,
                 step: CInterval | int | float = 1):

        self._initial: int | float = initial
        self._final: int | float = final
        self._step: CInterval | int | float = step

        self._counter = initial

    def __str__(self):
        string = f"[{self._initial}:{self._final}:{str(self._step)}]"
        return string

    def __iter__(self):

        stp = self._step

        while self._counter < self._final:
            yield self._counter

            if isinstance(self._step, CInterval):
                stp = self._step.generate()
            self._counter += stp

    def get_tuple(self):
        return tuple(x for x in self)

    def get_in_dictionary(self):

        step = self._step
        if isinstance(self._step, CInterval):
            step = self._step.get_in_dictionary()
        dct = {
            "compact": str(self),
            "initial": self._initial,
            "final": self._final,
            "step": step
        }

        return dct

    @property
    def initial(self):
        return self._initial

    @property
    def final(self):
        return self._final

    @property
    def step(self):
        return self._step
