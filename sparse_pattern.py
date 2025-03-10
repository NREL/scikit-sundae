import timeit
import inspect

from warnings import warn
from typing import Callable, Any

import numpy as np
import matplotlib.pyplot as plt

from scipy import linalg
from numpy.typing import ArrayLike


def bandwidth(
    resfn: Callable, t0: float, y0: ArrayLike, yp0: ArrayLike,
    userdata: Any = None, return_pattern: bool = False,
) -> tuple[int | np.ndarray]:

    # Wrap resfn for cases w/ and w/o userdata
    signature = inspect.signature(resfn)

    if len(signature.parameters) == 4:
        def wrapper(t, y, yp, res): return resfn(t, y, yp, res)
    elif len(signature.parameters) == 5:
        if userdata is None:
            warn("'resfn' signature has 5 inputs, but 'userdata=None'.")

        def wrapper(t, y, yp, res): return resfn(t, y, yp, res, userdata)
    else:
        raise ValueError("'resfn' signature must have either 4 or 5 inputs.")

    # Get recommended minimum perturbation
    uround = np.finfo(y0.dtype).eps
    srur = np.sqrt(uround)

    # Perturbed variables
    y = np.maximum(srur, y0)
    yp = np.maximum(srur, yp0)

    # Initial residuals
    res_0 = np.zeros_like(y)

    wrapper(t0, y, yp, res_0)

    norm = max(srur, np.abs(res_0).max())
    res_0 = res_0 / norm

    # Jacobian pattern
    def j_pattern(j):
        res = np.zeros_like(y)

        rng = np.random.default_rng(42)
        rand = rng.random(2)

        y_store, yp_store = y[j], yp[j]

        y[j] += max(srur, srur*y[j]) * rand[0]
        yp[j] += max(srur, srur*yp[j]) * rand[1]

        wrapper(t0, y, yp, res)

        res = res / norm

        y[j], yp[j] = y_store, yp_store

        return (res_0 != res).astype(int)

    j_cols = [j_pattern(j) for j in range(y.size)]
    j_pat = np.column_stack(j_cols)

    # Find lband and uband
    output = linalg.bandwidth(j_pat)

    if return_pattern:
        output += (j_pat,)

    return output


NEQ = 20


def resfn(t, y, yp, res):
    y0, yp0 = y[:NEQ], yp[:NEQ]
    y1, yp1 = y[NEQ:2*NEQ], yp[NEQ:2*NEQ]
    y2, _ = y[2*NEQ:3*NEQ], yp[2*NEQ:3*NEQ]

    res[:NEQ] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[NEQ:2*NEQ] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2*NEQ:3*NEQ] = y0 + y1 + y2 - 1


t0 = 0.

y0 = np.zeros(3*NEQ)
y0[:NEQ] = 1

yp0 = np.zeros(3*NEQ)
yp0[:NEQ] = -0.04
yp0[NEQ:2*NEQ] = 0.04


def f():
    return bandwidth(resfn, t0, y0, yp0, return_pattern=True)


lband, uband, pattern = f()
print(lband, uband)

plt.figure()
plt.spy(pattern)
plt.show()

number = 5
total_time = timeit.timeit(f, number=number)

print(f"{total_time=:.5f} s")
print(f"normalized_time={total_time/number:.5f} s")
