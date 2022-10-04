"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# linter disables for Sphinx specific configuration settings
# pylint: disable=invalid-name

# Cannot exclude conf.py in vulture, see https://github.com/PyCQA/prospector/issues/505
# The following lines also suppresses pylint unfortunately, however the file is clean
# flake8: noqa

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sphinx-emf"
copyright = "2022, useblocks GmbH"  # pylint: disable=redefined-builtin
author = "useblocks GmbH"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html"],
}

html_logo = "./_static/logo.png"
html_favicon = "./_static/logo-favicon.ico"
html_theme_options = {
    # TOC options
    'collapse_navigation': False,
    'sticky_navigation': False,
    'navigation_depth': 7,
    # content options
    'prev_next_buttons_location': None,
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

