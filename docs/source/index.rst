.. .. raw:: html

..    <embed>
..       </br>
..       <img alt='logo' class='onlight bg-transparent' src='_static/light_tag.png'
..        style='width: 75%; min-width: 250px; max-width: 500px;'>
..       <img alt='logo' class='ondark bg-transparent' src='_static/dark_tag.png'
..        style='width: 75%; min-width: 250px; max-width: 500px;'>
..       </br>
..    </embed>

=======
Summary
=======
scikit-SUNDAE provides Python bindings to `SUNDIALS`_ integrators. The implicit
differential algebraic (IDA) solver and C-based variable-coefficient ordinary
differential equations (CVODE) solver are both included.

The name SUNDAE combines (SUN)DIALS and DAE, which stands for differential
algebraic equations. Solvers specific to DAE problems are not frequently
available in Python. An ordinary differential equation (ODE) solver is also
included for completeness. ODEs can be categorized as a subset of DAEs (i.e.,
DAEs with no algebraic constraints).

.. _SUNDIALS: https://sundials.readthedocs.io/en/latest/

.. toctree:: 
   :caption: User Guide
   :hidden:
   :maxdepth: 2

   User Guide <user_guide/index>

.. toctree:: 
   :caption: API Reference
   :hidden:
   :maxdepth: 2

   API Reference <api/sksundae/index>

.. toctree:: 
   :caption: Examples
   :hidden:
   :maxdepth: 2

   Examples <examples/index>

.. toctree:: 
   :caption: Development
   :hidden:
   :maxdepth: 2

   Development <development/index>

**Version:** |version|

**Useful links:** 
`SUNDIALS <https://sundials.readthedocs.io/en/latest/>`_ |
`conda-forge/sundials <https://anaconda.org/conda-forge/sundials>`_ | 
`anaconda <https://www.anaconda.com/download>`_ |
`numpy <https://numpy.org/doc/stable>`_ |
`scipy <https://docs.scipy.org/doc/scipy>`_ 

.. grid:: 1 2 2 2

   .. grid-item-card:: User Guide
         :class-footer: border-0
         :padding: 2

         Access installation instructions and in-depth
         information on solver concepts and settings.

         .. image:: _static/user_guide.svg
            :class: bg-transparent
            :align: center
            :height: 75px

         +++
         .. button-ref:: user_guide/index
            :expand:
            :color: primary
            :click-parent:

            To the user guide

   .. grid-item-card:: API Reference
      :class-footer: border-0
      :padding: 2

      Get detailed documentation on all of the modules,
      functions, classes, etc.

      .. image:: _static/api_reference.svg
         :class: bg-transparent
         :align: center
         :height: 75px

      +++
      .. button-ref:: api/sksundae/index
         :expand:
         :color: primary
         :click-parent:

         Go to the docs

   .. grid-item-card:: Examples
         :class-footer: border-0
         :padding: 2
           
         A great place to learn how to use the package and
         expand your skills.

         .. image:: _static/examples.svg
            :class: bg-transparent
            :align: center
            :height: 75px

         +++
         .. button-ref:: examples/index
            :expand:
            :color: primary
            :click-parent:

            See some examples

   .. grid-item-card:: Development
      :class-footer: border-0
      :padding: 2
         
      Trying to fix a typo in the documentation? Looking
      to improve or add a new feature?

      .. image:: _static/development.svg
         :class: bg-transparent
         :align: center
         :height: 75px

      +++
      .. button-ref:: development/index
         :expand:
         :color: primary
         :click-parent:

         Read contributor guidelines
            