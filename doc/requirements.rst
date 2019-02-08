=====================
Software Requirements
=====================

.. contents:: `Contents`
    :depth: 3
    :local:

---------------------------------
Requirements for mlx.traceability
---------------------------------

.. item:: RQT-TRACEABILITY A plugin for sphinx documentation system, adding traceability

    System shall implement a plugin for the sphinx documentation system. It shall add tracebility within
    the documentation.

.. item:: RQT-ITEMIZE Allow splitting the documentation in parts
    :depends_on: RQT-TRACEABILITY

    The plugin shall allow for splitting the documentation in parts.

.. item:: RQT-DOCUMENTATION_ID Identification of documentation part
    :depends_on: RQT-ITEMIZE

    A documentation part shall have a unique identification.

.. item:: RQT-CAPTION Brief description of documentation part
    :depends_on: RQT-ITEMIZE

    A documentation part shall have a optional brief description.

.. item:: RQT-CONTENT Conten of documentation part
    :depends_on: RQT-ITEMIZE

    A documentation part shall have optional content. The content shall be parseable RST, and passed
    through the configured sphinx parser/renderer.

.. item:: RQT-ATTRIBUTES Documentation parts can have attributes
    :depends_on: RQT-ITEMIZE

    Attributes shall be able to be added to the documentation parts.
    Attributes have a key and an optional value.
    The set of attributes and the validness of the attribute values shall be configurable.

.. item:: RQT-RELATIONS Documentation parts can be linked to each other
    :depends_on: RQT-ITEMIZE

    Documentation parts shall be able to link to other documentation parts.
    The set of relations shall be configurable.

.. item:: RQT-AUTO_REVERSE Automatic creation of reverse relations
    :depends_on: RQT-RELATIONS

    When a documentation part <A> is related to a documentation part <B> (forward relation), the reverse
    relation from documentation part <B> to documentation part <A> shall be automatically created.

.. item:: RQT-LIST Listing documentation parts
    :depends_on: RQT-ITEMIZE

    A list of documentation parts matching a certain query shall be able to be retrieved.

.. item:: RQT-COVERAGE Calculation of coverage for relations between documentation parts
    :depends_on: RQT-RELATIONS

    The plugin shall be able to calculate the coverage for a certain type of relation between
    documentation parts.

.. item:: RQT-MATRIX Auto-generation of a traceability matrix
    :depends_on: RQT-RELATIONS

    The relations between documentation parts shall be able to be queried, and an overview matrix
    shall be able to be generated.

.. item:: RQT-TREE Auto-generation of a traceability tree
    :depends_on: RQT-RELATIONS

    The relations between documentation parts shall be able to be queried, and an overview tree
    shall be able to be generated.

.. item:: RQT-ATTRIBUTES_MATRIX Overview of attributes on documentation parts
    :depends_on: RQT-ATTRIBUTES

    An overview table of the attribute values for documentation parts shall be generated.

-------------------
Traceability matrix
-------------------

Tree of requirements
====================

.. item-tree:: Requirement tree
    :top: RQT
    :top_relation_filter: depends_on
    :type: impacts_on

Design coverage
===============

.. item-matrix:: Trace requirements to design
    :source: RQT
    :target: DESIGN
    :sourcetitle: Requirement
    :targettitle: Design
    :nocaptions:
    :stats:

Test coverage
=============

.. item-matrix:: Trace requirements to test cases
    :source: RQT
    :target: [IU]TEST
    :sourcetitle: Requirement
    :targettitle: Test case
    :nocaptions:
    :stats:

