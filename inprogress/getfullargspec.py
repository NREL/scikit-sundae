import inspect
from collections import namedtuple
from inspect import (_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD, _VAR_POSITIONAL,
                     _KEYWORD_ONLY, _VAR_KEYWORD,)

from jax import jit as jjit
from numba import jit as njit


def py_func(a: int, b: int, *c, x: int = 1, y: int = 2, **z):
    return x + y


@njit
def nb_func(a: int, b: int, *c, x: int = 1, y: int = 2, **z):
    return x + y


@jjit
def jax_func(a: int, b: int, *c, x: int = 1, y: int = 2, **z):
    return x + y


class py_call:

    def __call__(self, a: int, b: int, *c, x: int = 1, y: int = 2, **z):
        return x + y

    @classmethod
    def call(cls, a: int, b: int, *c, x: int = 1, y: int = 2, **z):
        return x + y


FullArgSpec = namedtuple(
    'FullArgSpec',
    'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations',
)


def getfullargspec(func) -> FullArgSpec:

    try:
        sig = inspect.signature(func)
    except Exception as ex:
        raise TypeError('unsupported callable') from ex

    args = []
    varargs = None
    varkw = None
    posonlyargs = []
    kwonlyargs = []
    annotations = {}
    defaults = ()
    kwdefaults = {}

    if sig.return_annotation is not sig.empty:
        annotations['return'] = sig.return_annotation

    for param in sig.parameters.values():
        kind = param.kind
        name = param.name

        if kind is _POSITIONAL_ONLY:
            posonlyargs.append(name)
            if param.default is not param.empty:
                defaults += (param.default,)
        elif kind is _POSITIONAL_OR_KEYWORD:
            args.append(name)
            if param.default is not param.empty:
                defaults += (param.default,)
        elif kind is _VAR_POSITIONAL:
            varargs = name
        elif kind is _KEYWORD_ONLY:
            kwonlyargs.append(name)
            if param.default is not param.empty:
                kwdefaults[name] = param.default
        elif kind is _VAR_KEYWORD:
            varkw = name

        if param.annotation is not param.empty:
            annotations[name] = param.annotation

    if not kwdefaults:
        kwdefaults = None

    if not defaults:
        defaults = None

    return FullArgSpec(posonlyargs + args, varargs, varkw, defaults,
                       kwonlyargs, kwdefaults, annotations)


print('py:', getfullargspec(py_func))
print('nb:', getfullargspec(nb_func))
print('jax:', getfullargspec(jax_func))
print('call:', getfullargspec(py_call()))
print('cls:', getfullargspec(py_call.call))
