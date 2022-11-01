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

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCommonConfig.emf_path_m2_model

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCommonConfig.emf_pre_read_hook

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCommonConfig.emf_post_read_hook

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCommonConfig.emf_class_2_need_def

   .. autoclass:: sphinx_emf.config.model.Class2NeedDefValues
      :members:
      :undoc-members:

   .. autoclass:: sphinx_emf.config.model.Class2NeedDefSettings
      :members:
      :undoc-members:

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_path_m1_model

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_rst_output_configs

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_rst_indent

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_allowed_classes

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_denied_classes

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_allowed_values

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_denied_values

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_sort_field

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_templates_dir

.. autoattribute:: sphinx_emf.config.model.SphinxEmfCliConfig.emf_show_nested_need_title

.. autoattribute:: sphinx_emf.config.model.SphinxEmfBuilderConfig.emf_model_roots

.. autoattribute:: sphinx_emf.config.model.SphinxEmfBuilderConfig.emf_sort_xmi_attributes

.. autoattribute:: sphinx_emf.config.model.SphinxEmfBuilderConfig.emf_xmi_output_name

.. autoattribute:: sphinx_emf.config.model.SphinxEmfBuilderConfig.emf_convert_rst_to_plain
