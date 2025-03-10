#ifndef SUPERLUMT_WRAPPER_H 
#define SUPERLUMT_WRAPPER_H  

#include <sundials/sundials_types.h>
#include <sundials/sundials_nvector.h>
#include <sundials/sundials_matrix.h>
#include <sundials/sundials_linearsolver.h>

// Include SuperLU_MT support, if enabled
#ifdef SUNDIALS_HAS_SUPERLUMT
  #include <sunlinsol/sunlinsol_superlumt.h>
#else
  // If SuperLU_MT is NOT enabled, define a dummy function
  static inline SUNLinearSolver SUNLinSol_SuperLUMT(N_Vector y, SUNMatrix A, int nthreads, SUNContext ctx) {
      return NULL;
  }
#endif

#endif
