# _cy_ida.pyx

# Enable embedded signatures for the entire module
# cython: embedsignature=True, embeddedsignature.format='python'

# Standard library
from warnings import warn
from types import MethodType
from inspect import getfullargspec
from typing import Callable, Iterable

# Dependencies
import numpy as np
cimport numpy as np
from cpython.exc cimport PyErr_CheckSignals, PyErr_Occurred

# Extern cdef headers
from .c_ida cimport *
from .c_sundials cimport *
from .c_nvector cimport *
from .c_sunmatrix cimport *
from .c_sunlinsol cimport *

# Internal cdef headers
from ._cy_common cimport *
from ._cy_common import DTYPE, INT_TYPE  # Python precisions

# Local python dependencies
from .utils import RichResult


# Messages shorted from documentation online:
# https://sundials.readthedocs.io/en/latest/ida/Constants_link.html
IDAMESSAGES = {
    0: "Successful function return.",
    1: "Reached specified tstop.",
    2: "Detected one or more events.",
    99: "Succeeded but something unusual happened.",
    -1: "Could not reach endpoint after 'max_num_steps'.",
    -2: "Could not satisfy demanded accuracy for an internal step.",
    -3: "Error tests failed too many times, or reached min step size.",
    -4: "Convergence tests failed too many times, or reached min step size.",
    -5: "Linear solver initialization routine failed.",
    -6: "Linear solver setup function unrecoverably failed.",
    -7: "Linear solver solve function unrecoverably failed.",
    -8: "Residual function had a non-recoverable error.",
    -9: "'resfn' returned recoverable errors, but the solver cannot recover",
    -10: "Event-detection routine unrecoverably failed.",
    -11: "Inequality constraints could not be met.",
    -12: "Residual function failed on the first call.",
    -13: "The line search failed.",
    -14: "Couldn't recover from a 'resfn' or 'linsolver' error.",
    -15: "Nonlinear solver initialization routine failed.",
    -16: "Nonlinear solver setup function failed.",
    -17: "Nonlinear solver solve function failed.",
    -20: "The integrator's 'mem' argument is NULL.",
    -21: "A memory allocation request failed.",
    -22: "One of the function inputs is invalid.",
    -23: "Memory was not allocated prior to an IDAInit call.",
    -24: "Zero value of some error weight component.",
    -25: "Bad k value. k must be in range 0, 1, ..., order.",
    -26: "Bad t value. t must be within the last step interval.",
    -27: "The Dky vector is NULL.",
    -28: "IDA experienced a vector operation error.",
    -29: "A SUNContext error occurred while initializing the solver.",
    -99: "An unrecognized error occurred within the solver.",
}

LSMESSAGES = {
    0: "Successful function return.",
    -1: "The integrator's 'mem' argument is NULL.",
    -2: "The linear solver has not been initialized.",
    -3: "The linear solver is not compatible with the N_Vector module.",
    -4: "A memory allocation request failed.",
    -5: "The preconditioner module has not been initialized.",
    -6: "The Jacobian function unrecoverably failed.",
    -7: "The Jacobian function had a recoverable error.",
    -8: "An error occurred with the current SUNMatrix module.",
    -9: "An error occurred with the current SUNLinearSolver module.",
}


cdef int _resfn_wrapper(sunrealtype t, N_Vector yy, N_Vector yp, N_Vector rr,
                        void* data) except? -1:
    """Wraps 'resfn' by converting between N_Vector and ndarray types."""

    aux = <AuxData> data

    svec2np(yy, aux.np_yy)
    svec2np(yp, aux.np_yp)

    if aux.with_userdata:
        _ = aux.resfn(t, aux.np_yy, aux.np_yp, aux.np_rr, aux.userdata)
    else:
        _ = aux.resfn(t, aux.np_yy, aux.np_yp, aux.np_rr)

    np2svec(aux.np_rr, rr)
    
    return 0


cdef int _eventsfn_wrapper(sunrealtype t, N_Vector yy, N_Vector yp,
                           sunrealtype* ee, void* data) except? -1:
    """Wraps 'eventsfn' by converting between N_Vector and ndarray types."""

    aux = <AuxData> data

    svec2np(yy, aux.np_yy)
    svec2np(yp, aux.np_yp)

    if aux.with_userdata:
        _ = aux.eventsfn(t, aux.np_yy, aux.np_yp, aux.np_ee, aux.userdata)
    else:
        _ = aux.eventsfn(t, aux.np_yy, aux.np_yp, aux.np_ee)

    np2ptr(aux.np_ee, ee)
    
    return 0


cdef int _jacfn_wrapper(sunrealtype t, sunrealtype cj, N_Vector yy, N_Vector yp,
                        N_Vector rr, SUNMatrix JJ, void* data, N_Vector tmp1,
                        N_Vector tmp2, N_Vector tmp3) except? -1:
    """Wraps 'jacfn' by converting between N_Vector and ndarray types."""
    
    aux = <AuxData> data

    svec2np(yy, aux.np_yy)
    svec2np(yp, aux.np_yp)
    svec2np(rr, aux.np_rr)

    if aux.with_userdata:
        _ = aux.jacfn(t, aux.np_yy, aux.np_yp, aux.np_rr, cj, aux.np_JJ,
                      aux.userdata)
    else:
        _ = aux.jacfn(t, aux.np_yy, aux.np_yp, aux.np_rr, cj, aux.np_JJ)

    np2smat(aux.np_JJ, JJ)

    return 0


cdef void _err_handler(int line, const char* func, const char* file,
                       const char* msg, int err_code, void* err_user_data,
                       SUNContext ctx) except *:
    """Custom error handler for shorter messages (no line or file)."""
    
    decoded_func = func.decode("utf-8")
    decoded_msg = msg.decode("utf-8").replace(", ,", ",").strip()

    if not PyErr_Occurred():
        print(f"\n[{decoded_func}, Error: {err_code}] {decoded_msg}\n")


cdef class AuxData:
    """
    Auxiliary data.
    
    Used to pre-allocate and store numpy arrays in memory, and to carry data
    to function wrappers.

    """
    cdef np.ndarray np_yy       # state variables
    cdef np.ndarray np_yp       # yy time derivatives
    cdef np.ndarray np_rr       # residuals array
    cdef np.ndarray np_ee       # events array
    cdef np.ndarray np_JJ       # Jacobian matrix
    cdef bint with_userdata

    cdef object resfn
    cdef object userdata
    cdef object eventsfn
    cdef object jacfn

    def __cinit__(self, np.npy_intp NEQ, object options):
        self.np_yy = np.empty(NEQ, DTYPE)
        self.np_yp = np.empty(NEQ, DTYPE)
        self.np_rr = np.empty(NEQ, DTYPE)
        
        self.resfn = options["resfn"]
        self.userdata = options["userdata"]
        self.with_userdata = 1 if self.userdata is not None else 0

        self.eventsfn = options["eventsfn"]
        self.np_ee = np.empty(options["num_events"], DTYPE)

        self.jacfn = options["jacfn"]
        if self.jacfn is not None:
            self.np_JJ = np.zeros((NEQ, NEQ), DTYPE)
        else:
            self.np_JJ = np.empty(0, DTYPE)


class IDAResult(RichResult):
    _order_keys = ["message", "success", "status", "t", "y", "yp", "i_events",
                   "t_events", "y_events", "yp_events", "nfev", "njev",]


cdef class IDA:
    cdef void* mem
    cdef SUNContext ctx
    cdef N_Vector atol
    cdef N_Vector algidx
    cdef N_Vector constraints
    cdef N_Vector yy
    cdef N_Vector yp
    cdef SUNMatrix A 
    cdef SUNLinearSolver LS
    cdef np.npy_intp NEQ
    cdef AuxData aux

    cdef object _size
    cdef object _malloc
    cdef object _options
    cdef object _initialized

    def __cinit__(self, object resfn, **options):
        self._free_memory()
        
        self._options = {
            "resfn": resfn,
            "userdata": None,
            "calc_initcond": None,
            "calc_init_dt": 0.01,
            "algebraic_idx": None,
            "first_step": 0.,
            "min_step": 0., 
            "max_step": 0.,
            "rtol": 1e-5, 
            "atol": 1e-6,
            "linsolver": "dense",
            "lband": None,
            "uband": None,
            "max_order": 5,
            "max_num_steps": 500,
            "max_nonlin_iters": 4,
            "max_conv_fails": 10,
            "constraints_idx": None,
            "constraints_type": None,
            "eventsfn": None,
            "num_events": 0,
            "jacfn": None,
        }

        invalid_keys = set(options.keys()) - set(self._options.keys())
        if invalid_keys:
            raise ValueError(f"Invalid keyword arguments: {invalid_keys}.")
        
        self._options.update(options)

        _check_options(self._options)

        self._initialized = False

    cdef _create_linsolver(self):
        
        if self._options["linsolver"] == "dense":
            self.A = SUNDenseMatrix(self.NEQ, self.NEQ, self.ctx)
            self.LS = SUNLinSol_Dense(self.yy, self.A, self.ctx)

        elif self._options["linsolver"] == "band":
            uband = self._options["uband"]
            lband = self._options["lband"]

            self.A = SUNBandMatrix(self.NEQ, uband, lband, self.ctx)
            self.LS = SUNLinSol_Band(self.yy, self.A, self.ctx)

        if self.A is NULL:
            raise MemoryError("SUNMatrix constructor returned NULL.")
        elif self.LS is NULL:
            raise MemoryError("SUNLinSol constructor returned NULL.")

    cdef _set_tolerances(self):
        rtol = self._options["rtol"]
        atol = self._options["atol"]

        if isinstance(atol, Iterable):
            rtol = <sunrealtype> rtol
            atol = np.asarray(atol, dtype=DTYPE)

            if len(atol) != self.NEQ:
                raise ValueError(f"'atol' length ({atol.size}) differs from"
                                 f" problem size ({self.NEQ}).")

            self.atol = N_VNew_Serial(atol.size, self.ctx)
            np2svec(atol, self.atol)

            flag = IDASVtolerances(self.mem, rtol, self.atol)

        else:
            rtol = <sunrealtype> rtol
            atol = <sunrealtype> atol 

            flag = IDASStolerances(self.mem, rtol, atol)

        if flag < 0:
            raise RuntimeError("IDAtolerances - " + IDAMESSAGES[flag])

    cdef _free_memory(self):
        if self.mem is not NULL:
            IDAFree(&self.mem)
            self.mem = NULL

        if self.ctx is not NULL:
            SUNContext_Free(&self.ctx)
            self.ctx = NULL

        if self.atol is not NULL:
            N_VDestroy(self.atol)
            self.atol = NULL

        if self.algidx is not NULL:
            N_VDestroy(self.algidx)
            self.algidx = NULL

        if self.constraints is not NULL:
            N_VDestroy(self.constraints)
            self.constraints = NULL

        if self.yy is not NULL:
            N_VDestroy(self.yy)
            self.yy = NULL

        if self.yp is not NULL:
            N_VDestroy(self.yp)
            self.yp = NULL

        if self.A is not NULL:
            SUNMatDestroy(self.A)
            self.A = NULL

        if self.LS is not NULL:
            SUNLinSolFree(self.LS)
            self.LS = NULL

        self._size = None
        self._malloc = False

    cdef int _setup(self, sunrealtype t0, np.ndarray[DTYPE_t, ndim=1] y0,
                    np.ndarray[DTYPE_t, ndim=1] yp0):

        # Enumerated steps below correspond to the SUNDIALS IDA documentation,
        # available at https://sundials.readthedocs.io/en/latest/ida/Usage.

        cdef int flag
        cdef np.ndarray np_eventsdir

        # 1) Initialize parallel environment (skip, only use serial here)

        # 2) Create sundials context object
        flag = SUNContext_Create(SUN_COMM_NULL, &self.ctx)
        if flag < 0:
            raise RuntimeError(f"SUNContext_Create failed with {flag=}.")

        # 3) Create vectors of initial values
        if len(y0) != len(yp0):
            raise ValueError("'y0' and 'yp0' must be the same size.")
        
        self.NEQ = y0.size
        self.aux = AuxData(self.NEQ, self._options)

        self.yy = N_VNew_Serial(self.NEQ, self.ctx)
        if self.yy is NULL:
            raise MemoryError("N_VNew_Serial returned a NULL pointer for yy.")

        self.yp = N_VNew_Serial(self.NEQ, self.ctx)
        if self.yp is NULL:
            raise MemoryError("N_VNew_Serial returned a NULL pointer for yp.")

        np2svec(y0.copy(), self.yy)
        np2svec(yp0.copy(), self.yp)

        # 4) and 5) Create matrix and linear solver - they must match
        self._create_linsolver()

        # 6) Create nonlinear solver object (skip, use default Newton solver)

        # 7) Create IDA object
        self.mem = IDACreate(self.ctx)
        if self.mem is NULL:
            raise MemoryError("IDACreate returned a NULL pointer for 'mem'.")

        # 8) Initialize IDA solver
        flag = IDAInit(self.mem, _resfn_wrapper, t0, self.yy, self.yp)
        if flag < 0:
            raise RuntimeError("IDAInit - " + IDAMESSAGES[flag])

        # 9) Specify integration tolerances
        self._set_tolerances()

        # 10) Attach the linear solver
        flag = IDASetLinearSolver(self.mem, self.LS, self.A)
        if flag < 0:
            raise RuntimeError("IDASetLinearSolver - " + LSMESSAGES[flag])

        # 11) Set linear solver optional inputs
        jacfn = self._options["jacfn"]
        if jacfn:
            flag = IDASetJacFn(self.mem, _jacfn_wrapper)
            if flag < 0:
                raise RuntimeError("IDASetJacFn - " + LSMESSAGES[flag])

        # 12) Attach nonlinear solver module (skip, use default Newton solver)

        # 13) Set nonlinear solver optional inputs
        cdef int max_nonlin_iters = <int> self._options["max_nonlin_iters"]
        flag = IDASetMaxNonlinIters(self.mem, max_nonlin_iters)
        if flag < 0:
            raise RuntimeError("IDASetMaxNonlinIters - " + IDAMESSAGES[flag])

        cdef int max_conv_fails = <int> self._options["max_conv_fails"]
        flag = IDASetMaxConvFails(self.mem, max_conv_fails)
        if flag < 0:
            raise RuntimeError("IDASetMaxConvFails - " + IDAMESSAGES[flag])

        # 14) Specify rootfinding problem
        eventsfn = self._options["eventsfn"]
        num_events = self._options["num_events"]
        if eventsfn:
            flag = IDARootInit(self.mem, <int> num_events, _eventsfn_wrapper)
            if flag < 0:
                raise RuntimeError("IDARootInit - " + IDAMESSAGES[flag])

            np_eventsdir = np.array(eventsfn.direction, dtype=INT_TYPE)

            flag = IDASetRootDirection(self.mem, <int*> np_eventsdir.data)
            if flag < 0:
                raise RuntimeError("IDASetRootDirection - " + IDAMESSAGES[flag])

        # 15) Set optional inputs
        SUNContext_ClearErrHandlers(self.ctx)
        SUNContext_PushErrHandler(self.ctx, _err_handler, NULL)

        flag = IDASetUserData(self.mem, <void*> self.aux)
        if flag < 0:
            raise RuntimeError("IDASetUserData - " + IDAMESSAGES[flag])

        np_algidx = np.ones(self.NEQ, DTYPE)
        if self._options["algebraic_idx"]:
            for idx in self._options["algebraic_idx"]:
                np_algidx[idx] = 0.0

        self.algidx = N_VNew_Serial(self.NEQ, self.ctx)
        np2svec(np_algidx, self.algidx)

        flag = IDASetId(self.mem, self.algidx)
        if flag < 0:
            raise RuntimeError("IDASetId - " + IDAMESSAGES[flag])

        cdef sunrealtype first_step = <sunrealtype> self._options["first_step"] 
        flag = IDASetInitStep(self.mem, first_step)
        if flag < 0:
            raise RuntimeError("IDASetInitStep - " + IDAMESSAGES[flag])

        cdef sunrealtype min_step = <sunrealtype> self._options["min_step"] 
        flag = IDASetMinStep(self.mem, min_step)
        if flag < 0:
            raise RuntimeError("IDASetMinStep - " + IDAMESSAGES[flag])

        cdef sunrealtype max_step = <sunrealtype> self._options["max_step"] 
        flag = IDASetMaxStep(self.mem, max_step)
        if flag < 0:
            raise RuntimeError("IDASetMaxStep - " + IDAMESSAGES[flag])

        cdef int max_order = <int> self._options["max_order"]
        flag = IDASetMaxOrd(self.mem, max_order)
        if flag < 0:
            raise RuntimeError("IDASetMaxOrd - " + IDAMESSAGES[flag])

        cdef long int max_num_steps = <long int> self._options["max_num_steps"]
        flag = IDASetMaxNumSteps(self.mem, max_num_steps)
        if flag < 0:
            raise RuntimeError("IDASetMaxNumSteps - " + IDAMESSAGES[flag])

        constraints_idx = self._options["constraints_idx"]
        constraints_type = self._options["constraints_type"]
        if constraints_idx:

            np_constraints = np.zeros(self.NEQ, DTYPE)
            for idx, val in zip(constraints_idx, constraints_type):
                np_constraints[idx] = val

            self.constraints = N_VNew_Serial(self.NEQ, self.ctx)
            np2svec(np_constraints, self.constraints)

            flag = IDASetConstraints(self.mem, self.constraints)
            if flag < 0:
                raise RuntimeError("IDASetConstraints - " + IDAMESSAGES[flag])

        self._size = self.NEQ
        self._malloc = True
        
        return flag

    cdef _init_step(self, sunrealtype t0, np.ndarray[DTYPE_t, ndim=1] y0,
                    np.ndarray[DTYPE_t, ndim=1] yp0):

        cdef int flag
        cdef int ic_opt
        cdef sunrealtype ic_t0

        yy_tmp = y0.copy()
        yp_tmp = yp0.copy()

        # Steps 1-15 handled in _setup()... only runs on first call, or if the
        # size of the system changes.

        if not self._malloc:
            flag = self._setup(t0, y0, yp0)
        
        elif self._size != y0.size:
            self._free_memory()
            self._setup(t0, y0, yp0)

        else:

            np2svec(yy_tmp, self.yy)
            np2svec(yp_tmp, self.yp)

            flag = IDAReInit(self.mem, t0, self.yy, self.yp)
            if flag < 0:
                raise RuntimeError("IDAReInit - " + IDAMESSAGES[flag])

        # 16) Correct initial values
        calc_initcond = self._options["calc_initcond"]
        ic_t0 = t0 + self._options["calc_init_dt"]

        if calc_initcond == "y0":
            ic_opt = IDA_Y_INIT
        elif calc_initcond == "yp0":
            ic_opt = IDA_YA_YDP_INIT

        if calc_initcond:
            flag = IDACalcIC(self.mem, ic_opt, ic_t0)
            if flag < 0:
                raise RuntimeError("IDACalcIC - " + IDAMESSAGES[flag])

            flag = IDAGetConsistentIC(self.mem, self.yy, self.yp)
            if flag < 0:
                raise RuntimeError("IDAGetConsistentIC - " + IDAMESSAGES[flag])

        self._initialized = True

        # Construct result instance to return
        svec2np(self.yy, yy_tmp)
        svec2np(self.yp, yp_tmp)

        nfev, njev = _collect_stats(self.mem)

        result = IDAResult(
            message=IDAMESSAGES[flag], success=flag >= 0, status=flag,
            t=t0, y=yy_tmp.copy(), yp=yp_tmp.copy(),
            i_events=None, t_events=None, y_events=None, yp_events=None,
            nfev=nfev, njev=njev,
        )

        return result

    cdef _step(self, sunrealtype tt, object method, object tstop):
        cdef int itask
        cdef sunrealtype tout

        # Setup step type:
        if method == "normal":  # output solution at tt
            itask = IDA_NORMAL
        elif method == "onestep":  # output after one internal step toward tt
            itask = IDA_ONE_STEP

        if isinstance(tstop, (int, float)):
            flag = IDASetStopTime(self.mem, <sunrealtype> tstop)
            if flag < 0:
                raise RuntimeError("IDASetStopTime - " + IDAMESSAGES[flag])

        yy_tmp = self.aux.np_yy
        yp_tmp = self.aux.np_yp
        
        # 17) Advance solution in time
        flag = IDASolve(self.mem, tt, &tout, self.yy, self.yp, itask)

        svec2np(self.yy, yy_tmp)
        svec2np(self.yp, yp_tmp)

        if flag == IDA_ROOT_RETURN:
            _ = _handle_events(self.mem, self.aux, tout, yy_tmp, yp_tmp)

        if self.aux.eventsfn:
            i_ev, t_ev, y_ev, yp_ev = _collect_events(self.aux)
        else:
            i_ev, t_ev, y_ev, yp_ev = [None]*4

        nfev, njev = _collect_stats(self.mem)

        result = IDAResult(
            message=IDAMESSAGES[flag], success=flag >= 0, status=flag,
            t=tout, y=yy_tmp.copy(), yp=yp_tmp.copy(),
            i_events=i_ev, t_events=t_ev, y_events=y_ev, yp_events=yp_ev,
            nfev=nfev, njev=njev,
        )

        flag = IDAClearStopTime(self.mem)
        if flag < 0:
            raise RuntimeError("IDAClearStopTime - " + IDAMESSAGES[flag])

        return result

    cdef _normal_solve(self, np.ndarray[DTYPE_t, ndim=1] tspan,
                             np.ndarray[DTYPE_t, ndim=1] y0,
                             np.ndarray[DTYPE_t, ndim=1] yp0
        ):

        cdef int ind
        cdef int flag
        cdef int stop
        cdef sunrealtype tt
        cdef sunrealtype tend

        _ = self._init_step(tspan[0], y0, yp0)

        # Setup solution storage
        tt_out = np.empty(tspan.size, DTYPE)
        yy_out = np.empty((tspan.size, self.NEQ), DTYPE)
        yp_out = np.empty((tspan.size, self.NEQ), DTYPE)

        yy_tmp = self.aux.np_yy
        yp_tmp = self.aux.np_yp

        tt_out[0] = tspan[0]
        svec2np(self.yy, yy_out[0, :])
        svec2np(self.yp, yp_out[0, :])

        # 17) Advance solution in time
        stop = 0
        ind = 1

        flag = IDASetStopTime(self.mem, <sunrealtype> tspan[-1])
        if flag < 0:
            raise RuntimeError("IDASetStopTime - " + IDAMESSAGES[flag])

        while True:
            tend = tspan[ind]

            flag = IDASolve(self.mem, tend, &tt, self.yy, self.yp, IDA_NORMAL)

            svec2np(self.yy, yy_tmp)
            svec2np(self.yp, yp_tmp)

            if flag == IDA_ROOT_RETURN:
                stop = _handle_events(self.mem, self.aux, tt, yy_tmp, yp_tmp)
            elif flag == IDA_TSTOP_RETURN:
                stop = 1
            elif ind == len(tspan) - 1:
                stop = 1
            elif flag < 0:
                stop = 1

            if flag == IDA_ROOT_RETURN and not stop:
                pass
            else:
                tt_out[ind] = tt
                yy_out[ind, :] = yy_tmp
                yp_out[ind, :] = yp_tmp

                ind += 1

            if stop:
                break
            elif PyErr_CheckSignals() == -1:
                return

        if self.aux.eventsfn:
            i_ev, t_ev, y_ev, yp_ev = _collect_events(self.aux)
        else:
            i_ev, t_ev, y_ev, yp_ev = [None]*4

        nfev, njev = _collect_stats(self.mem)

        result = IDAResult(
            message=IDAMESSAGES[flag], success=flag >= 0, status=flag,
            t=tt_out[:ind], y=yy_out[:ind], yp=yp_out[:ind],
            i_events=i_ev, t_events=t_ev, y_events=y_ev, yp_events=yp_ev,
            nfev=nfev, njev=njev,
        )

        flag = IDAClearStopTime(self.mem)
        if flag < 0:
            raise RuntimeError("IDAClearStopTime - " + IDAMESSAGES[flag])      

        return result

    cdef _onestep_solve(self, np.ndarray[DTYPE_t, ndim=1] tspan,
                              np.ndarray[DTYPE_t, ndim=1] y0,
                              np.ndarray[DTYPE_t, ndim=1] yp0
        ):

        cdef int ind
        cdef int flag
        cdef int stop
        cdef sunrealtype tt
        cdef sunrealtype tend

        _ = self._init_step(tspan[0], y0, yp0)

        # Setup solution storage
        # Pre-allocate some memory (for 1000 time steps) to fill. Periodically
        # add 500 more more in if the pre-allocated memory gets filled.
        tt_out = np.empty(1000, DTYPE)
        yy_out = np.empty((1000, self.NEQ), DTYPE)
        yp_out = np.empty((1000, self.NEQ), DTYPE)

        extra_t = np.empty(500, DTYPE)
        extra_y = np.empty((500, self.NEQ), DTYPE)

        yy_tmp = self.aux.np_yy
        yp_tmp = self.aux.np_yp

        tt_out[0] = tspan[0]
        svec2np(self.yy, yy_out[0, :])
        svec2np(self.yp, yp_out[0, :])

        tend = tspan[-1]
        stop = 0
        ind = 1

        flag = IDASetStopTime(self.mem, tend)
        if flag < 0:
            raise RuntimeError("IDASetStopTime - " + IDAMESSAGES[flag])

        # 17) Advance solution in time
        while True:
            flag = IDASolve(self.mem, tend, &tt, self.yy, self.yp, IDA_ONE_STEP)

            svec2np(self.yy, yy_tmp)
            svec2np(self.yp, yp_tmp)

            if flag == IDA_ROOT_RETURN:
                stop = _handle_events(self.mem, self.aux, tt, yy_tmp, yp_tmp)
            elif flag == IDA_TSTOP_RETURN:
                stop = 1
            elif flag < 0:
                stop = 1

            if ind == tt_out.size - 1:
                tt_out = np.concatenate((tt_out, extra_t))
                yy_out = np.concatenate((yy_out, extra_y))
                yp_out = np.concatenate((yp_out, extra_y))

            if flag == IDA_ROOT_RETURN and not stop:
                pass
            else:
                tt_out[ind] = tt
                yy_out[ind, :] = yy_tmp
                yp_out[ind, :] = yp_tmp

                ind += 1

            if stop:
                break
            elif PyErr_CheckSignals() == -1:
                return

        if self.aux.eventsfn:
            i_ev, t_ev, y_ev, yp_ev = _collect_events(self.aux)
        else:
            i_ev, t_ev, y_ev, yp_ev = [None]*4

        nfev, njev = _collect_stats(self.mem)

        result = IDAResult(
            message=IDAMESSAGES[flag], success=flag >= 0, status=flag,
            t=tt_out[:ind], y=yy_out[:ind], yp=yp_out[:ind],
            i_events=i_ev, t_events=t_ev, y_events=y_ev, yp_events=yp_ev,
            nfev=nfev, njev=njev,
        )

        flag = IDAClearStopTime(self.mem)
        if flag < 0:
            raise RuntimeError("IDAClearStopTime - " + IDAMESSAGES[flag])

        return result

    def init_step(self, DTYPE_t t0, object y0, object yp0):
        
        y0 = np.asarray(y0, dtype=DTYPE)
        yp0 = np.asarray(yp0, dtype=DTYPE)
        
        return self._init_step(t0, y0, yp0)

    def step(self, DTYPE_t t, object method, object tstop):

        valid = {"normal", "onestep",}
        if method not in valid:
            raise ValueError(f"'method' is invalid. Valid values are {valid}.")
        elif not self._initialized:
            raise ValueError("'init_step' must be run prior to 'step'.")

        if tstop is None:
            pass
        elif not isinstance(tstop, (int, float)):
            raise TypeError("'tstop' must be type float, or None.")
        
        return self._step(t, method, tstop)

    def solve(self, object tspan, object y0, object yp0):

        tspan = np.asarray(tspan, dtype=DTYPE)
        y0 = np.asarray(y0, dtype=DTYPE)
        yp0 = np.asarray(yp0, dtype=DTYPE)

        diff = np.diff(tspan)
        if not all(diff > 0) ^ all(diff < 0):
            raise ValueError("'tspan' must stictly increase or decrease.")

        if tspan.size > 2:
            soln = self._normal_solve(tspan, y0, yp0)
        elif tspan.size == 2:
            soln = self._onestep_solve(tspan, y0, yp0)
        else:
            raise ValueError("'tspan' length must be >= 2.")

        self._initialized = False 

        return soln

    def __dealloc__(self):
        self._free_memory()


cdef _prepare_events(object eventsfn, int num_events):

    # eventsfn.terminal
    if not hasattr(eventsfn, "terminal"):
        eventsfn.terminal = [True]*num_events

    terminal = eventsfn.terminal
    if not isinstance(terminal, Iterable):
        raise TypeError("'eventsfn.terminal' must be type Iterable.")
    elif not all(isinstance(x, (bool, int)) for x in terminal):
        raise TypeError("All 'eventsfn.terminal' values must be bool or int.")
    elif not all(int(x) >= 0 for x in terminal):
        raise ValueError("At least one 'eventsfn.terminal' value is invalid."
                         " Values must be interpretable as int(x) >= 0.")
    elif len(terminal) != num_events:
        raise ValueError("'eventsfn.terminal' length != 'num_events'.")

    # eventsfn.direction
    if not hasattr(eventsfn, "direction"):
        eventsfn.direction = [0]*num_events

    direction = eventsfn.direction
    if not isinstance(direction, Iterable):
        raise TypeError("'eventsfn.direction' must be type Iterable.")
    elif not all(x in (-1, 0, 1) for x in direction):
        raise ValueError(f"At least one 'eventsfn.direction' value is invalid."
                          " Values must be in {-1, 0, 1}.")
    elif len(direction) != num_events:
        raise ValueError("'eventsfn.direction' length != 'num_events'.")

    # add extra fields for _handle_events function
    eventsfn._i_tmp = np.zeros(num_events, dtype=INT_TYPE)
    eventsfn._i_cnt = np.zeros(num_events, dtype=INT_TYPE)

    eventsfn._i = []
    eventsfn._t = []
    eventsfn._y = []
    eventsfn._yp = []

    eventsfn._max_events = []
    for i, term in enumerate(terminal):
        if term == False:
            eventsfn._max_events.append(np.inf)
        elif term == True:
            eventsfn._max_events.append(1)
        else:
            eventsfn._max_events.append(term)   


cdef _handle_events(void* mem, AuxData aux, sunrealtype tt, np.ndarray yy_tmp,
                    np.ndarray yp_tmp):

    cdef int flag
    cdef int stop
    cdef np.ndarray i_tmp

    fn = aux.eventsfn
    i_tmp = fn._i_tmp

    flag = IDAGetRootInfo(mem, <int*> i_tmp.data)
    if flag < 0:
        raise RuntimeError("IDAGetRootInfo - " + IDAMESSAGES[flag])

    fn._i.append(i_tmp.copy())
    fn._t.append(tt)
    fn._y.append(yy_tmp.copy())
    fn._yp.append(yp_tmp.copy())

    fn._i_cnt[i_tmp != 0] += 1
    if any(fn._i_cnt >= fn._max_events):
        stop = 1
    else:
        stop = 0

    return stop


cdef _collect_events(AuxData aux):

    fn = aux.eventsfn

    i_events = np.asarray(fn._i, INT_TYPE) if fn._i else None
    t_events = np.asarray(fn._t, DTYPE) if fn._t else None
    y_events = np.asarray(fn._y, DTYPE) if fn._y else None
    yp_events = np.asarray(fn._yp, DTYPE) if fn._yp else None

    return i_events, t_events, y_events, yp_events


cdef _collect_stats(void* mem):
    cdef long int nfev
    cdef long int njev

    flag = IDAGetNumResEvals(mem, &nfev)
    if flag < 0:
        raise RuntimeError("IDAGetNumResEvals - " + IDAMESSAGES[flag])

    flag = IDAGetNumJacEvals(mem, &njev)
    if flag < 0:
        raise RuntimeError("IDAGetNumJacEvals - " + LSMESSAGES[flag])

    return nfev, njev


def _check_signature(name: str, func: Callable, expected: tuple[int]) -> int:
    """Check 'resfn', 'eventsfn', and 'jacfn' signatures."""

    argspec = getfullargspec(func)
    if isinstance(func, MethodType):  # if method, remove self/cls
        argspec.args.pop(0)
    elif argspec.args[0] in ("self", "cls"):
        argspec.args.pop(0)

    if argspec.varargs or argspec.varkw:
        raise ValueError(f"'{name}' cannot include *args or **kwargs.")
    elif argspec.kwonlyargs:
        raise ValueError(f"'{name}' cannot include keyword-only args.")

    if name == "resfn" and len(argspec.args) not in expected:
        raise ValueError(f"'{name}' has an invalid signature. It must only"
                          " have 4 (w/o userdata) or 5 (w/ userdata) args.")
    elif len(argspec.args) not in expected:
        raise ValueError(f"'{name}' signature is inconsistent with 'resfn'."
                         " look for a missing or extraneous 'userdata' arg.")
    
    if name == "resfn" and len(argspec.args) == 4:
        with_userdata = 0
    elif name == "resfn" and len(argspec.args) == 5:
        with_userdata = 1
    else:
        with_userdata = None

    return with_userdata


def _check_options(options: dict) -> None:

    # resfn
    if not isinstance(options["resfn"], Callable):
        raise TypeError("'resfn' must be type Callable.")
    else:
        expected = (4, 5)
        with_userdata = _check_signature("resfn", options["resfn"], expected)

    # userdata    
    if with_userdata and options["userdata"] is None:
        raise ValueError("'userdata' cannot be None if 'resfn' has 5 args.")
    elif options["userdata"] and not with_userdata:
        warn("'userdata' will be ignored since 'resfn' only has 4 args.")

    # calc_initcond
    valid =  {"y0", "yp0", None}
    calc_initcond = options["calc_initcond"]
    if calc_initcond is None:
        pass
    elif not isinstance(calc_initcond, str):
        raise TypeError("'calc_initcond' must be type str.")
    elif calc_initcond not in valid:
        raise ValueError(f"{calc_initcond=} is invalid. Must be in {valid}.")

    # calc_init_dt
    if not isinstance(options["calc_init_dt"], (int, float)):
        raise TypeError("'calc_init_dt' must be type float.")
    elif options["calc_init_dt"] == 0.:
        raise ValueError("'calc_init_dt' cannot be 0.")

    # algebraic_idx
    algebraic_idx = options["algebraic_idx"]
    if algebraic_idx is None:
        pass
    elif not isinstance(algebraic_idx, Iterable):
        raise TypeError("'algebraic_idx' must be type Iterable.")
    elif not all(isinstance(x, int) for x in algebraic_idx):
        raise TypeError("All 'algebraic_idx' values must be type int.")
    
    # first_step
    if not isinstance(options["first_step"], (int, float)):
        raise TypeError("'first_step' must be type float.")
    elif options["first_step"] < 0.:
        raise ValueError("'first_step' must be positive or zero.")
        
    # min_step
    if not isinstance(options["min_step"], (int, float)):
        raise TypeError("'min_step' must be type float.")
    elif options["min_step"] < 0.:
        raise ValueError("'min_step' must be positive or zero.")

    # max_step
    if not isinstance(options["max_step"], (int, float)):
        raise TypeError("'max_step' must be type float.")
    elif options["max_step"] < 0.:
        raise ValueError("'max_step' must be positive or zero.")
    elif options["max_step"] < options["min_step"]:
        raise ValueError("'max_step' cannot be smaller than 'min_step'.")

    # rtol
    if not isinstance(options["rtol"], float):
        raise TypeError("'rtol' must be type float.")

    # atol
    if not isinstance(options["atol"], (float, Iterable)):
        raise TypeError("'atol' must be type float or Iterable.")

    # linsolver
    valid =  {"dense", "band",}
    linsolver = options["linsolver"]
    if not isinstance(linsolver, str):
        raise TypeError("'linsolver' must be type str.")
    elif linsolver not in valid:
        raise ValueError(f"{linsolver=} is invalid. Must be in {valid}.")

    # lband
    lband = options["lband"]
    if lband is None:
        pass
    elif not isinstance(lband, int):
        raise TypeError("'lband' must be type int.")
    elif lband < 0:
        raise ValueError("'lband' must be positive or zero.")

    # uband
    uband = options["uband"]
    if uband is None:
        pass
    elif not isinstance(uband, int):
        raise TypeError("'uband' must be type int.")
    elif uband < 0:
        raise ValueError("'uband' must be positive or zero.")

    # consistency between linsolver and lband/uband
    if linsolver == "band" and (lband is None or uband is None):
        raise ValueError("'lband' and 'uband' can't be None if 'linsolver'"
                         " is 'band'.")
    elif linsolver == "dense" and (lband is not None or uband is not None):
        warn("'lband', 'uband' will be ignored since 'linsolver' is 'dense'.")

    # max_order
    if not isinstance(options["max_order"], int):
        raise TypeError("'order' must be type int.")
    elif options["max_order"] < 1 or options["max_order"] > 5:
        raise ValueError("'order' must be in range [1, 5].")

    # max_num_steps
    if not isinstance(options["max_num_steps"], int):
        raise TypeError("'max_num_steps' must be type int.")
    elif not options["max_num_steps"] > 0:
        raise ValueError("'max_num_steps' must be > 0.")

    # max_nonlin_iters
    if not isinstance(options["max_nonlin_iters"], int):
        raise TypeError("'max_nonlin_iters' must be type int.")
    elif not options["max_nonlin_iters"] > 0:
        raise ValueError("'max_nonlin_iters' must be > 0.")

    # max_conv_fails
    if not isinstance(options["max_conv_fails"], int):
        raise TypeError("'max_conv_fails' must be type int.")
    elif not options["max_conv_fails"] > 0:
        raise ValueError("'max_conv_fails' must be > 0.")

    # constraints_idx
    constraints_idx = options["constraints_idx"]
    if constraints_idx is None:
        pass
    elif not isinstance(constraints_idx, Iterable):
        raise TypeError("'constraints_idx' must be type Iterable.")
    elif not all(isinstance(x, int) for x in constraints_idx):
        raise TypeError("All 'constraints_idx' values must be type int.")

    # constraints_type
    constraints_type = options["constraints_type"]
    if constraints_type is None:
        pass
    elif not isinstance(constraints_type, Iterable):
        raise TypeError("'constraints_type' must be type Iterable")
    elif not all(x in (-2, -1, 1, 2) for x in constraints_type):
        raise ValueError(f"At least one 'constraints_type' value is invalid."
                          " Values must be in {-2, -1, 1, 2}.")

    # consistency between constraints index and types
    if constraints_idx is None and constraints_type is None:
        pass 
    elif (constraints_idx is None) ^ (constraints_type is None):
        raise ValueError("'constraints_idx' and 'constraints_type' must both"
                         " be set or both be None.")
    elif len(constraints_idx) != len(constraints_type):
        raise ValueError("'constraints_idx' and 'constraints_type' lengths"
                         " must be the same.")

    # eventsfn
    eventsfn = options["eventsfn"]
    if eventsfn is None:
        pass
    elif not isinstance(eventsfn, Callable):
        raise TypeError("'eventsfn' must be type Callable.")
    else:
        expected = (4 + with_userdata,)
        _ = _check_signature("eventsfn", eventsfn, expected)

    # num_events
    num_events = options["num_events"]    
    if num_events == 0:
        pass
    elif not isinstance(num_events, int):
        raise TypeError("'num_events' must be type int.")
    elif num_events < 0:
        raise ValueError("'num_events' must be positive or zero.")

    # consistency between eventsfn and num_events
    if eventsfn and not num_events:
        raise ValueError("'num_events' cannot be 0 if 'eventsfn' is set.")
    elif num_events and not eventsfn:
        warn("'num_events' will be ignored since 'eventsfn' is not set.")

    # prepare events if eventsfn is not None
    if eventsfn:
        _prepare_events(eventsfn, num_events)
        
    # jacfn
    jacfn = options["jacfn"]
    if jacfn is None:
        pass
    elif not isinstance(jacfn, Callable):
        raise TypeError("'jacfn' must be type Callable.")
    else:
        expected = (6 + with_userdata,)
        _ = _check_signature("jacfn", jacfn, expected)
