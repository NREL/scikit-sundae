# c_sunmatrix.pxd

from .c_sundials cimport *  # Access to types

# sunmatrix_dense.h
cdef extern from "sunmatrix/sunmatrix_dense.h":
    SUNMatrix SUNDenseMatrix(sunindextype M, sunindextype N, SUNContext ctx)

    sunrealtype** SUNDenseMatrix_Cols(SUNMatrix A)

# sunmatrix_band.h
cdef extern from "sunmatrix/sunmatrix_band.h":
    SUNMatrix SUNBandMatrix(sunindextype M, sunindextype mu, sunindextype ml,
                            SUNContext ctx)

    sunindextype SUNBandMatrix_StoredUpperBandwidth(SUNMatrix A)
    sunindextype SUNBandMatrix_LowerBandwidth(SUNMatrix A)
    sunindextype SUNBandMatrix_UpperBandwidth(SUNMatrix A)
    sunrealtype** SUNBandMatrix_Cols(SUNMatrix A)