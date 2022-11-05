
Sphinx-EMF
==========

Sphinx-EMF makes it possible to exchange data between
`Eclipse EMF <https://www.eclipse.org/modeling/emf/>`_ ECore models and
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_.

This Sphinx extensions comes with 2 main features:

* a CLI script ``sphinx-emf-cli`` that reads an XMI model and writes RST files contain needs objects
* a Sphinx builder that reads a Sphinx project containing Sphinx-Needs objects and writes an XMI model from it

Both features require an EMF ECore metamodel.


.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   configuration
   usage
   contributing
   support
   license
   changelog

Motivation
----------

Sphinx-Needs makes managing objects inside docs-as-code approaches easy and joyful.
It also features options to get objects in and out the Sphinx-Needs ecosystem:

- `needs.json <https://sphinx-needs.readthedocs.io/en/latest/builders.html#needs-builder>`_
- `Dynamic functions <https://sphinx-needs.readthedocs.io/en/latest/dynamic_functions.html>`_
- `Sphinx-Collections <https://sphinx-collections.readthedocs.io/en/latest/>`_

They all do not support enforcing a defined model when exporting or importing needs.
This includes options, links, the needs body and nested needs in the body.

Sphinx-EMF makes it possible to define an EMF ECore `metamodel <https://en.wikipedia.org/wiki/Meta-Object_Facility>`_
and write RST files from an XMI model that follows the metamodel.
Objects can then be managed in docs-as-code and exported back to XMI using a Sphinx builder.

The extension also enables data exchange with tools that use EMF ECore XMI as data store or as export/import format.
