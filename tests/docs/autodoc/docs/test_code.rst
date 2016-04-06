=========
Test Code
=========

Software Test Specification
===========================

.. item-list::
   :filter: ^SW_TEST_

Integration Level Test Specification
====================================

This section could specify test cases on the integration level.

Unit Level Test Specification
=============================

This section specifies test cases on the unit level.

.. automodule:: test_code
   :members:

.. item:: SW_TEST_002 The abstract method shall raise a
                      NotImplementedError.
    :validates: SW_REQ_002

.. item:: SW_TEST_003 The "cat" class shall have the animal class as
                      superclass.
    :validates: SW_REQ_003

    This test case references a missing requirement.

.. item:: SW_TEST_004 The concrete implementation of the "cat" class
                      method "talk" shall return "Meow!".
    :validates: SW_REQ_004

.. item:: SW_TEST_006 The concrete implementation of the "dog" class
                      method "talk" shall return "Woof!".
    :validates: SW_REQ_006
