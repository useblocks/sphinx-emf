.. _config:

Configuration
=============

All configurations take place in your project's **conf.py** file.

Activation
----------

Add **sphinx_emf** to your extensions:

.. code-block:: python

   extensions = ["sphinx_needs", "sphinx_emf", ]

Options
-------

All configuration options start with the prefix ``emf_`` for Sphinx-EMF.

Sphinx-EMF features some nested configuration parameters and therefore
uses `pydantic <https://pydantic-docs.helpmanual.io/>`_ to validate the configuration.
There are 3 pydantic classes defined:

* ``SphinxEmfCommonConfig`` parameters common to CLI and the Sphinx Builder
* ``SphinxEmfCliConfig`` CLI specific parameters
* ``SphinxEmfBuilderConfig`` Sphinx Builder specific parameters

The CLI script transforms from XMI to RST (needs) while the Sphinx Builder reads RST and writes
XMI.

.. note::
   Above classes are not exposed to the user, they are just needed internally for pydantic.
   The class field names starting with ``emf_`` are the relevant configuration parameters
   with their documented types. You may put all configuration (common, CLI and builder) into your conf.py
   and use that file also as input parameter to the CLI script.

.. note::
   The type checking also uses TypedDict types which allows the validation of nested dictionaries.
   Those are added to the documentation as well (e.g. :class:`sphinx_emf.config.model.Class2NeedDefValues`).
   The class field names represent the values of the dictionary.

.. autopydantic_model:: sphinx_emf.config.model.SphinxEmfCommonConfig
   :model-show-json: False
   :model-show-field-summary: False
   :member-order: bysource

.. autoclass:: sphinx_emf.config.model.Class2NeedDefValues
   :members:
   :undoc-members:

.. autoclass:: sphinx_emf.config.model.Class2NeedDefSettings
   :members:
   :undoc-members:

.. autopydantic_model:: sphinx_emf.config.model.SphinxEmfCliConfig
   :model-show-json: False
   :model-show-field-summary: False
   :member-order: bysource

.. autopydantic_model:: sphinx_emf.config.model.SphinxEmfBuilderConfig
   :model-show-json: False
   :model-show-field-summary: False
   :member-order: bysource
