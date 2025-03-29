# precond.py

from typing import Callable


class CVODEPrecond:

    __slots__ = ('setupfn', 'solvefn', 'side')

    def __init__(self, setupfn: Callable | None, solvefn: Callable,
                 side: str = 'left') -> None:

        if setupfn is None:
            pass
        elif not isinstance(setupfn, Callable):
            raise TypeError("'setupfn' must be type Callable.")

        if not isinstance(solvefn, Callable):
            raise TypeError("'solvefn' must be type Callable.")
        elif side not in {'left', 'right', 'both'}:
            raise ValueError("'side' must be in {'left', 'right', 'both'}.")

        self.setupfn = setupfn
        self.solvefn = solvefn
        self.side = side


class IDAPrecond:

    __slots__ = ('setupfn', 'solvefn', 'side')

    def __init__(self, setupfn: Callable | None, solvefn: Callable) -> None:

        if setupfn is None:
            pass
        elif not isinstance(setupfn, Callable):
            raise TypeError("'setupfn' must be type Callable.")

        if not isinstance(solvefn, Callable):
            raise TypeError("'solvefn' must be type Callable.")

        self.setupfn = setupfn
        self.solvefn = solvefn
        self.side = 'left'  # IDA only supports left precond
