Examples
========
Examples below provide a collection of practical demonstrations to help you get started with scikit-SUNDAE. These examples showcase how to solve various initial value problems (IVPs) using both the CVODE and IDA solvers for ordinary differential equations (ODEs) and differential algebraic equations (DAEs), respectively. Each example is designed to guide you through the process of setting up a solver, defining your system of equations, and customizing solver options such as event tracking or explicit Jacobians.

Whether you're new to numerical integration or already familiar with SUNDIALS, these examples will illustrate how to effectively apply scikit-SUNDAE to your own problems. From simple ODEs to more complex DAE systems, you'll see how to leverage the speed and flexibility of the package while working entirely within Python.

.. grid:: 1 2 2 2

   .. grid-item-card:: ODE Problems
         :class-footer: border-0
         :padding: 2
           
         Learn how to solve ordinary differential equations
         (ODEs) with CVODE.

         .. toctree::
            :caption: ODE Problems
            :numbered:
            :titlesonly:

            van_der_pol.ipynb

   .. grid-item-card:: DAE Problems
         :class-footer: border-0
         :padding: 2
           
         Explore solving differential algebraic equations
         (DAEs) using IDA.

         .. toctree::
            :caption: DAE Problems
            :numbered:
            :titlesonly:

            robertson.ipynb
