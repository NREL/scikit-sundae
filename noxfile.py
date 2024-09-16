# noxfile.py

import os
import shutil

import nox


@nox.session(name='cleanup', python=False)
def run_cleanup(_):
    """Use os/shutil to remove some files/directories"""

    if os.path.exists('.coverage'):
        os.remove('.coverage')

    folders = ['.pytest_cache', '__pycache__']
    for f in folders:
        if os.path.exists(f):
            shutil.rmtree(f)


@nox.session(name='linter', python=False)
def run_flake8(session):
    """
    Run flake8 with the github config file

    Use the optional 'format' argument to run autopep8 on the src and tests
    directories prior to running the linter.

    """

    if 'format' in session.posargs:
        session.run('autopep8', '--in-place', '--recursive', '.')

    session.run('flake8', '--config=.github/linters/.flake8')


@nox.session(name='codespell', python=False)
def run_codespell(session):
    """
    Run codespell with the github config file

    Use the optional 'write' argument to write the corrections directly into
    the files. Otherwise, you will only see a summary of the found errors.

    """

    command = ['codespell', '--config=.github/linters/.codespellrc']

    if 'write' in session.posargs:
        command.insert(1, '-w')

    session.run(*command)


@nox.session(name='spellcheck', python=False)
def run_spellcheck(session):
    """
    Run codespell with some docs files indcluded

    Use the optional 'write' argument to write the corrections directly into
    the files. Otherwise, you will only see a summary of the found errors.

    """

    command = ['codespell']

    if 'write' in session.posargs:
        command.append('-w')

    run_codespell(session)

    session.run(*command, 'docs/index.html')
    session.run(*command, 'docs/source/examples')


@nox.session(name='tests', python=False)
def run_pytest(session):
    """
    Run pytest and generate test/coverage reports

    Use the optional 'parallel' argument to run the tests in parallel. As just
    a flag, the number of workers will be determined automatically. Otherwise
    you can specify the number of workers as an int.

    """

    command = [
        'pytest',
        '--cov=src/sksundae',
        '--cov-report=html:reports/htmlcov',
        '--cov-report=xml:reports/coverage.xml',
        '--junitxml=reports/junit.xml',
        'tests/',
    ]

    for arg in session.posargs:
        if arg.startswith('parallel='):
            command[1:1] = ['-n', arg.split('=')[-1]]
        elif arg.startswith('parallel'):
            command[1:1] = ['-n', 'auto']

    session.run(*command)

    run_cleanup(session)


@nox.session(name='badges', python=False)
def run_genbadge(session):
    """Run genbadge to make test/coverage badges"""

    session.run(
        'genbadge', 'coverage', '-l',
        '-i', 'reports/coverage.xml',
        '-o', 'images/coverage.svg',
    )

    session.run(
        'genbadge', 'tests', '-l',
        '-i', 'reports/junit.xml',
        '-o', 'images/tests.svg',
    )


@nox.session(name='docs', python=False)
def run_sphinx(session):
    """Run spellcheck and then use sphinx to build docs"""

    if 'clean' in session.posargs:
        os.chdir('docs')
        session.run('make', 'clean')

        if os.path.exists('source/api'):
            shutil.rmtree('source/api')

        os.chdir('..')

    run_spellcheck(session)

    session.run('sphinx-build', 'docs/source', 'docs/build')


@nox.session(name='pre-commit', python=False)
def run_pre_commit(session):
    """
    Run all linters/tests and make new badges

    Order of sessions: flake8, codespell, pytest, genbade. Using 'write' for
    codespell and/or 'parallel' for pytest is permitted.

    """

    run_flake8(session)
    run_codespell(session)

    run_pytest(session)
    run_genbadge(session)
    

@nox.session(name='rebuild', python=False)
def run_build_ext(session):
    """
    Runs setup.py build_ext --inplace
    
    Use this to rebuild your editable package when the Cython files change.
    This removes for a full reinstallation. Note, this only works if your
    original install was done in editable mode. Editable mode already takes
    care of keeping modified python files synced, so only rebuild when the
    extension files (.pyx, .pxd) are modified.
        
    """
    
    session.run('python', 'setup.py', 'build_ext', '--inplace')
