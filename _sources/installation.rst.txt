Installation
============

Using poetry
------------

.. code-block:: bash

    poetry add sphinx-emf

Using pip
---------

.. code-block:: bash

    pip install sphinx-emf

Using sources
-------------

.. code-block:: bash

    git clone https://github.com/useblocks/sphinx-emf
    cd sphinx-emf
    pip install .
    # or
    poetry install


Activation
----------

For final activation, please add `sphinx_emf` to the project's extension list of your **conf.py** file.

.. code-block:: python

   extensions = ["sphinx_emf",]

For the full configuration, please read :ref:`config`.
