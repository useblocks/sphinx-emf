.. _changelog:

Changelog
=========

.. _Unreleased Changes: http://github.com/useblocks/sphinx-emf/compare/0.2.0...HEAD
.. _0.1.0: https://github.com/useblocks/sphinx-emf/tree/0.1.0
.. _0.2.0: http://github.com/useblocks/sphinx-emf/compare/0.1.0...0.2.0
.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

All notable *functional* changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_.

Unreleased
------------

Please see all `Unreleased Changes`_ for more information.

`0.2.0`_ - 2022-11-07
---------------------

Main reason for this release is the naming change of configuration parameters.
The `(E)MOF terms <https://en.wikipedia.org/wiki/Meta-Object_Facility>`_ M1/M2 were replaced by XMI (model) and ECore (metamodel) as they are clearly defined in EMF.

**Changed**

- Renamed parameter ``emf_path_m1_model`` to ``emf_path_xmi``
- Renamed parameter ``emf_path_m2_model`` to ``emf_path_ecore``
- Renamed parameter ``emf_pre_read_hook`` to ``emf_pre_xmi_read_hook``
- Renamed parameter ``emf_post_read_hook`` to ``emf_post_xmi_read_hook``


`0.1.0`_ - 2022-11-03
---------------------

**Added**

- Initial extension version
- Initial start of the changelog
