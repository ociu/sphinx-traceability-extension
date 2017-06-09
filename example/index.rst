.. Example documentation master file, created by
   sphinx-quickstart on Sat Sep  7 17:17:38 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Example's documentation!
===================================

Contents:

.. toctree::
   :maxdepth: 1

   SRS
   SSS

.. item:: r001 First requirement
   :class: functional requirement

   This is one item

   - More content
   - More again

     - And nested content
     - *other* with **emphasis** and
     - .. note:: a note

          Yes, a note

.. item:: r002
   :class: critical

   We have to extend this section

This text is not part of any item

.. item:: r003 The great
   :class: secondary
   :trace: r002
   :ext_toolname: namespace:group:document

   Clean up all this.

.. item:: r005 Another
   :class: terciary
   :trace: r002 r003

   Clean up all this again

.. item:: r006 Depends on all
   :class: terciary
   :trace: r001
           r002
           r003 r005

   To demonstrate that bug #2 is solved

.. item:: r007 Depends on all with stereotypes
   :class: terciary
   :trace: r001
   :validates: r002
   :fulfills:  r003
           r005

   To demonstrate stereotype usage in relationships


.. requirement:: r100 A requirement using the ``requirement`` type

   This item has been defined using other directive. It easily extends
   rst semantics

.. item:: r008 Requirement with invalid reference to other one
    :trace: non_existing_requirement

    Ai caramba, this should report a broken link to an non existing requirement.

.. item:: r009 Requirement with invalid relation kind to other one
    :non_existing_relation: r007

    Ai caramba, this should report a warning as the relation kind does not exist.

Item list
=========

List all items:

.. item-list::


List all items beginning with ``r00``

.. item-list::
   :filter: r00

List system requirements (beginning with SYS)

.. item-list::
   :filter: ^SYS

List all well-formed SYS and SRS requirements

.. item-list::
   :filter: ^S[YR]S_\d

Item matrix
===========

All relationships

.. item-matrix:: All

Traceability from SRS to SSS

.. item-matrix:: SRS to SSS
   :target: SYS
   :source: SRS
   :type:   fulfills

Traceability from SSS to SRS

.. item-matrix:: SSS to SRS
   :target: SRS
   :source: SYS
   :type:   fulfilled_by

Another matrix that should spawn a warning as the relation in *type* does not exist

.. item-matrix:: SSS to SRS
   :target: SRS
   :source: SYS
   :type:   non_existing_relation

Item tree
=========

Succesfull SYS tree

.. item-tree:: SYS
    :top: SYS
    :top_relation_filter: depends_on
    :type: fulfilled_by

Another tree that should spawn a warning as the relation in *top_relation_filter* does not exist.

.. item-tree:: warning for unknown relation
    :top: SYS
    :top_relation_filter: non_existing_relation
    :type: fulfilled_by

Another tree that should spawn a warning as the relation in *type* does not exist

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

Links and references
====================

Item reference: :item:`r001`

:item:`Item reference with alternative text<r001>`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
