from typing import Callable, Generic, TypeVar


T = TypeVar('T')


class Predicate(Generic[T]):
    __function = None

    def __init__(self, f: Callable[[T], bool]):
        self.__function = f

    def apply_to(self, o: T) -> bool:
        return self.__function(o)
