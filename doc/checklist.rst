=========
Checklist
=========

.. contents:: `Contents`
    :depth: 3
    :local:

---------------
Checklist items
---------------

.. checklist-item:: QUE-UNIT_TESTS Added unit tests
    :depends_on: QUE-PROCESS

    Have you written unit tests for regression detection?

.. checklist-item:: QUE-PACKAGE_TEST Tested the package
    :depends_on: QUE-PROCESS

    Have you tested the package?

.. checklist-item:: QUE-PROCESS Followed the process

    Did you follow the process?

.. checklist-item:: ITEM_MISSING_FROM_CHECKLIST Triggers a warning

    This item ID is not present in the checklist of the pull request and should trigger a warning.

.. checklist-item:: CL-SOME_ITEM A checklist item from a different PR
    :nocaptions:

    Checklist item with hidden caption.

.. checklist-item:: CL-ANOTHER_ONE Another checklist item

    Checklist items inherit from regular items.

.. item:: CL-LUCKY_ONE Item that should be a checklist-item

    The item ID is present in the queried PR description, but won't get the configured checklist-attribute added since
    its defined with the regular item directive.

-------------------------
Matrices of checklist items
-------------------------

.. item-attributes-matrix:: Questions and answers
    :filter: QUE-
    :attributes: checked

.. item-attributes-matrix:: Checklist attribute matrix
    :filter: ^CL-
    :attributes: checked
