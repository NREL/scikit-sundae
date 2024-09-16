#include <stdio.h>
#include <stdlib.h>
#include <cvode/cvode.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sunlinsol/sunlinsol_dense.h>

#define NEQ 2  // Number of equations

int rhs(sunrealtype t, N_Vector yy, N_Vector yp, void *data) {
    
    sunrealtype *yy_p = N_VGetArrayPointer(yy);
    sunrealtype *yp_p = N_VGetArrayPointer(yp);

    yp_p[0] = yy_p[1];
    yp_p[1] = (1.0 - yy_p[0]*yy_p[0])*yy_p[1] - yy_p[0];

    return 0;
}

int main() {
    void *mem;
    N_Vector tt, yy;
    sunrealtype *tt_p, *yy_p;
    sunrealtype t0, tend, tout;
    SUNMatrix A;
    SUNLinearSolver LS;
    SUNContext ctx;
    sunrealtype lin_start = 0.0;
    sunrealtype lin_end = 20.0;
    int lin_num = 1000;
    sunrealtype step = (lin_end - lin_start) / (lin_num - 1.0);
    int flag;

    FILE *file = fopen("output.csv", "w");
    if (file == NULL) {
        printf("Error opening file.\n");
        return -1;
    }

    // Write the column headers
    fprintf(file, "t,y0,y1\n");

    SUNContext_Create(SUN_COMM_NULL, &ctx);

    tt = N_VNew_Serial(lin_num, ctx);
    tt_p = N_VGetArrayPointer(tt);
    for (int i = 0; i < lin_num; i++) {
        tt_p[i] = lin_start + i*step;
    }

    yy = N_VNew_Serial(NEQ, ctx);
    yy_p = N_VGetArrayPointer(yy);
    yy_p[0] = 2.0;
    yy_p[1] = 0.0;

    t0 = tt_p[0];
    tend = tt_p[lin_num-1];

    mem = CVodeCreate(CV_BDF, ctx);
    CVodeInit(mem, rhs, t0, yy);
    CVodeSStolerances(mem, 1.0e-6, 1.0e-8);

    A = SUNDenseMatrix(NEQ, NEQ, ctx);
    LS = SUNLinSol_Dense(yy, A, ctx);
    CVodeSetLinearSolver(mem, LS, A);

    CVodeSetMaxNonlinIters(mem, 3);
    CVodeSetMaxConvFails(mem, 10);

    CVodeSetInitStep(mem, 0.0);
    CVodeSetMinStep(mem, 0.0);
    CVodeSetMaxStep(mem, 0.0);
    CVodeSetMaxOrd(mem, 5);
    CVodeSetMaxNumSteps(mem, 500);

    flag = CVodeSetStopTime(mem, tend);
    if (flag != 0) {
        printf("Error: CVodeSetStopTime failed\n");
        return -1;
    }

    fprintf(file, "%.17g,%.17g,%.17g\n", t0, yy_p[0], yy_p[1]);

    // for (int i = 1; i < lin_num; i++) {
    //     flag = CVode(mem, tt_p[i], yy, &tout, CV_NORMAL);
    //     if (flag < 0) {
    //         printf("Error: CVODE failed\n");
    //         return -1;
    //     } 
        
    //     fprintf(file, "%.17g,%.17g,%.17g\n", tout, yy_p[0], yy_p[1]);
    //     printf("t=%g, y=%g, %g\n", tout, yy_p[0], yy_p[1]);

    //     if (flag == CV_TSTOP_RETURN) {
    //         break;
    //     }  
    // }   

    while (1) {
        flag = CVode(mem, tend, yy, &tout, CV_ONE_STEP);
        if (flag < 0) {
            printf("Error: CVODE failed\n");
            return -1;
        } 
        
        fprintf(file, "%.17g,%.17g,%.17g\n", tout, yy_p[0], yy_p[1]);
        printf("t=%g, y=%g, %g\n", tout, yy_p[0], yy_p[1]);

        if (flag == CV_TSTOP_RETURN) {
            break;
        }  
    } 

    N_VDestroy(yy);
    SUNMatDestroy(A);
    SUNLinSolFree(LS);
    CVodeFree(&mem);
    SUNContext_Free(&ctx);

    fclose(file);

    return 0;
}
