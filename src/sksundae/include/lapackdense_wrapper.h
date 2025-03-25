#ifndef LAPACKDENSE_WRAPPER_H 
#define LAPACKDENSE_WRAPPER_H  

#include <sundials/sundials_types.h>
#include <sundials/sundials_nvector.h>
#include <sundials/sundials_matrix.h>
#include <sundials/sundials_linearsolver.h>

// Include LAPACK dense support, if enabled
#ifdef SUNDIALS_HAS_LAPACK
  #include <sunlinsol/sunlinsol_lapackdense.h>
#else
  // If LAPACK dense is NOT enabled, define a dummy function
  static inline SUNLinearSolver SUNLinSol_LapackDense(N_Vector y, SUNMatrix A, SUNContext ctx) {
      return NULL;
  }
#endif

#endif
