Ordinary Differential Equations
===============================
An Ordinary Differential Equation (ODE) is an equation that involves functions of a single variable and their derivatives. ODEs represent relationships between the rates of change of a quantity and the quantity itself. They are used extensively to model dynamic systems, where a change in one variable affects the entire system over time.

For example, in physics, the motion of an object under the influence of forces like gravity can be modeled by an ODE that links the acceleration of the object to its velocity and position.

What is an ODE?
---------------
In contrast to partial differential equations (PDEs), discussed below, ODEs relate a function with a single independent variable to the function itself, and its derivatives. In what follows, :math:`y = f(x)` is an unknown function that only depends on the independent variable :math:`x`. The general form of an :math:`n^{\rm th}` order ODE is,

.. math:: 

    F(y, y', ..., y^n) = G(x),

where :math:`y^n` is the :math:`n^{\rm th}` derivative of :math:`y` and the right hand side :math:`G(x)` includes all terms without :math:`y` or its derivatives. In some cases, :math:`G(x)` may be a simple constant, including zero, as discussed in the :ref:`Classification` section below.
    
ODEs are widely used to describe processes that evolve over time in various scientific and engineering fields. Examples include:

* **Physics:** Modeling the motion of objects (Newton's laws of motion)
* **Biology:** Population dynamics in ecology, such as predator-prey models
* **Engineering:** Electrical circuits governed by voltage and current relationships
* **Economics:** Modeling investment growth or decay over time (interest rate models)

In general, whenever a system's future state depends on its current state and rate of change, an ODE can be used to describe that system.

.. _Classification:

Classification
^^^^^^^^^^^^^^
ODEs are classified based on several characteristics that describe the nature of the equation and the problem being solved. Below are common criteria used for classification:

1. Order 
    The order of an ODE is determined by the highest derivative present in the equation. For example:

    - A first-order ODE involves only the first derivative, :math:`dy/dx = -ky`.
    - A second-oder derivative involves the second derivative, :math:`d^2y/dx^2 + k^2y = 0`.

2. Linear vs. Nonlinear
    A differential equation is linear if :math:`F`, from above, can be written as a linear combination of :math:`y` and its derivatives

    .. math:: 

        F(y, y', ..., y^n) = \sum_{i=0}^n a_i(x)y^{i},

    where the :math:`a_i(x)` terms can be any continuous function of :math:`x`, including nonlinear functions. ODEs are classified as nonlinear when there exist any terms where :math:`y` and/or its derivatives have nonlinear operations applied. For example,

    - :math:`dy/dx - ky^2 = G(x)`
    - :math:`d^2y/dx^2 \times dy/dx \times y = G(x)`
    - :math:`dy/dx + \exp(y) = G(x)` 

3. Homogeneous vs. Nonhomogeneous 
    A homogeneous ODE has :math:`G(x) = 0`. In contrast, for any ODEs where :math:`G(x) \ne 0`, the ODE is considered nonhomogeneous. Nonzero :math:`G(x)` typically represent external influence or forcing terms.

Initial Value vs. Boundary Value Problems
-----------------------------------------
While ODEs can take many forms, not all ODEs will be well suited for the solvers in scikit-SUNDAE. Below we discuss two main ODE problem types.

1. Initial Value Problems (IVPs)
    An initial value problem is an ODE where the solution is determined by the value of the function at a single starting point. In IVPs, the initial state :math:`y(t_0)` is known, and the goal is to evaluate the function :math:`y(t)` at later times. A simple one-varible example might look like

    .. math::

        \frac{dy}{dt} = -2y, \quad y(0) = 1.

    In this case, the initial value :math:`y(0) = 1` is provided, and the solution describes how :math:`y(t)` evolves from this starting point.

2. Boundary Value Problems (BVPs)
    A boundary value problem is an ODE where the solution is determined by conditions physical boundaries. Instead of knowing the initial state, boundary conditions at multiple points are specified. The number of boundary conditions must match the order of the ODE. For example,

    .. math::

        \frac{d^2y}{dx^2} = -y, \quad y(0) = 0, \quad y(\pi) = 0.

    In the second-order BVP above, the solution must satisfy the specified boundary conditions at both :math:`x = 0` and :math:`x = \pi`.

The CVODE solver in scikit-SUNDAE is well suited for IVPs. It can solve both ODEs and discretized PDEs, when problems have more than one dependent variable (e.g., time and space).

Intro to CVODE
--------------
The CVODE solver is part of the SUNDIALS suite and is designed for solving stiff and nonstiff initial value problem ODEs. It implements both an Adams-Moulton method for nonstiff problems and a backward differentiation formula (BDF) method for stiff problems. This flexibility makes it well-suited for a wide variety of ODEs, including systems with rapidly changing or slow-moving dynamics.

CVODE is capable of solving ODEs across all classifications discussed above. However, CVODE is designed specifically to handle ODE systems that are cast as first-order. This makes it essential for users to reformulate higher-order ODEs into equivalent first-order systems. CVODE is also primarily intended for Initial Value Problems (IVPs), but it can sometimes be adapted for Boundary Value Problems (BVPs) by repeatedly solving IVPs until a steady state is reached. This approach is particularly useful when direct BVP solvers are impractical, such as when it's difficult to provide a good guess for the solution.

Stiff vs. Nonstiff ODEs
^^^^^^^^^^^^^^^^^^^^^^^
* Stiff ODEs occur when there are rapid changes in some components of the system, requiring a more stable integration method like BDF. For example, chemical reactions involving vastly different timescales tend to be stiff.
* Nonstiff ODEs, such as those encountered in simple population growth models, are more straightforward to solve and are handled efficiently by methods like Adams-Moulton.

CVODE is particularly effective for stiff systems but performs well for nonstiff systems as well.

Refactoring High-Order ODEs
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Many numerical solvers, including CVODE, solve first-order ODE systems. Higher-order ODEs can be refactored into first-order systems using variable substitutions. For example, the second-order equation 

.. math:: 

    \frac{d^2y}{dt^2} = f(t, y, y^{\prime})

can be rewritten as two first-order equations:

.. math:: 

    \frac{dy_1}{dt} = y_2, \quad \frac{dy_2}{dt} = f(t, y_1, y_2).

This reformulation allows CVODE to handle higher-order ODEs by transforming them into an equivalent first-order system. While we do not provide a thorough example here, this concept is covered extensively online. Most differential equations textbooks cover this topic. For interested parties, we refer you to the open-access textbook `Advanced Engineering Mathematics and Analysis`_. You will find detailed discussions and examples in chapter 7.

.. _Advanced Engineering Mathematics and Analysis: https://osf.io/hstxz/

CVODE for PDEs
--------------
Partial Differential Equations (PDEs) are used to model systems where changes occur in more than one dimension, such as heat flow or fluid dynamics. Unlike ODEs, PDEs involve partial derivatives with respect to multiple variables.

Discretizing PDEs into ODEs
^^^^^^^^^^^^^^^^^^^^^^^^^^^
CVODE is also capable of solving PDEs. However, as we discussed above, users may need to refactor problems to make them suitable for CVODE. In the case of PDEs, they should be discretized and reduced into a system of ODEs. This process transforms the continuous equation into a system of algebraic equations that CVODE can handle. For example, the 1D heat equation:

.. math:: 

    \frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2},
 
can be discretized using finite difference methods, resulting in a system of ODEs that CVODE or another solver can handle. For example, discretizing the :math:`x` dimension into :math:`N` discrete volumes, each with its own temperature :math:`T_i` where :math:`i \in [1,N]`, results in equations like 

.. math:: 

    \frac{dT_i}{dt} = \alpha \frac{T_{i+1} - 2T_i + T_{i-1}}{\Delta x^2}.

This specific discretization uses a second-order central differencing scheme and a uniform "mesh", i.e., each discrete control volume is the same size and the distance from any two adjanced centers is always :math:`\Delta x`. There are also  one-sided methods, lower-order methods, and higher-order methods. We leave it to the user to review these concepts and choose strategies that best suite their problems. 

In short, given a PDE, you will want to discretize any spatial dimensions. The number of discretizations will determine how many equations you need to write out for CVODE. Ensure that equations for boundary volumes (i.e., the volumes at the edges of your discretized domain) enforce boundary conditions using modified expressions. For example, if the boundary conditions in our heat equation example are adiabatic at :math:`x=0` and convective at :math:`x=L`, the expressions for :math:`T_1` and :math:`T_N` might look something like:

.. math:: 

    \frac{dT_1}{dt} = \alpha \frac{T_2 - T_1}{\Delta x},

.. math::
    
    \frac{dT_N}{dt} = \alpha \bigg(\frac{T_N - T_{i-1}}{\delta x} - hA(T_{\infty} - T_N)\bigg),

where :math:`h`, :math:`A`, and :math:`T_{\infty}` are the convective heat transfer coefficient, area, and environment temperature. For this problem, all other expressions for :math:`T_2` to :math:`T_{N-1}` would be of the general form given above.

Summary
-------
On this page, we introduced the concept of Ordinary Differential Equations (ODEs), discussing their role in modeling real-world systems and classifying them by order, linearity, and problem type. We then explored the CVODE solver, highlighting its suitability for both stiff and nonstiff problems, and how higher-order ODEs can be refactored into first-order systems for easier numerical solution. Finally, we touched on how Partial Differential Equations (PDEs) can be discretized into systems of ODEs so they can be solved with solvers like CVODE.
