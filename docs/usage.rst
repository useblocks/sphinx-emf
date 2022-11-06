.. _usage:

Usage
=====

Generate RST from ECore XMI
---------------------------

The main idea of this extension is to maintain objects in a docs-as-code approach.
For this XMI data must be initially imported as need objects.
This extensions installs a CLI entry point that can be used for a one-time import::

    sphinx-emf-cli CONFPY_PATH

``CONFPY_PATH`` is the path to a Python configuration file (commonly conf.py) that contains all configuration
parameters requirement for the import.

The relevant parameters are fields of :any:`SphinxEmfCommonConfig` and :any:`SphinxEmfCliConfig`.


Generate ECore XMI from RST
---------------------------

This export of XMI from need objects is realized as Sphinx builder.
It must be called from the root of a Sphinx project::

    sphinx-build -b emf . _build/emf

All Sphinx-EMF configuration parameters must be available in the Sphinx conf.py file.

Besides `Sphinx-Needs parameters <https://sphinx-needs.readthedocs.io/en/latest/configuration.html>`_
the relevant Sphinx-EMF parameters are fields of :any:`SphinxEmfCommonConfig` and :any:`SphinxEmfBuilderConfig`.

The builder run will put the XMI output file to the directory ``_build/emf`` using the file name specified in
:any:`emf_xmi_output_name`.
