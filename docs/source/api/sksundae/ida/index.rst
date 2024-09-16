sksundae.ida
============

.. py:module:: sksundae.ida


Classes
-------

.. autoapisummary::

   sksundae.ida.IDA
   sksundae.ida.IDAResult


Module Contents
---------------

.. py:class:: IDA(resfn, **options)

   SUNDIALS IDA solver.

   This class wraps the implicit differential algebraic (IDA) solver from
   SUNDIALS. It can be used to solve both ordinary differential equations
   (ODEs) and differiential agebraic equatinos (DAEs).

   :param resfn: Residual function with signature ``f(t, y, yp, res[, userdata])``.
                 If 'resfn' has return values, they are ignored. Instead of using
                 returns, the solver interacts directly with the 'res' array memory.
                 For more info see the notes.
   :type resfn: Callable
   :param \*\*options: Keyword arguments to describe the solver options. A full list of
                       names, types, descriptions, and defaults is given below.
   :type \*\*options: dict, optional
   :param userdata: Additional data object to supply to all user-defined callables. If
                    'resfn' takes in 5 arguments, including the optional 'userdata',
                    then this option cannot be None (default). See notes for more info.
   :type userdata: object or None, optional
   :param calc_initcond: Specifies which initial condition, if any, to calculate prior to
                         the first time step. The options 'y0' and 'yp0' will correct 'y0'
                         or 'yp0' values at 't0', respectively. When not None (default),
                         the 'calc_init_dt' value should be used to specify the direction
                         of integration.
   :type calc_initcond: {'y0', 'yp0', None}, optional
   :param calc_init_dt: Relative time step to take during the initial condition correction.
                        Positive vs negative values provide the direction of integration as
                        forwards or backwards, respectively. The default is 0.01.
   :type calc_init_dt: float, optional
   :param algebraic_idx: Specifies indices 'i' in the 'y[i]' state variable array that are
                         purely algebraic. This option should always be provided for DAEs;
                         otherwise, the solver can be unstable. The default is None.
   :type algebraic_idx: array_like[int] or None, optional
   :param first_step: Specifies the initial step size. The default is 0, which uses an
                      estimated value internally determined by SUNDIALS.
   :type first_step: float, optional
   :param min_step: Minimum allowed step size. The default is 0.
   :type min_step: float, optional
   :param max_step: Maximum allowed step size. Use 0 (default) for unbounded steps.
   :type max_step: float, optional
   :param rtol: Relative tolerance. For example, 1e-4 means errors are controlled
                to within 0.01%. It is recommended to not use values larger than
                1e-3 nor smaller than 1e-15. The default is 1e-5.
   :type rtol: float, optional
   :param atol: Absolute tolerance. Use be a scalar float to apply the same value
                for all state variables, or an array with a length matching 'y' to
                provide tolerances specific to each variable. The default is 1e-6.
   :type atol: float or array_like[float], optional
   :param linsolver: Choice of linear solver. When using 'band', don't forget to provide
                     'lband' and 'uband' values. The default is 'dense'.
   :type linsolver: {'dense', 'band'}, optional
   :param lband: Lower Jacobian bandwidths. Given a DAE system ``0 = F(t, y, yp)``,
                 the Jacobian is ``J = dF_i/dy_j + c_j*dF_i/dyp_j`` where 'c_j' is
                 determined internally from step size and order. 'lband' should be
                 set to the max distance between the main diagonal and the non-zero
                 elements below the diagonal. This option cannot be None (default)
                 if 'linsolver' is 'band'.
   :type lband: int or None, optional
   :param uband: Upper Jacobian bandwidth. See 'lband' for the Jacobian description.
                 'uband' should be set to the max distance between the main diagonal
                 and the non-zero elements above the diagonal. This option cannot be
                 None (default) if 'linsolver' is 'band'.
   :type uband: int or None, optional
   :param max_order: Specifies the maximum order for the linear multistep BDF method.
                     The value must be in the range [1, 5]. The default is 5.
   :type max_order: int, optional
   :param max_num_steps: Specifies the maximum number of steps taken by the solver in each
                         attempt to reach the next output time. The default is 500.
   :type max_num_steps: int, optional
   :param max_nonlin_iters: Specifies the maximum number of nonlinear solver iterations in one
                            step. The default is 4.
   :type max_nonlin_iters: int, optional
   :param max_conv_fails: Specifies the max number of nonlinear solver convergence failures
                          in one step. The default is 10.
   :type max_conv_fails: int, optional
   :param constraints_idx: Specifies indices 'i' in the 'y[i]' state variable array for which
                           inequality constraints should be applied. Constraints types must be
                           specified in 'constraints_type', see below. The default is None.
   :type constraints_idx: array_like[int] or None, optional
   :param constraints_type: If 'constraints_idx' is not None, then this option must include an
                            array of equal length specifying the types of constraints to apply.
                            Values should be in ``{-2, -1, 1, 2}`` which apply ``y[i] < 0``,
                            ``y[i] <= 0``, ``y[i] >=0,`` and ``y[i] > 0``, respectively. The
                            default is None.
   :type constraints_type: array_like[int] or None, optional
   :param eventsfn: Events function with signature ``g(t, y, yp, events[, userdata])``.
                    Return values from this function are ignored. Instead, the solver
                    directly interacts with the 'events' array. Each 'events[i]' should
                    be an expression that triggers an event when equal to zero. If None
                    (default), no events are tracked. See the notes for more info. The
                    option 'num_events' must be set if 'eventsfn' is not None so memory
                    can be allocated and managed for the events array. The 'eventsfn'
                    can also have the following attributes:

                        terminal: list[bool, int], optional
                            A list with length 'num_events' that tells how the solver
                            how to respond to each event. If boolean, the solver will
                            terminate when True and will simply record the event when
                            False. If integer, termination occurs at the given number
                            of occurrences. The default is ``[True]*num_events``.
                        direction: list[int], optional
                            A list with length 'num_events' that tells the solver which
                            event directions to track. Values must be in ``{-1, 0, 1}``.
                            Negative values will only trigger events when the slope is
                            negative (i.e., 'events[i]' went from positive to negative).
                            Alternatively, positive values track events with positive
                            slope. If zero, either direction triggers the event. When
                            not assigned, ``direction = [0]*num_events``.

                    You can assign attributes like ``eventsfn.terminal = [True]`` to
                    any function in Python, after it has been defined.
   :type eventsfn: Callable or None, optional
   :param num_events: Number of events to track. Must be greater than zero if 'eventsfn'
                      is not None. The default is 0.
   :type num_events: int, optional
   :param jacfn: Jacobian function like ``J(t, y, yp, res, cj, JJ[, userdata])``.
                 The function should fill the pre-allocated 2D matrix 'JJ' with the
                 values defined by ``JJ[i,j] = dres_i/dy_j + cj*dres_i/dyp_j``. An
                 internal finite difference method is applied when None (default).
                 As with other user-defined callables, return values from 'jacfn'
                 are ignored. See notes for more info.
   :type jacfn: Callable or None, optional

   .. rubric:: Notes

   Return values from 'resfn', 'eventsfn', and 'jacfn' are ignored by the
   solver. Instead the solver directly reads from pre-allocated memory.
   The 'res', 'events', and 'JJ' arrays from each user-defined callable
   should be filled within each respective function. When setting values
   across the entire array/matrix at once, don't forget to use ``[:]`` to
   fill the existing array rather than overwriting it. For example, using
   ``res[:] = F(t, y, yp)`` is correct whereas ``res = F(t, y, yp)`` is
   not. Using this method of pre-allocated memory helps pass data between
   Python and the SUNDIALS C functions. It also keeps the solver fast,
   especially for large problems.

   When 'resfn' (or 'eventsfn', or 'jacfn') require data outside of their
   normal arguments, you can supply 'userdata' as an option. When given,
   'userdata' must appear in the function signatures for all of 'resfn',
   'eventsfn' (when not None), and 'jacfn' (when not None), even if it is
   not used in all of these functions. Note that 'userdata' only takes up
   one argument position; however, 'userdata' can be any Python object.
   Therefore, if you need to pass more than one extra argument then you
   should pack all of the data into a single tuple, dict, dataclass, etc.
   and pass them all together as 'userdata'. The data can be unpacked as
   needed within a function.

   .. rubric:: Examples

   The following example solves the Robertson problem, which is a classic
   test problem for programs that solve stiff ODEs. A full description of
   the problem is provided by `MATLAB`_. Note that in initializing the
   solver, ``algebraic_idx=[2]`` specifies ``y[2]`` is purely algebraic,
   and ``calc_initcond='yp0'`` tells the solver to determine the values
   for 'yp0' at 'tspan[0]' before starting to integrate. That is why it
   can be initialized as an array of zeros even though plugging in 'y0'
   to the residuals expressions actually gives ``yp0 = [-0.04, 0.04, 0]``.
   The initialization is checked against the correct answer after solving.

   .. _MATLAB:
       https://mathworks.com/help/matlab/math/
       solve-differential-algebraic-equations-daes.html

   .. code-block:: python

       import numpy as np
       import sundae as sun
       import matplotlib.pyplot as plt

       def resfn(t, y, yp, res):
           res[0] = yp[0] + 0.04*y[0] - 1e4*y[1]*y[2]
           res[1] = yp[1] - 0.04*y[0] + 1e4*y[1]*y[2] + 3e7*y[1]**2
           res[2] = y[0] + y[1] + y[2] - 1.0

       solver = sun.ida.IDA(resfn, algebraic_idx=[2], calc_initcond='yp0')

       tspan = np.hstack([0, 4*np.logspace(-6, 6)])
       y0 = np.array([1, 0, 0])
       yp0 = np.zeros_like(y0)

       soln = solver.solve(tspan, y0, yp0)
       assert np.allclose(soln.yp[0], [-0.04, 0.04, 0], rtol=1e-3)

       soln.y[:, 1] *= 1e4
       plt.semilogx(soln.t, soln.y)
       plt.show()


   .. py:method:: init_step(t0, y0, yp0)

      Initializes the solver.

      This method is called automatically when using 'solve'. However, it
      must be run manually, before the 'step' method, when solving with a
      step-by-step approach.

      :param t0: Initial value of time.
      :type t0: float
      :param y0: State variable values at 't0'. The length must match that of 'yp0'
                 and the number of residual equations in 'resfn'.
      :type y0: array_like[float], shape(m,)
      :param yp0: Time derivatives for the 'y0' array, evaluated at 't0'. The length
                  and indexing should be consistent with 'y0'.
      :type yp0: array_like[float], shape(m,)

      :returns: :class:`~sundae.ida.IDAResult` -- Custom output class for IDA solutions. Includes pretty-printing
                consistent with scipy outputs. See the class definition for more
                information.

      :raises MemoryError: Failed to allocate memory for the IDA solver.
      :raises RuntimeError: A SUNDIALS function returned NULL or was unsuccessful.
      :raises ValueError: 'y0' and 'yp0' must be the same length.



   .. py:method:: solve(tspan, y0, yp0)

      Return the solution across 'tspan'.

      :param tspan: Solution time span. If ``len(tspan) == 2``, the solution will save
                    at internally chosen time steps. If ``len(tspan) > 2``, the values
                    themselves are used to create the solution output.
      :type tspan: array_like[float], shape(n >= 2,)
      :param y0: State variable values at 'tspan[0]'. The length must match that of
                 'yp0' and the number of residual equations in 'resfn'.
      :type y0: array_like[float], shape(m,)
      :param yp0: Time derivatives for the 'y0' array, evaluated at 'tspan[0]'. The
                  length and indexing should be consistent with 'y0'.
      :type yp0: array_like[float], shape(m,)

      :returns: :class:`~sundae.ida.IDAResult` -- Custom output class for IDA solutions. Includes pretty-printing
                consistent with scipy outputs. See the class definition for more
                information.

      :raises ValueError: 'tspan' must be strictly increasing or decreasing.
      :raises ValueError: 'tspan' length must be >= 2.



   .. py:method:: step(t, method='normal', tstop=None)

      Return the solution at time 't'.

      Before calling the 'step' method, you must first initialize the solver
      by running 'init_step'.

      :param t: Value of time.
      :type t: float
      :param method: Solve method for the current step. When 'normal' (default), output
                     is returned at time 't'. If 'onestep', output is returned after one
                     internal step toward 't'. Both methods stop at events, if given,
                     regardless of how 'eventsfn.terminal' was set.
      :type method: {'normal', 'onestep'}, optional
      :param tstop: Specifies a hard time constraint for which the solver should not
                    pass, regardless of the 'method'. The default is None.
      :type tstop: float, optional

      :returns: :class:`~sundae.ida.IDAResult` -- Custom output class for IDA solutions. Includes pretty-printing
                consistent with scipy outputs. See the class definition for more
                information.

      :raises ValueError: 'method' value is invalid. Must be 'normal' or 'onestep'.
      :raises ValueError: 'init_step' must be run prior to 'step'.

      .. rubric:: Notes

      In general, when solving step by step, times should all be provided in
      either increasing or decreasing order. The solver can output results at
      times taken in the opposite direction of integration if the requested
      time is within the last internal step interval; however, values outside
      this interval with raise errors. Rather than trying to mix forward and
      reverse directions, choose each sequential time step carefully so you
      get all of the values you need.

      When mixing the 'normal' and 'onestep' methods, consider using 'tstop'
      for all steps. Even though the solver may be returning the solution at
      time 't' for the 'normal' method, the internal state can pass this time
      during the step when 'tstop' is not provided. Therefore, the following
      time steps may throw errors if the internal state has surpassed a next
      requested 't' value in the direction of integration.



.. py:class:: IDAResult(**kwargs)



   Results class for IDA solver.

   Inherits from :class:`~sundae.common.RichResult`. The solution class
   groups output from :class:`IDA` into an object with the fields:

   :param message: Human-readable description of the status value.
   :type message: str
   :param success: True if the solver was successful (status >= 0). False otherwise.
   :type success: bool
   :param status: Reason for the algorithm termination. Negative values correspond
                  to errors, and positive values to different successful termination
                  criteria.
   :type status: int
   :param t: Solution time(s). The dimension depends on the method. Stepwise
             solutions will only have 1 value whereas solutions across a full
             'tspan' will have many.
   :type t: ndarray, shape(n,)
   :param y: State variable values at each solution time. Rows correspond to
             indices in 't' and columns match indexing from 'y0'.
   :type y: ndarray, shape(n, m)
   :param yp: State variable time derivate values at each solution time. Row
              and column indexing matches 'y'.
   :type yp: ndarray, shape(n, m)
   :param i_events: Provides an array for each detected event 'k' specifying indices
                    for which event(s) occurred. ``i_events[k,i] != 0`` if 'events[i]'
                    occurred at 't_events[k]'. The sign of 'i_events' indicates the
                    direction of zero-crossing:

                        * -1 indicates 'events[i]' was decreasing
                        * +1 indicates 'events[i]' was increasing

                    Output for 'i_events' will be None when either 'eventsfn' was None
                    or if no events occurred during the solve.
   :type i_events: ndarray, shape(k, num_events) or None
   :param t_events: Times at which events occurred or None if 'eventsfn' was None or
                    no events were triggered during the solve.
   :type t_events: ndarray, shape(k,) or None
   :param y_events: State variable values at each 't_events' value or None. Rows and
                    columns correspond to 't_events' and 'y0' indexing, respectively.
   :type y_events: ndarray, shape(k, m) or None
   :param yp_events: State variable time derivative values at each 't_events' value or
                     None. Row and column indexing matches 'y_events'.
   :type yp_events: ndarray, shape(k, m) or None
   :param nfev: Number of times that 'resfn' was evaluated.
   :type nfev: int
   :param njev: Number of times the Jacobian was evaluated, 'jacfn' or internal
                finite difference method.
   :type njev: int

   .. rubric:: Notes

   Terminal events are appended to the end of 't', 'y', and 'yp'. However,
   if an event was not terminal then it will only appear in '_events'
   outputs and not within the main output arrays.


