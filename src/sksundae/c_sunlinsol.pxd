# c_sunlinsol.pxd

from .c_sundials cimport *  # Access to types

# sunlinsol_dense.h
cdef extern from "sunlinsol/sunlinsol_dense.h":
    SUNLinearSolver SUNLinSol_Dense(N_Vector y, SUNMatrix A, SUNContext ctx)

# sunlinsol_band.h
cdef extern from "sunlinsol/sunlinsol_band.h":
    SUNLinearSolver SUNLinSol_Band(N_Vector y, SUNMatrix A, SUNContext ctx)

# sunlinsol_superlumt.h - real or dummy, depending on availability
cdef extern from "./include/superlumt_wrapper.h":
    SUNLinearSolver SUNLinSol_SuperLUMT(N_Vector y, SUNMatrix A, int nthreads,
                                        SUNContext ctx)
