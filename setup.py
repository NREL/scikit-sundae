# setup.py

import os
import re
import setuptools
from warnings import warn

import numpy
from Cython.Build import cythonize


def find_sundials():
    search_paths = []

    SUNDIALS_PREFIX = os.environ.get('SUNDIALS_PREFIX')
    if SUNDIALS_PREFIX:
        search_paths.append(SUNDIALS_PREFIX)

    CONDA_PREFIX = os.environ.get('CONDA_PREFIX')
    if CONDA_PREFIX:
        search_paths.extend([
            CONDA_PREFIX,
            os.path.join(CONDA_PREFIX, 'Library'),
        ])

    search_paths.extend([
        '/usr',
        '/usr/local',
        'C:/SUNDIALS',
        'C:/Program Files/SUNDIALS',
    ])

    for BASE in search_paths:
        include_dir = os.path.join(BASE, 'include')
        CONFIG_H = os.path.join(include_dir, 'sundials', 'sundials_config.h')
        if os.path.exists(CONFIG_H):
            return BASE, CONFIG_H

    raise FileNotFoundError("Can't find SUNDIALS installation in any of the"
                            f" {search_paths=}. Set the environment variable"
                            " SUNDIALS_PREFIX to the parent directory of the"
                            " 'include' and 'lib' directories and retry the"
                            " installation.")


def parse_config_h(file):

    config = {}
    define_rx = re.compile(r"#define\s+(\w+)(?:\s+(.*))?")

    for line in file:

        line = line.strip()
        if define_rx.match(line):

            name, value = define_rx.match(line).group(1, 2)
            if isinstance(value, str):
                value = value.strip('"')

            try:
                config[name] = int(value)
            except (ValueError, TypeError):  # Catch non int and NoneType
                config[name] = value

    return {k: config[k] for k in sorted(config)}


def get_extensions():

    # Parse sundials_config.h
    BASE, CONFIG_H = find_sundials()
    with open(CONFIG_H, 'r') as f:
        config = parse_config_h(f)

    # Write pxi files for C and Python to match types to sundials_config.h
    SUNDIALS_VERSION = config.get('SUNDIALS_VERSION')
    MAJOR_VERSION = SUNDIALS_VERSION.split('.')[0]
    if int(MAJOR_VERSION) < 7:
        raise RuntimeError(f"sksundae - incompatible {SUNDIALS_VERSION=}."
                           " MAJOR_VERSION must be at least 7.")

    if config.get('SUNDIALS_SINGLE_PRECISION'):
        precision = 'float'
        np_precision = 'np.float32_t'
    elif config.get('SUNDIALS_DOUBLE_PRECISION'):
        precision = 'double'
        np_precision = 'np.float64_t'
    elif config.get('SUNDIALS_EXTENDED_PRECISION'):
        precision = 'long double'
        np_precision = 'np.float128_t'
    else:
        warn("Couldn't find SUNDIALS_PRECISION. Defaulting to double.")
        precision = 'double'
        np_precision = 'np.float64_t'

    if config.get('SUNDIALS_INT32_T'):
        indexsize = 'int'
        np_indexsize = 'np.int32_t'
    elif config.get('SUNDIALS_INT64_T'):
        indexsize = 'long int'
        np_indexsize = 'np.int64_t'
    else:
        warn("Couldn't find SUNDIALS_INDEX_SIZE. Defaulting to int.")
        indexsize = 'int'
        np_indexsize = 'np.int32_t'

    with open('src/sksundae/py_config.pxi', 'w') as f:  # Python config
        f.write(f"SUNDIALS_VERSION = \"{SUNDIALS_VERSION}\"\n")
        f.write(f"SUNDIALS_FLOAT_TYPE = \"{precision}\"\n")
        f.write(f"SUNDIALS_INT_TYPE = \"{indexsize}\"\n")

    with open('src/sksundae/c_config.pxi', 'w') as f:  # C config
        f.write("cimport numpy as np\n\n")

        f.write(f"ctypedef {precision} sunrealtype\n")
        f.write(f"ctypedef {np_precision} DTYPE_t\n\n")

        f.write(f"ctypedef {indexsize} sunindextype\n")
        f.write(f"ctypedef {np_indexsize} INT_TYPE_t\n")

    # Specify include_dirs, library_dirs, and libraries for each extension
    SUNDIALS_INCLUDE_DIRS = [numpy.get_include(), os.path.join(BASE, 'include')]
    SUNDIALS_LIBRARY_DIRS = [os.path.join(BASE, 'lib')]

    LIBRARIES = [
        'sundials_core',
        'sundials_nvecserial',
        'sundials_sunlinsoldense',
        'sundials_sunlinsolband',
        'sundials_sunmatrixdense',
        'sundials_sunmatrixband',
    ]

    # Define the extension modules
    extensions = [
        setuptools.Extension(
            name='sksundae._cy_common',
            sources=['src/sksundae/_cy_common.pyx'],
            include_dirs=SUNDIALS_INCLUDE_DIRS,
            library_dirs=SUNDIALS_LIBRARY_DIRS,
            libraries=LIBRARIES,
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        ),
        setuptools.Extension(
            name='sksundae._cy_cvode',
            sources=['src/sksundae/_cy_cvode.pyx'],
            include_dirs=SUNDIALS_INCLUDE_DIRS,
            library_dirs=SUNDIALS_LIBRARY_DIRS,
            libraries=LIBRARIES + ['sundials_cvode'],
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        ),
        setuptools.Extension(
            name='sksundae._cy_ida',
            sources=['src/sksundae/_cy_ida.pyx'],
            include_dirs=SUNDIALS_INCLUDE_DIRS,
            library_dirs=SUNDIALS_LIBRARY_DIRS,
            libraries=LIBRARIES + ['sundials_ida'],
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        ),
    ]

    ext_modules = cythonize(
        extensions,
        compiler_directives={'language_level': 3},
    )

    return ext_modules


# Run the setup
BUILD_SDIST = os.environ.get('BUILD_SDIST', 0)

if int(BUILD_SDIST):  # Don't compile extensions if just building sdist
    setuptools.setup(
        include_package_data=True,
    )
else:
    setuptools.setup(
        include_package_data=True,
        ext_modules=get_extensions(),
    )
