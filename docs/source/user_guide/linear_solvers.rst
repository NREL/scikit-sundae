Linear Solvers
==============
SUNDIALS (Suite of Nonlinear and Differential/Algebraic Equation Solvers) provides efficient linear solvers tailored for solving systems of equations arising in scientific computing. The two primary types of linear solvers available in SUNDIALS are ``direct`` and ``iterative`` solvers. These solvers cater to different problem structures, optimizing performance and computational efficiency.

Direct Solvers
--------------
Direct solvers are designed to compute the exact solution of a system of linear equations in a finite number of steps, typically by factorizing the Jacobian matrix. They are most effective for smaller to medium-sized systems or systems with dense matrices, where the computational cost of matrix factorization is not prohibitive. These solvers provide reliable, accurate solutions, but can be less efficient for large or sparse systems.

Dense Solvers 
^^^^^^^^^^^^^
Dense solvers are suitable for systems where the Jacobian matrix is fully populated with non-zero entries. While they can handle banded problems, they may be less efficient than banded solvers in cases where sparsity exists.

When to use:

* Opt for a dense solver when the Jacobian matrix does not exhibit a banded structure.
* Ideal for smaller systems where the overhead of manipulating the problem into a banded structure may outweigh the benefits.

Banded Solvers 
^^^^^^^^^^^^^^
Banded solvers are designed for systems where the Jacobian matrix is sparse and has non-zero entries concentrated around the diagonal. This structure is common in problems derived from finite difference methods or certain discretizations of partial differential equations.

When to use:

* Use a band solver when the Jacobian matrix has a banded structure.
* Beneficial for large systems. When possible, try to order your problem's systems of equations to `minimize the bandwidth`_.

.. _minimize the bandwidth: https://sciendo.com/article/10.2478/awutm-2014-0019

Sparse Solvers
^^^^^^^^^^^^^^
Sparse solvers are designed for systems where the Jacobian matrix contains a significant number of zero entries, allowing for more efficient storage and computation by only focusing on non-zero elements. These solvers are particularly useful when dealing with large, sparse systems where maintaining the full matrix would be computationally expensive.

When to use:

* Opt for a sparse solver when the Jacobian matrix is large and sparse, meaning most of its entries are zero.
* Ideal for large-scale systems, especially when the matrix has does not already have a structure that would be suitable for the baneded solver.
* Use sparse solvers to reduce memory usage and improve computational efficiency when the problem involves a sparse matrix.

Configuration in scikit-SUNDAE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Switching between SUNDIALS direct linear solvers in scikit-SUNDAE is straightforward. While initializing your solver, simply specify which linear solver to use. The ``dense`` linear solver is the default. Changing to a banded linear solver is the same in both the ``CVODE`` and ``IDA`` solvers as demonstrated below:

.. code-block:: python 

    from sksundae.ida import IDA
    from sksundae.cvode import CVODE 

    # IDA with a dummy residuals function
    def resfn(t, y, yp, res):
        pass

    L = 0  # lower bandwidth
    U = 0  # upper bandwidth

    solver = IDA(resfn, linsolver='band', lband=L, uband=U)

    # COVDE with a dummy right-hand-side function
    def rhsfn(t, y, yp):
        pass 

    L = 0  # lower bandwidth
    U = 0  # upper bandwidth
    solver = CVODE(rhsfn, linsolver='band', lband=L, uband=U)

Ensure you provide both the lower bandwidth ``lband`` and upper bandwidth ``uband`` when using the ``band`` linear solver. Each bandwidth defines the LARGEST distance between a non-zero element and the main diagonal, on either side, as shown in the figure below. Forgetting to set either bandwidth will raise an error. If ``lband + uband`` matches the dimension ``N`` of the matrix, the performance of the ``band`` and ``dense`` linear solvers will be approximately the same.

.. figure:: figures/banded_jacobian.png 
   :width: 50% 
   :alt: Banded Jacobian example.
   :align: center
    
In the limiting case where the Jacobian is only non-zero along the main diagonal, both bandwidths can be zero. However, it is unlikely that you will be able to find many, if any, problems that fit this exact form. Alternatively, you can activate the ``sparse`` linear solver by is that is a better fit for your problem. When ``sparse`` is chosen, you must also provide the option ``sparsity`` which provides a sparsity pattern to the solver so it knows how much memory to allocate for the Jacobian, and which indices to track according to the non-zero entries. There are helper functions in the ``jacband`` module that can help you determine the sparsity pattern so you do not always need to construct it manually. See the examples below which demonstrate activating the ``sparse`` linear solver.

.. code-block:: python 

    from sksundae.ida import IDA
    from sksundae.cvode import CVODE 

    # IDA with a dummy residuals function
    def resfn(t, y, yp, res):
        pass

    sparsity = ...  # sparse matrix or 2D array w/ Jacobian sparsity pattern
    solver = IDA(resfn, linsolver='sparse', sparisty=sparsity)

    # COVDE with a dummy right-hand-side function
    def rhsfn(t, y, yp):
        pass 

    sparsity = ...  # sparse matrix or 2D array w/ Jacobian sparsity pattern
    solver = CVODE(rhsfn, linsolver='sparse', sparisty=sparsity)

Iterative Solvers
-----------------
Iterative solvers approximate a linear system's solution by iteratively refining an initial guess. They are particularly well-suited for large, sparse systems where direct solvers would be too computationally expensive. These solvers are often more memory-efficient and faster for large problems, though they may require preconditioners or appropriate convergence criteria to ensure robustness and efficiency. However, at the moment preconditioning options are not implemented into scikit-SUNDAE. Consequently, if you use a linear solver for a poorly conditioned system you will likely run into stability issues and the solver will fail. Preconditioning interfaces will likely be added in a future release, but implementing a preconditioner is a non-trivial exercise and is generally problem specific. It will be left to the user to define their own preconditioners when available as SUNDIALS has limited general preconditioning modules available, and some require parallel vector interfaces which are not planned to ever be included in scikit-SUNDAE.

To activate an iterative solver use the ``linsolver`` option with one of the following strings: ``gmres``, ``bicgstab``, or ``tfqmr``. There solvers are for the general minimal residual, bicongugate gradient stabilized, and transpose-free quasi-minimum residual algorithms. Note that each of these iterative methods are considered "matrix free" and do not interface with any Jacobian options. Therefore, you will get an error if you attempt to use a Jacobian routine either by passing ``sparsity`` or ``jacfn``.

Performance Considerations
--------------------------
Choosing between the direct solvers depends primarily on the structure of your Jacobian matrix. Banded and sparse solvers can significantly reduce memory usage and improve computational speed for large systems, while dense solvers may be more straightforward for smaller, fully populated matrices.

In any case, the default algorithm will numerically approximate the Jacobian for you. However, the ``dense`` routine requires ``N`` function evaluations to approximate the derivative whereas the ``band`` and ``sparse`` options can require significantly fewere, depending on the bandwidth or sparsity pattern, respectively. Note that the Jacobian approximation routine for the ``sparse`` solver is a custom implementation written by scikit-SUNDAE developers. It is not a base routine that comes with SUNDIALS. Consequently, its performance may be less consistent than the difference quotient routines implemented for the ``dense`` and ``band`` solvers. However, for any direct solver you can further improve the performance of either by explicitly providing the Jacobian, as we cover :doc:`here <explicit_jacobians>`.

Iterative solvers offer significant performance advantages for large, sparse systems by avoiding direct factorization of the Jacobian. Instead, they iteratively refine the solution, reducing both memory usage and computational cost compared to direct solvers. However, their efficiency and stability depends on factors such as the conditioning of the system, the choice of preconditioners, and the convergence tolerance.

Unlike direct solvers, iterative methods may require careful tuning to achieve optimal performance. While they can be highly effective for large-scale problems, poor preconditioning or ill-conditioned systems can lead to slow convergence or even divergence. Providing a well-constructed preconditioner can drastically improve both speed and stability; however, an interface to user-defined preconditioners is not yet available in scikit-SUNDAE.

Further Reading
---------------
For more detailed information on the linear solvers and their implementation, please refer to the `SUNDIALS documentation`_. However, be aware that their full documentation covers more solvers than are implemented in scikit-SUNDAE. 

.. _SUNDIALS documentation: https://sundials.readthedocs.io/en/latest/sunlinsol/index.html
