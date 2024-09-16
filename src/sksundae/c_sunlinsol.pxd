# c_sunlinsol.pxd

from .c_sundials cimport *  # Access to types

# sunlinsol_dense.h
cdef extern from "sunlinsol/sunlinsol_dense.h":
    SUNLinearSolver SUNLinSol_Dense(N_Vector y, SUNMatrix A, SUNContext ctx)

# sunlinsol_band.h
cdef extern from "sunlinsol/sunlinsol_band.h":
    SUNLinearSolver SUNLinSol_Band(N_Vector y, SUNMatrix A, SUNContext ctx)