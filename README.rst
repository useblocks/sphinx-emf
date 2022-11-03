**Complete documentation**: https://sphinx-emf.useblocks.com/

Introduction
============

Sphinx-EMF makes it possible to exchange data between
`Eclipse EMF <https://www.eclipse.org/modeling/emf/>`_ ECore models and
`Sphinx-Needs <https://github.com/useblocks/sphinx-needs>`_.

This Sphinx extensions comes with 2 main features:

* a CLI script ``sphinx-emf-cli`` that reads an XMI model and writes RST files contain needs objects
* a Sphinx builder that reads a Sphinx project containing Sphinx-Needs objects and writes an M1 XMI model from it 

Both features require an EMF ECore M2 model.
