.. Example documentation master file, created by
   sphinx-quickstart on Sat Sep  7 17:17:38 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Example's documentation!
===================================

Contents:

.. toctree::
    :maxdepth: 1

    rqts/SRS
    rqts/SSS

.. item:: r001 First requirement
    :class: functional requirement
    :status: Draft
    :asil: C
    :aspice: 3

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
    :aspice: 3
    :asil: C
    :class: terciary
    :trace: r002 r002 r003
    :nocaptions:

    Clean up all this again

.. item:: r006 Depends on all
    :class: terciary
    :trace: r001
        r002
        r003
        r005

    To demonstrate that bug #2 is solved

.. item:: r007 Depends on all with stereotypes
    :asil: X
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

    Ai caramba, this should report a broken link to an non existing requirement.

.. item:: r009 Requirement with invalid relation kind or attribute
    :non_existing_relation_or_attribute: r007

    Ai caramba, this should report a warning as the relation kind or attribute does not exist.

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

.. item-attributes-matrix:: None
    :filter: r
    :attributes: asil

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

All attributes for all items
------------------------------

.. item-attributes-matrix:: All attributes for all items

All attributes for non-matching-filter
--------------------------------------

.. item-attributes-matrix:: Non-matching filter: empty table
    :filter: regex_doesnt_match_anything

Invalid attribute for all items
-------------------------------

.. item-attributes-matrix:: Invalid attribute
    :attributes: non_existing_relation_or_attribute asil

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
