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

extensions = [
    "sphinx_design",
    "sphinx_immaterial",
    "sphinx.ext.autodoc",
    "sphinxcontrib.programoutput",
    "sphinxcontrib.autodoc_pydantic",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_immaterial"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html"],
}

html_logo = "./_static/sphinx-emf-logo-white.png"
# html_favicon = "./_static/sphinx-emf-logo-favicon.png"
# material theme options (see theme.conf for more information)
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
    },
    "site_url": "https://sphinx-emf.useblocks.com",
    "repo_url": "https://github.com/useblocks/sphinx-emf",
    "repo_name": "Sphinx-EMF",
    "repo_type": "github",
    "edit_uri": "blob/master/docs",
    # "google_analytics": ["UA-XXXXX", "auto"],
    "globaltoc_collapse": True,
    "features": [
        "navigation.sections",
        "navigation.top",
        "search.share",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "blue",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "blue",
            "accent": "yellow",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to light mode",
            },
        },
    ],
    "toc_title_is_page_title": True,
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

rst_epilog = """
.. |ex| replace:: **Example**

.. |out| replace:: **Result**

.. |br| raw:: html

   <br>

"""


def process_docstring(app, what, name, obj, options, lines):
    pass


def before_process_signature(app, obj, bound_method):
    pass


def process_signature(app, what, name, obj, options, signature, return_annotation):
    if name.startswith("sphinx_emf.config.model."):
        return "", None
    return None


def setup(app):
    app.connect("autodoc-process-docstring", process_docstring)
    app.connect("autodoc-before-process-signature", before_process_signature)
    app.connect("autodoc-process-signature", process_signature)


add_module_names = False
python_use_unqualified_type_names = True
autodoc_member_order = "bysource"
