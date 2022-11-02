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

All configuration options starts with the prefix ``emf_`` for Sphinx-EMF.

Sphinx-EMF features some nested configuration parameters and therefore
uses `pydantic <https://pydantic-docs.helpmanual.io/>`_ to validate the configuration.
The following parameters start with one of the 3 pydantic class names:

* ``SphinxEmfCommonConfig`` parameters common to CLI and the Builder
* ``SphinxEmfCliConfig`` CLI parameters
* ``SphinxEmfBuilderConfig`` Sphinx Builder parameters

The CLI script transforms from XMI to RST (needs) while the Sphinx Builder reads RST and writes
XMI. The classes are needed just for pydantic, all settings are primitive Python types such as
dictionaries, lists, tuples, lists, strings, bools and integers.

.. note::
   Despite the prefixed class name in the documentation, the option itself does not include
   the class name, only the parameters starting with ``emf_``.



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
