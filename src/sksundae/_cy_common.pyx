# _cy_common.pyx

# Dependencies
cimport numpy as np

# Extern cdef headers
from .c_sundials cimport *  # Access to C types
from .c_nvector cimport *  # Access to N_Vector functions
from .c_sunmatrix cimport *  # Access to SUNMatrix functions

# Define float and int types:
# config.pxi is created in setup.py. While building the python package, the 
# sundials_config.h header is parsed to determine what precision was used to
# compile the SUNDIALS that is being built against. The settings are saved in
# the pxi file and used here.
include "config.pxi"

sundials_version = SUNDIALS_VERSION

if SUNDIALS_FLOAT_TYPE == "single":
    from numpy import float32 as DTYPE
elif SUNDIALS_FLOAT_TYPE == "double":
    from numpy import float64 as DTYPE
elif SUNDIALS_FLOAT_TYPE == "extended":
    from numpy import longdouble as DTYPE

if SUNDIALS_INT_TYPE == "int32":
    from numpy import int32 as INT_TYPE
elif SUNDIALS_INT_TYPE == "int64":
    from numpy import int64 as INT_TYPE


cdef svec2np(N_Vector nvec, np.ndarray[DTYPE_t, ndim=1] np_array):
    """Fill a numpy array with values from an N_Vector."""
    cdef sunrealtype* nvec_ptr

    nv_ptr = N_VGetArrayPointer(nvec)
    ptr2np(nv_ptr, np_array)


cdef np2svec(np.ndarray[DTYPE_t, ndim=1] np_array, N_Vector nvec):
    """Fill an N_Vector with values from a numpy array."""
    cdef sunrealtype* nv_ptr

    nv_ptr = N_VGetArrayPointer(nvec)
    np2ptr(np_array, nv_ptr)


cdef ptr2np(sunrealtype* nv_ptr, np.ndarray[DTYPE_t, ndim=1] np_array):
    """Fill a numpy array with values from an N_Vector pointer."""
    cdef sunindextype i
    cdef np.npy_intp size = np_array.size

    for i in range(size):
        np_array[i] = nv_ptr[i]


cdef np2ptr(np.ndarray[DTYPE_t, ndim=1] np_array, sunrealtype* nv_ptr):
    """Fill an N_Vector pointer with values from a numpy array."""
    cdef sunindextype i
    cdef np.npy_intp size = np_array.size

    for i in range(size):
        nv_ptr[i] = np_array[i]


cdef np2smat_dense(np.ndarray[DTYPE_t, ndim=2] np_A, SUNMatrix smat):
    """Fill a SUNDenseMatrix with values from a 2D numpy array."""
    cdef sunindextype i
    cdef sunindextype j 
    cdef np.npy_intp M = np_A.shape[0]
    cdef np.npy_intp N = np_A.shape[1]
    cdef sunrealtype** sm_cols = SUNDenseMatrix_Cols(smat)

    for j in range(N):
        for i in range(M):
            sm_cols[j][i] = np_A[i,j]


cdef np2smat_band(np.ndarray[DTYPE_t, ndim=2] np_A, SUNMatrix smat):
    """Fill a SUNBandMatrix with values from a 2D numpy array."""
    cdef sunindextype i
    cdef sunindextype j 
    cdef np.npy_intp N = np_A.shape[1]
    cdef sunrealtype** sm_cols = SUNBandMatrix_Cols(smat)
    cdef sunindextype lband = SUNBandMatrix_LowerBandwidth(smat)
    cdef sunindextype uband = SUNBandMatrix_UpperBandwidth(smat)
    cdef sunindextype smu = SUNBandMatrix_StoredUpperBandwidth(smat)

    # Indexing is more complex in a SUNBandMatrix, see documentation:
    # https://sundials.readthedocs.io/en/latest/sunmatrix/SUNMatrix_links.html
    for j in range(N):
        i_min = max(0, j - uband)
        i_max = min(N, j + lband + 1)
        for i in range(i_min, i_max):
            sm_cols[j][i-j+smu] = np_A[i,j]


cdef np2smat(np.ndarray[DTYPE_t, ndim=2] np_A, SUNMatrix smat):
    """Fill a SUNMatrix with values from np_A using the correct cdef."""
    cdef SUNMatrix_ID matrix_id = SUNMatGetID(smat)

    if matrix_id == SUNMATRIX_DENSE:
        np2smat_dense(np_A, smat)
    elif matrix_id == SUNMATRIX_BAND:
        np2smat_band(np_A, smat)
    else:
        raise TypeError("'smat' must be a 'dense' or 'band' SUNMatrix.")
