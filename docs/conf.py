"""Configuration file for the Sphinx documentation builder."""

import os
import sys

sys.path.insert(0, os.path.abspath("."))


# -- Project information -----------------------------------------------------

project = "sponsorblock.py"  # pylint: disable=invalid-name
copyright = "2021, Wasi Master"  # pylint: disable=redefined-builtin,invalid-name
author = "Wasi Master"  # pylint: disable=invalid-name

# The full version, including alpha/beta/rc tags
release = "0.2.0"  # pylint: disable=invalid-name

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
]

autodoc_member_order = "bysource"  # pylint: disable=invalid-name
autoclass_content = "both"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
html_title = "Welcome to sponsorblock.py"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"  # pylint: disable=invalid-name


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
