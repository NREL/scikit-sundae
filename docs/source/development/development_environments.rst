Development Environments
========================
This guide will walk you through setting up a local development environment for contributing to scikit-SUNDAE. It covers recommended practices, tools, and commands for developers to efficiently build, test, and contribute to the project.

.. note:: 

    We assume developers are already at least a little familiar with using git and GitHub. If this is not the case for you, there are many online tutorials to help you `learn git <https://www.w3schools.com/git/default.asp?remote=github>`_.

1. Fork and clone the repository
    Before setting up your local environment, make sure you have forked the main repository and cloned it from your own fork. This allows you to create pull requests from your fork to the main repo.

2. Create a virtual environment
    Since we build scikit-SUNDAE agasint SUNDIALS releases on conda-forge, you will need to set up a virtual environment with ``conda`` access. While there are a few options you can use, we recommend using `Anaconda <https://anaconda.org>`_. With Anaconda installed, open the terminal (MacOS/Linux) or Anaconda Prompt and run::

        conda install python=x.x sundials=x.x -c conda-forge

    The ``x.x`` version numbers should be filled in with the latest stable releases of Python and SUNDIALS. Continuous Integration (CI) workflows automatically test older versions. On occasion, if issues arise during tests, you may need to work with older Python versions temporarily.

3. Set the ``SUNDIALS_PREFIX`` environment variable
    Scikit-SUNDAE expects your SUNDIALS installation to be in either ``$CONDA_PREFIX`` or ``%CONDA_PREFIX%\Library``. Check to see if your installation is in either of these directories. If it isn't, you will need to set the ``SUNDIALS_PREFIX`` environment variable::

        set SUNDIALS_PREFIX="..."         (on Windows)
        export SUNDIALS_PREFIX="..."      (on MacOS or Linux)

    If you used Anaconda to setup your environment you can likely skip this step, but it is good practice to double check that SUNDIALS was installed in one of the expected directories.

3. Install scikit-SUNDAE in editable mode
    Once you have your virtual environment activated and the files locally available, install scikit-SUNDAE in editable mode, including the necessary development tools and dependencies, like so::

        pip install -e .[dev]

    * Make sure you are in the same folder as the ``pyproject.toml`` file when you run this command.
    * The ``-e`` flag ensures that any changes to local Python files will be immediately available without reinstalling. However, modifying Cython files (``.pyx`` or ``.pxd``) will require rebuilding, as covered in the :doc:`version_control` section.
    * The ``[dev]`` argument installs all developer dependencies: linters, spellcheckers, testing tools, and more.

4. Running tests 
    We recommend testing your installation before you start making changes. To run unit tests and make a coverage report, we have integrated ``nox``::

        nox -s tests 

    This will run all tests and generate coverage reports. You can see the coverage report by opening the ``index.html`` file in the ``reports/htmlcov/`` folder once the tests are finished.

5. Linting, formatting, and spellchecking
    All linting, formatting, and spellchecking tasks are automated. To run these checks locally::

        nox -s linter [-- format]
        nox -s codespell [-- write]
    
    The optional ``format`` and ``write`` arguments will attempt to format the code and correct misspellings, respectively. For more information on linting and code style, make sure you reference the :doc:`code_style_and_linting` section.

6. Building documentation
    We use `sphinx <https://www.sphinx-doc.org/en/master/>`_ to build documentation by scraping docstrings. Before you start modifying the code base, make sure the documentation builds locally::

        nox -s docs 

    You can see the local documentation build in your browser by opening the ``index.html`` file from the ``docs/build/`` folder, after running the command above.

Now that you're all setup with a development version of scikit-SUNDAE and have tested the codebase using the ``nox`` integration, be sure to follow the :doc:`version_control` workflow as you contribute. Happy coding!
