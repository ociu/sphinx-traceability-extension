.. Example documentation master file, created by
   sphinx-quickstart on Sat Sep  7 17:17:38 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to an advanced documentation example integrating with autodoc
=====================================================================

Contents
--------

.. toctree::
   :maxdepth: 2

   prod_code
   test_code

Traceability Matrix
-------------------

Bi-directional traceability (forward = requirements -> test cases,
backward = test cases -> requirements) of the software requirements and the test
cases provide information about missing requirements and/or missing test cases.

.. item-matrix:: Traceability
   :source: SW_REQ_
   :target: SW_TEST_
   :type: validated_by

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
