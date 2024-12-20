# c_sundials.pxd

# Dependencies
cimport numpy as np

# Define float and int types:
# config.pxi is created in setup.py. While building the python package, the 
# sundials_config.h header is parsed to determine what precision was used to
# compile the SUNDIALS that is being built against. The settings are saved in
# the pxi file and used here.
include "config.pxi"

IF SUNDIALS_FLOAT_TYPE == "single":
    ctypedef float sunrealtype
    ctypedef np.float32_t DTYPE_t
ELIF SUNDIALS_FLOAT_TYPE == "double":
    ctypedef double sunrealtype
    ctypedef np.float64_t DTYPE_t
ELIF SUNDIALS_FLOAT_TYPE == "extended":
    ctypedef long double sunrealtype
    ctypedef np.float128_t DTYPE_t

IF SUNDIALS_INT_TYPE == "int32":
    ctypedef int sunindextype
    ctypedef np.int32_t INT_TYPE_t
ELIF SUNDIALS_INT_TYPE == "int64":
    ctypedef long int sunindextype
    ctypedef np.int64_t INT_TYPE_t

# sundials_types.h
cdef extern from "sundials/sundials_types.h":
    ctypedef struct _SUNContext:
        pass
    ctypedef _SUNContext* SUNContext
    ctypedef int SUNComm
    ctypedef void (*SUNErrHandlerFn)(int line, const char* func, const char* file,
                                     const char* msg, int err_code, void* err_user_data,
                                     SUNContext ctx) except *

    int SUN_COMM_NULL

# sundials_context.h
cdef extern from "sundials/sundials_context.h":
    int SUNContext_Create(int comm, SUNContext* ctx)
    void SUNContext_Free(SUNContext* ctx)

    int SUNContext_ClearErrHandlers(SUNContext ctx)
    int SUNContext_PushErrHandler(SUNContext ctx, SUNErrHandlerFn err_fn,
                                  void* err_user_data)

# sundials_nvector.h
cdef extern from "sundials/sundials_nvector.h":
    ctypedef struct _N_Vector:
        pass
    ctypedef _N_Vector* N_Vector

    void N_VDestroy(N_Vector v)

# sundials_matrix.h
cdef extern from "sundials/sundials_matrix.h":
    ctypedef struct _SUNMatrix:
        pass 
    ctypedef _SUNMatrix* SUNMatrix

    ctypedef enum SUNMatrix_ID:
        SUNMATRIX_DENSE
        SUNMATRIX_BAND

    SUNMatrix_ID SUNMatGetID(SUNMatrix A)

    void SUNMatDestroy(SUNMatrix A)

# sundials_linearsolver.h
cdef extern from "sundials/sundials_linearsolver.h":
    ctypedef struct _SUNLinearSolver:
        pass 
    ctypedef _SUNLinearSolver* SUNLinearSolver

    int SUNLinSolFree(SUNLinearSolver LS)
