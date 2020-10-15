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
    :asil: B

    For this item the checkbox value is overwritten by the checkbox-result directive in meeting_notes.rst.

.. checklist-item:: QUE-PACKAGE_TEST Tested the package
    :depends_on: QUE-PROCESS

    Have you tested the package?

.. checklist-item:: QUE-PROCESS Followed the process

    Did you follow the process?

.. checklist-item:: QUE-DOCUMENTATION Added documentation

    Did you add documentation?

.. checklist-item:: QUE_MEETING-UNIQUE_NAME Does every test case have a unique name?

.. checklist-item:: QUE_MEETING-HW_EXECUTION Did the test cases execute on actual hardware?

.. checklist-item:: QUE_MEETING-TEST_GUIDELINES Does the test report follow the guidelines?

.. checklist-item:: ITEM_MISSING_FROM_CHECKLIST Does not trigger a warning

    This item ID is not present in the checklist of the pull request, but this should not trigger a warning.

.. checklist-item:: CL-SOME_ITEM A checklist item from a different PR
    :nocaptions:

    Checklist item with hidden caption.

.. checklist-item:: CL-ANOTHER_ONE

    Checklist items inherit from regular items.

.. item:: CL-UNDEFINED_CL_ITEM Item that should be a checklist-item

    The item ID is present in the queried PR description, but won't get the configured checklist-attribute added since
    it's defined with the regular *item* directive.

.. attribute-link::
    :filter: CL-
    :asil: A

---------------------------
Matrices of checklist items
---------------------------

.. item-attributes-matrix:: Questions and answers
    :filter: QUE-
    :attributes: checked
    :onlycaptions:

.. item-attributes-matrix:: Checklist attribute matrix
    :filter: ^CL-
    :attributes: checked asil
    :onlycaptions:
