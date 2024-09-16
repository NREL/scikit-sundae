# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'scikit-sundae'
copyright = '2024, Corey R. Randall'
author = 'Corey R. Randall'
version = '1.0.0'
release = '1.0.0'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'autoapi.extension',
    'myst_nb',
    'sphinx_design',
    'sphinx_favicon',
    'sphinx_copybutton',
    'sphinx.ext.githubpages',
]

templates_path = ['templates']

exclude_patterns = [
    'build',
    'Thumbs.db',
    '.DS_Store',
    '*.ipynb_checkpoints',
    '__pycache__',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.ipynb': 'myst-nb',
    '.myst': 'myst-nb',
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html

html_theme = 'pydata_sphinx_theme'

html_favicon = 'static/favicon.ico'

html_static_path = ['static']
html_js_files = ['custom.js']
html_css_files = ['custom.css']

html_context = {'default_mode': 'dark'}

html_sidebars = {'index': [], '**': ['sidebar-nav-bs.html']}

html_theme_options = {
    'logo': {
        'image_light': 'static/light.png',
        'image_dark': 'static/dark.png'
    },
    'header_links_before_dropdown': 5,
    'navbar_align': 'content',
    'footer_start': ['copyright.html'],
    'footer_end': ['sphinx-version.html'],
    'navbar_persistent': ['search-button-field.html'],
    'secondary_sidebar_items': ['page-toc.html'],
    'search_bar_text': 'Search...',
    'show_prev_next': False,
    'collapse_navigation': True,
    'show_toc_level': 0,
    'pygments_light_style': 'tango',
}


# -- Options for napoleon ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

napoleon_use_rtype = False
napoleon_custom_sections = [
    'Accessing the documentation',
    'Acknowledgements',
]


# -- Options for autoapi -----------------------------------------------------
# https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html

autoapi_type = 'python'
autoapi_ignore = ['*/__pycache__/*']
autoapi_dirs = ['../../src/sksundae']
autoapi_keep_files = True
autoapi_root = 'api'
autoapi_member_order = 'groupwise'
autodoc_typehints = 'none'
autoapi_python_class_content = 'both'
autoapi_options = [
    'members',
    'inherited-members',
    'undoc-members',
    'show-module-summary',
    'imported-members',
]


# -- Options for myst --------------------------------------------------------
# https://myst-nb.readthedocs.io/en/latest/configuration.html

nb_execution_timeout = 300
nb_number_source_lines = True
myst_enable_extensions = ['amsmath', 'dollarmath']
