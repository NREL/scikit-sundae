User Guide 
==========
Welcome to the scikit-SUNDAE user guide, your comprehensive resource for getting started with and mastering the use of the scikit-SUNDAE package. Whether you're a beginner looking to learn the basics of numerical integration with SUNDIALS or an experienced user seeking advanced features, this guide provides a structured path to help you navigate through the package's capabilities. Here, you'll find detailed explanations of scikit-SUNDAE's core features, installation instructions, and guidance on solving typical problems using the package.

In this guide, you'll also learn about the numerical solvers wrapped by scikit-SUNDAE, including the popular CVODE and IDA solvers, which are used to solve initial value problems for ordinary differential equations (ODEs) and differential-algebraic equations (DAEs), respectively.

This guide offers a basic tutorial to help you get started. You'll also find descriptions of the solver configurations and the various options for customizing their behavior to suit your specific use case. For more technical users, detailed documentation on the linear solvers, event functions, and Jacobians will ensure you can fully utilize the flexibility of the package in complex workflows.

Each section is designed to give you the information you need in a straightforward and
accessible format. Look through and explore each page to get the most out of scikit-SUNDAE and start integrating powerful numerical solvers into your Python projects.

.. toctree::
   :hidden: 
   :caption: Getting Started

   what_is_sksundae.rst
   installation.rst

.. toctree::
   :hidden:
   :caption: Fundamentals and Usage

   ivp_overview.rst
   ode_overview.rst
   dae_overview.rst

.. toctree::
   :hidden:
   :caption: Advanced Usage

   linear_solvers.rst
   event_functions.rst
   explicit_jacobians.rst 
