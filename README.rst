Introduction
============

``Sphinx-EMF`` makes it possible to connect
`Eclipse EMF <https://www.eclipse.org/modeling/emf/>`_ ECore models with
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_.

The Sphinx extensions comes with 2 main features:

* a CLI script ``sphinx-emf-cli`` that reads an XMI model and writes RST files contain needs objects
* a Sphinx builder that reads a Sphinx project containing Sphinx-Needs objects and writes an M1 XMI model from it 

Both features require an EMF ECore M2 model.

Usage
=====

1. Install with pip::

    pip install sphinx-emf

2. Add it to your project with poetry::

    poetry add sphinx-emf
