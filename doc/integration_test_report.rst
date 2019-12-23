
=======================
Integration test report
=======================

.. contents:: `Contents`
    :depth: 3
    :local:

SRS and SSS
===========

.. toctree::
    :maxdepth: 1

    rqts/SRS
    rqts/SSS

Other requirements
==================

.. item:: r001 First requirement
    :class: functional requirement
    :status: Draft
    :asil: C
    :aspice: 1
    :value: 5

    This is one item

    - More content
    - More again

        - And nested content
        - *other* with **emphasis** and

    .. note:: a note

        Yes, a note

.. item:: r002
    :class: critical
    :status: Reviewed
    :asil: C
    :value: 1

    We have to extend this section

This text is not part of any item

.. item:: r003 The great
    :class: secondary
    :trace: r002
    :ext_toolname: namespace:group:document
    :asil: A
    :status: Approved

    Clean up all this.

.. item:: r005 Another (does not show captions on the related items)
    :aspice: 2
    :asil: C
    :class: terciary
    :trace: r002 r002 r003
    :nocaptions:

    Clean up all this again

.. item:: r005 Duplicate: should trigger warning

    As this one is the second one, this should **not** appear in the generated documentation.

.. item:: r006 Depends on all
    :class: terciary
    :asil: C
    :value: 12
    :trace: r001
        r002
        r003
        r005

    To demonstrate that bug #2 is solved

.. item:: r007 Depends on all with stereotypes
    :asil: X
    :aspice: 2
    :class: terciary
    :trace: r001
    :validates: r002
    :fulfills:  r003
        r005

    To demonstrate stereotype usage in relationships.

    To demonstrate invalid attribute, X is not valid attribute for ASIL level (should not appear in e.g. item-list).

.. requirement:: r100 A requirement using the ``requirement`` type
    :asil: QM

    This item has been defined using other directive. It easily extends
    rst semantics

.. item:: r008 Requirement with invalid reference to other one
    :asil: D
    :trace: non_existing_requirement

    Ai caramba, this should report a broken link to a non-existing requirement.

.. item:: r009 Requirement with invalid relation kind or attribute
    :non_existing_relation_or_attribute: r007

    Ai caramba, this should report a warning as the relation kind or attribute does not exist.

Integration tests
=================

.. item:: ITEST-CAPTION Tests caption
    :validates: RQT-CAPTION

.. item:: ITEST-AUTO_REVERSE Tests automatic creation of reverse relations
    :validates: RQT-AUTO_REVERSE

.. item:: ITEST-COVERAGE Tests calculation of coverage for relations between documentation parts.
    :validates: RQT-COVERAGE

.. item:: ITEST-MATRIX Tests auto-generation of traceability matrix.
    :validates: RQT-MATRIX

.. item:: ITEST-TREE Tests auto-generation of a traceability tree.
    :validates: RQT-TREE

.. item:: ITEST-TREE_SCOPE Tests scope of a traceability tree.
    :validates: RQT-TREE

.. item:: ITEST-ATTRIBUTES_MATRIX Tests overview of attributes on documentation parts
    :validates: RQT-ATTRIBUTES_MATRIX

.. item:: ITEST-LIST Tests listing of documentation parts
    :validates: RQT-LIST

.. item:: ITEST-r100 Test a requirement using the ``requirement`` type
    :validates: r100

Integration test reports
========================

.. item:: ITEST_REP-CAPTION Report with attribute missing from priority list
    :depends_on: ITEST-CAPTION
    :result: RUNNING

.. item:: ITEST_REP-AUTO_REVERSE
    :depends_on: ITEST-AUTO_REVERSE
    :result: FAIL

.. item:: ITEST_REP-COVERAGE
    :depends_on: ITEST-COVERAGE
    :result: error

.. item:: ITEST_REP-MATRIX
    :depends_on: ITEST-MATRIX
    :result: pass

.. item:: ITEST_REP-TREE
    :depends_on: ITEST-TREE
    :result: PASS

.. item:: ITEST_REP-TREE_SCOPE
    :depends_on: ITEST-TREE_SCOPE
    :result: ERROR

.. item:: ITEST_REP-ATTRIBUTES_MATRIX
    :depends_on: ITEST-ATTRIBUTES_MATRIX

.. item:: ITEST_REP-r100
    :depends_on: ITEST-r100

Attribute details
=================

.. item-attribute:: ASIL The level for ASIL

    In ISO26262 ASIL is defined as Automotive Safety Integrity Level. The level can be
    at A/B/C/D for increasing safety requirements.

.. item-attribute:: ASPICE The level for A-SPICE

    Similar to ASIL, ASPICE is an automitve safety standard. Levels are ASPICE 1/2/3.

.. item-attribute:: non_existing_attribute This should trigger a warning

Item list
=========

No items
--------

.. item-list:: No items
    :filter: this_regex_doesnt_match_any_item

List all items
--------------

.. item-list:: All available items (no captions)
    :nocaptions:


List all items beginning with ``r00``
-------------------------------------

.. item-list::
    :filter: ^r00

List system requirements (beginning with SYS)
---------------------------------------------

.. item-list:: System requirements
    :filter: ^SYS

List all well-formed SYS and SRS requirements
---------------------------------------------

.. item-list:: System and software requirements
    :filter: ^S[YR]S_\d

List all items with ASIL attribute
----------------------------------

.. item-list:: All ASIL items
    :asil: (QM|[ABCD])

List all items with ASIL and Draft/Approved attribute
-----------------------------------------------------

.. item-list:: All Draft ASIL items
    :status: (Draft|Approved)
    :asil: (QM|[ABCD])

Item matrix
===========

No relationships
----------------

.. item-matrix:: None
    :source: source_regex_doesnt_match_anything
    :targettitle: nothing
    :sourcetitle: more of nothing
    :stats:

All relationships
-----------------

.. item-matrix:: All (no captions)
    :nocaptions:
    :stats:
    :group: bottom

All relationships with items having ASIL-C/D attribute
------------------------------------------------------

.. item-matrix:: All ASIL-C/D (with captions)
    :asil: [CD]
    :stats:

Traceability from SRS to SSS
----------------------------

.. item-matrix:: Software requirements fulfilling system requirements
    :target: SYS
    :source: SRS
    :targettitle: system requirement
    :sourcetitle: software requirement
    :type: fulfills
    :stats:

Traceability from SSS to SRS
----------------------------

.. item-matrix:: System requirements fulfilled by software requirements
    :target: SRS
    :source: SYS
    :targettitle: software requirement
    :sourcetitle: system requirement
    :type: fulfilled_by
    :stats:

Another matrix that should spawn a warning as the relation in *type* does not exist
-----------------------------------------------------------------------------------

.. item-matrix:: System requirements traced to software requirements, using a non-existing relationship (=warning)
    :target: SRS
    :source: SYS
    :type: non_existing_relation
    :targettitle: system requirement
    :sourcetitle: software requirement

Item attribute matrix
=====================

ASIL attribute for all r-items
------------------------------

.. item-attributes-matrix:: ASIL attribute for all r-items, reverse sorted on item-ID
    :filter: r
    :attributes: asil
    :reverse:

ASIL attribute for all r-items having ASIL-B/C
----------------------------------------------

.. item-attributes-matrix:: ASIL attribute for all r-items, having ASIL-C/D
    :filter: r
    :attributes: asil
    :asil: [CD]

Some attributes for all items
-----------------------------

.. item-attributes-matrix:: ASIL and status attribute for all items
    :filter:
    :attributes: asil status

All attributes for all r-items
------------------------------

.. item-attributes-matrix:: All attributes for all r-items
    :filter: r
    :attributes:
    :nocaptions:

All attributes for all items
----------------------------

.. item-attributes-matrix:: All attributes for all items

All attributes for all items, sorted
------------------------------------

.. item-attributes-matrix:: All attributes for all items, sorted on ASIL level
    :sort: asil
    :nocaptions:

All attributes for all items, reverse sorted on 2 attributes
------------------------------------------------------------

.. item-attributes-matrix:: All attributes for all items, reverse sorted on ASIL level and value
    :filter: r
    :attributes: asil value
    :sort: asil value
    :nocaptions:
    :reverse:

All attributes for items having a non-empty attribute
-----------------------------------------------------

.. item-attributes-matrix:: All attributes for items having a non-empty asil attribute
    :asil: ^.+$
    :sort: asil

.. item-attributes-matrix:: All attributes for items having a non-empty asil+aspice attribute
    :asil: ^.+$
    :aspice: ^.+$
    :sort: asil aspice
    :reverse:
    :nocaptions:

.. item-attributes-matrix:: Transposed version of the previous matrix
    :asil: ^.+$
    :aspice: ^.+$
    :sort: asil aspice
    :reverse:
    :transpose:
    :nocaptions:

All attributes for non-matching-filter
--------------------------------------

.. item-attributes-matrix:: Non-matching filter: empty table
    :filter: regex_doesnt_match_anything

Invalid attribute for all items
-------------------------------

.. item-attributes-matrix:: Invalid attribute
    :attributes: non_existing_relation_or_attribute asil

Invalid sort attributes for all items
-------------------------------------

.. item-attributes-matrix:: Invalid sort attribute
    :sort: non_existing_relation_or_attribute asil

Item 2D matrix
==============

SRS to SSS
----------

.. item-2d-matrix:: System requirements fulfilled by software requirements
    :target: SRS
    :source: SYS
    :type: fulfilled_by

.. item-2d-matrix:: System requirements fulfilled by software requirements
    :target: SRS
    :source: SYS
    :hit: x
    :miss: o
    :type: fulfilled_by

.. item-2d-matrix:: all to all with ASIL-C/D attribute
    :target:
    :source:
    :asil: [CD]
    :type: trace traced_by

SSS to SRS
----------

.. item-2d-matrix:: Software requirements fulfilling system requirements
    :target: SYS
    :source: SRS
    :hit: yes
    :miss:
    :type: fulfills

Another 2D matrix that should spawn a warning as the relation in *type* does not exist
--------------------------------------------------------------------------------------

.. item-2d-matrix:: System requirements traced to software requirements, using a non-existing relationship (=warning)
    :target: SRS
    :source: SYS
    :hit: yes
    :miss: no
    :type: non_existing_relation

Item tree
=========

Empty tree
----------

.. item-tree:: Empty
    :top: this_regex_doesnt_match_anything

Succesfull SYS tree
-------------------

.. item-tree:: SYS
    :top: SYS
    :top_relation_filter: depends_on
    :type: fulfilled_by

.. item-tree:: SYS (no captions)
    :top: SYS
    :top_relation_filter: depends_on
    :type: fulfilled_by
    :nocaptions:

.. item-tree:: r
    :top: r
    :top_relation_filter: trace
    :type: traced_by

.. item-tree:: r (only ASIL-C/D attributed)
    :top: r
    :top_relation_filter: trace
    :type: traced_by
    :asil: [CD]

Another tree that should spawn a warning as the relation in *top_relation_filter* does not exist.
-------------------------------------------------------------------------------------------------

.. item-tree:: warning for unknown relation
    :top: SYS
    :top_relation_filter: non_existing_relation
    :type: fulfilled_by

Another tree that should spawn a warning as the relation in *type* does not exist
---------------------------------------------------------------------------------

.. item-tree:: warning for unknown relation
    :top: SYS
    :top_relation_filter: depends_on
    :type: non_existing_relation

.. only:: TEST_FOR_ENDLESS_RECURSION

    Another tree that should spawn a warning as the forward and reverse relation are in the *type* field.

    .. item-tree:: warning for forward+reverse
        :top: SYS
        :top_relation_filter: depends_on
        :type: fulfilled_by fulfills

Item link
=========

This is a subtitle that has a ``item-link`` item under it. You shouldn't see anything in the rendering, though
--------------------------------------------------------------------------------------------------------------

.. item-link::
    :sources: r001
    :targets: r002
    :type: trace

.. test: link to later (bottom of this page) defined source, should not warn

.. item-link::
    :sources: late001
    :type: trace
    :targets: r001

.. warning on next item-link due to missing sources:

.. item-link::
    :type: trace
    :targets: r100

.. warning on next item-link due to missing targets:

.. item-link::
    :sources: r100
    :type: trace

.. warning on next item-link due to missing relation type:

.. item-link::
    :sources: r100
    :targets: r001

Extra late requirements
-----------------------

.. item:: late001

    Item is added after adding links from it using item-link above. This shouldn't give a warning.

Links and references
====================

Item reference: :item:`r001`

:item:`Item reference with alternative text<r001>`
