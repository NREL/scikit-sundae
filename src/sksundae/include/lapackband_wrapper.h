#ifndef LAPACKBAND_WRAPPER_H 
#define LAPACKBAND_WRAPPER_H  

#include <sundials/sundials_types.h>
#include <sundials/sundials_nvector.h>
#include <sundials/sundials_matrix.h>
#include <sundials/sundials_linearsolver.h>

// Include LAPACK band support, if enabled
#ifdef SUNDIALS_HAS_LAPACK
  #include <sunlinsol/sunlinsol_lapackband.h>
#else
  // If LAPACK band is NOT enabled, define a dummy function
  static inline SUNLinearSolver SUNLinSol_LapackBand(N_Vector y, SUNMatrix A, SUNContext ctx) {
      return NULL;
  }
#endif

#endif
