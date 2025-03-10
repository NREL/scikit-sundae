import time

import numpy as np
import sksundae as sun

from scipy import sparse as sp

NEQ = 1000
sparsity = np.zeros((3*NEQ, 3*NEQ))
for i in range(NEQ):
    sparsity[3*i:3*(i + 1), 3*i:3*(i+1)] = np.ones((3, 3))


def ida_sparsity(N):
    diagonals = [
        np.ones(N),
        np.ones(2*N),
        np.ones(3*N),
        np.ones(2*N),
        np.ones(N),
    ]

    offsets = [-2*N, -1*N, 0, 1*N, 2*N]

    A = sp.diags(diagonals, offsets, shape=(3*NEQ, 3*NEQ))

    return A


sparsity = ida_sparsity(NEQ)


def resfn(t, y, yp, res):
    y0, yp0 = y[:NEQ], yp[:NEQ]
    y1, yp1 = y[NEQ:2*NEQ], yp[NEQ:2*NEQ]
    y2, _ = y[2*NEQ:3*NEQ], yp[2*NEQ:3*NEQ]

    res[:NEQ] = yp0 + 0.04*y0 - 1e4*y1*y2
    res[NEQ:2*NEQ] = yp1 - 0.04*y0 + 1e4*y1*y2 + 3e7*y1**2
    res[2*NEQ:3*NEQ] = y0 + y1 + y2 - 1


tspan = np.logspace(-6, 6, 50)

y0 = np.zeros(3*NEQ)
y0[:NEQ] = 1

yp0 = np.zeros(3*NEQ)
yp0[:NEQ] = -0.04
yp0[NEQ:2*NEQ] = 0.04

alg = [2 + 3*i for i in range(NEQ)]

# options = {
#     'linsolver': 'band',
#     'lband': 2*NEQ,
#     'uband': 2*NEQ,
# }

options = {
    'linsolver': 'sparse',
    'sparsity': sparsity,
    'nthreads': 1,
}

solver = sun.ida.IDA(resfn, atol=1e-8, algebraic_idx=alg, **options)

start = time.time()
soln = solver.solve(tspan, y0, yp0)
print(f"\n\nsolvetime: {time.time() - start:.5f} seconds\n\n")

print(soln)

soln.y[:, NEQ:2*NEQ] *= 1e4  # scale the y1 values for plotting

###

NEQ = 1000


def cvode_sparsity(N):
    diagonals = [
        np.ones(N),
        np.ones(2*N),
        np.ones(N),
    ]

    offsets = [-1*N, 0, 1*N]

    A = sp.diags(diagonals, offsets, shape=(2*NEQ, 2*NEQ))

    return A


sparsity = cvode_sparsity(NEQ)


def rhsfn(t, y, yp):
    y0 = y[:NEQ]
    y1 = y[NEQ:]

    yp[:NEQ] = y1
    yp[NEQ:] = 1000*(1 - y0**2)*y1 - y0


tspan = np.array([0, 3000])

y0 = np.zeros(2*NEQ)
y0[:NEQ] = 2

# options = {
#     'linsolver': 'band',
#     'lband': NEQ,
#     'uband': NEQ,
#     'sparsity': sparsity,
# }

options = {
    'linsolver': 'sparse',
    'sparsity': sparsity,
    'nthreads': 1,
}

solver = sun.cvode.CVODE(rhsfn, **options)

start = time.time()
soln = solver.solve(tspan, y0)
print(f"\n\nsolvetime: {time.time() - start:.5f} seconds\n\n")

print(soln)

# plt.figure()
# plt.plot(soln.t, soln.y[:,:NEQ])
# plt.show()
