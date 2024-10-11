Initial Value Problems
======================
Initial value problems (IVPs) arise when solving differential equations where the solution is determined by integrating over time from an initial state. These problems are common in modeling physical systems, biology, engineering, and more.

What is an IVP?
---------------
An IVP consists of a differential equation along with an initial condition. In general, it takes the form:

.. math:: 

    \frac{dy}{dt} = f(t, y), \quad y(t_0) = y_0,

where:

* :math:`y(t)` is the time-dependent unknown state
* :math:`f(t, y)` is the function that describes how the state changes over time
* :math:`y_0` is the known initial state at :math:`t_0`

Common Applications
^^^^^^^^^^^^^^^^^^^
* **Physics:** Modeling the motion of particles, population dynamics
* **Engineering:** Control systems, heat transfer models
* **Biology:** Disease spread models, ecosystem modeling

Example of an IVP
^^^^^^^^^^^^^^^^^
Consider a simple linear system:

.. math:: 

    \frac{dy}{dt} = -ky, \quad y(0) = 1.

Here, :math:`y_0 = 1` is the initial condition, and the rate of change is proportional to the current state :math:`y`, controlled by the constant :math:`k`. While :math:`y` is a scalar here, initial value problems can also involve multi-dimensional states. Imagine :math:`y` as an array. In this case, the problem requires time derivative expressions and initial conditions for each element in :math:`y`. The solution procedure, however, is not significantly different.

Numerical Methods for IVPs
--------------------------
In most practical situations, the exact solution of an IVP is not available, and numerical methods are required to approximate the solution over a time interval. Some of the most common methods include:

1. Euler's Method 
    One of the simplest methods, Euler's method estimates the solution at the next time step :math:`t_{n+1}` using:

    .. math::

        y_{n+1} = y_n + h \cdot f(t_n, y_n),

    where :math:`h` is the step size. While easy to implement, Euler's method is not very accurate for stiff or complex problems.

2. Runge-Kutta Methods
    Runge-Kutta methods (particularly the 4th-order method) are widely used for IVPs because of their balance between accuracy and computational cost. The 4th-order Runge-Kutta method updates the solution with intermediate evaluations of :math:`f(t, y)`:

    .. math::

        y_{n+1} = y_n + \frac{h}{6}(k_1 + 2k_2 + 2K_3 + k_4),

    where:

    * :math:`k_1 = f(t_n, y_n)`
    * :math:`k_2 = f(t_n + h/2, y_n + hk_1/2)`
    * :math:`k_3 = f(t_n + h/2, y_n + hk_2/2)`
    * :math:`k_4 = f(t_n + h, y_n + hk_3)`

3. Backward Differentiation Formulas (BDF)
    Backward differentiation formulas are implicit methods used for stiff problems, where explicit methods (like Euler or Runge-Kutta) may be inefficient or unstable. BDF methods solve a system of equations at each step, making them more computationally demanding but highly effective for stiff systems.

    **Stiff vs. Non-Stiff Problems**
        - Stiff problems have states that change at significantly different time scales. For example, a reaction that starts off slow and then becomes near instantaneous. These problems benefit from implicit methods like BDF.
        - Non-Stiff problems are stable and efficiently solved with standard methods (e.g., Euler or Runge-Kutta).

SUNDIALS Solvers for IVPs
-------------------------
SUNDIALS implements three major solvers for IVPs:

1. CVODE
    - Type: Solves Ordinary Differential Equations (ODEs)
    - Methods: Includes both Adams-Moulton (explicit) and BDF (implicit) methods
    - Usage: Best suited for non-stiff and stiff ODE problems

2. ARKODE (Not implemented in scikit-SUNDAE)
    - Type: Solves Ordinary Differential Equations (ODEs)
    - Methods: Explicit Runge-Kutta methods for non-stiff problems and Implicit-Explicit (IMEX) Runge-Kutta methods for stiff problems
    - Usage: For systems that contain both stiff and non-stiff components

3. IDA 
    - Type: Solves Differential-Algebraic Equations (DAEs)
    - Methods: Uses Backward Differentiation Formulas (BDF) for implicit integration
    - Usage: Designed for stiff problems with both differential and algebraic components

Conclusion
----------
Initial value problems form the foundation of many mathematical models. While analytical solutions are rare, numerical methods like Runge-Kutta and BDF enable accurate approximations of IVPs. Choosing the right method depends on the problem's stiffness and required precision. For stiff problems, implicit methods like those implemented in SUNDIALS solvers are essential.
