#include <stdio.h>
#include <stdlib.h>
#include <ida/ida.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sunlinsol/sunlinsol_dense.h>

#define NEQ 3  // Number of equations

int res(sunrealtype t, N_Vector yy, N_Vector yp, N_Vector rr, void *data) {
    
    sunrealtype *yy_p = N_VGetArrayPointer(yy);
    sunrealtype *yp_p = N_VGetArrayPointer(yp);
    sunrealtype *rr_p = N_VGetArrayPointer(rr);

    rr_p[0] = yp_p[0] + 0.04*yy_p[0] - 1.0e4*yy_p[1]*yy_p[2];
    rr_p[1] = yp_p[1] - 0.04*yy_p[0] + 1.0e4*yy_p[1]*yy_p[2] + 3.0e7*yy_p[1]*yy_p[1];
    rr_p[2] = yy_p[0] + yy_p[1] + yy_p[2] - 1.0;

    return 0;
}

int main() {
    void *mem;
    N_Vector tt, yy, yp;
    sunrealtype *tt_p, *yy_p, *yp_p;
    sunrealtype t0, tend, tout;
    SUNMatrix A;
    SUNLinearSolver LS;
    SUNContext ctx;
    sunrealtype log_start = -6.0;
    sunrealtype log_end = 6.0;
    int log_num = 50;
    sunrealtype step = (log_end - log_start) / (log_num - 1.0);
    int flag;

    FILE *file = fopen("output.csv", "w");
    if (file == NULL) {
        printf("Error opening file.\n");
        return -1;
    }

    // Write the column headers
    fprintf(file, "t,y0,y1,y2\n");

    SUNContext_Create(SUN_COMM_NULL, &ctx);

    tt = N_VNew_Serial(log_num, ctx);
    tt_p = N_VGetArrayPointer(tt);
    for (int i = 0; i < log_num; i++) {
        tt_p[i] = 4.0*pow(10, log_start + i*step);
    }

    yy = N_VNew_Serial(NEQ, ctx);
    yy_p = N_VGetArrayPointer(yy);
    yy_p[0] = 1.0;
    yy_p[1] = 0.0;
    yy_p[2] = 0.0;

    yp = N_VNew_Serial(NEQ, ctx);
    yp_p = N_VGetArrayPointer(yp);
    yp_p[0] = -0.04;
    yp_p[1] = 0.04;
    yp_p[2] = 0.0;

    t0 = tt_p[0];
    tend = tt_p[log_num-1];

    mem = IDACreate(ctx);
    IDAInit(mem, res, t0, yy, yp);
    IDASStolerances(mem, 1.0e-4, 1.0e-8);

    A = SUNDenseMatrix(NEQ, NEQ, ctx);
    LS = SUNLinSol_Dense(yy, A, ctx);
    IDASetLinearSolver(mem, LS, A);

    IDASetMaxNonlinIters(mem, 4);
    IDASetMaxConvFails(mem, 10);

    N_Vector algidx = N_VNew_Serial(NEQ, ctx);
    sunrealtype *alg_p = N_VGetArrayPointer(algidx);

    alg_p[0] = 1.0;
    alg_p[1] = 1.0;
    alg_p[2] = 0.0;

    IDASetId(mem, algidx);

    IDASetInitStep(mem, 0.0);
    IDASetMinStep(mem, 0.0);
    IDASetMaxStep(mem, 0.0);
    IDASetMaxOrd(mem, 5);
    IDASetMaxNumSteps(mem, 500);

    flag = IDASetStopTime(mem, tend);
    if (flag != 0) {
        printf("Error: IDASetStopTime failed\n");
        return -1;
    }

    fprintf(file, "%.17g,%.17g,%.17g,%.17g\n", t0, yy_p[0], yy_p[1], yy_p[2]);

    for (int i = 1; i < log_num; i++) {
        flag = IDASolve(mem, tt_p[i], &tout, yy, yp, IDA_NORMAL);
        if (flag < 0) {
            printf("Error: IDASolve failed\n");
            return -1;
        } 
        
        fprintf(file, "%.17g,%.17g,%.17g,%.17g\n", tout, yy_p[0], yy_p[1], yy_p[2]);
        printf("t=%g, y=%g, %g, %g\n", tout, yy_p[0], yy_p[1], yy_p[2]);

        if (flag == IDA_TSTOP_RETURN) {
            break;
        }  
    }   

    N_VDestroy(yy);
    N_VDestroy(yp);
    SUNMatDestroy(A);
    SUNLinSolFree(LS);
    IDAFree(&mem);
    SUNContext_Free(&ctx);

    fclose(file);

    return 0;
}
