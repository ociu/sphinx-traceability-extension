===============
Software Design
===============

.. contents:: `Contents`
    :depth: 3
    :local:

---------------------------
Design for mlx.traceability
---------------------------

.. item:: DESIGN-TRACEABILITY Top level design for mlx.traceability
    :fulfills: RQT-TRACEABILITY

    Since the sphinx documentation system is python based, and it allows for plugin development in seperate
    python packages, python was chosen. No limit should exist on the version of python or sphinx.

    .. uml::
        :align: center

        TraceableBaseClass <|-- TraceableItem
        TraceableBaseClass <|-- TraceableAttribute
        TraceableItem "1" *-- "N" TraceableAttribute
        TraceableCollection "1" *-- "N" TraceableItem
        Exception <|-- TraceabilityException
        Exception <|-- MultipleTraceabilityExceptions

.. item:: DESIGN-ITEMIZE Allow splitting the documentation in parts
    :depends_on: DESIGN-TRACEABILITY
    :fulfills: RQT-ITEMIZE

    A directive name `item` is added to sphinx through the plugin that allows splitting the documentation
    into parts. The documentation parts are stored as objects of class `TraceableItem`. All `TraceableItem`
    objects are stored in a container class `TraceableCollection`.

.. item:: DESIGN-DOCUMENTATION_ID Identification of documentation part
    :depends_on: DESIGN-ITEMIZE
    :fulfills: RQT-ITEMIZE

    A first argument to the `item` directive is used as a unique identifier for the documentation part. The
    identifier can be any string - not containing spaces.

    To ensure uniqueness of the identifier, the `TraceableCollection` is used. When a `TraceableItem` will
    be added to the collection, its identifier is first checked to not appear in the collection yet. If it
    exists already, a warning is added to the documentation build log.

.. item:: DESIGN-CAPTION Brief description of documentation part
    :depends_on: DESIGN-ITEMIZE
    :fulfills: RQT-CAPTION

    A second optional argument to the `item` directive is used as a brief description, or caption of the
    documentation part. This argument is allowed to have spaces. The caption is stored in
    the `TraceableItem` object.

.. item:: DESIGN-CONTENT Conten of documentation part
    :depends_on: DESIGN-ITEMIZE

    The content of the `item` directive is used as the content of the documentation part.
    The caption is stored in the `TraceableItem` object. The content is forwarded through the sphinx
    parser. So other plugins and/or the native sphinx tool performs conversions from reStructured text
    (rst) syntax to docutils nodes.

.. item:: DESIGN-ATTRIBUTES Documentation parts can have attributes
    :depends_on: DESIGN-ITEMIZE

    Attributes shall be able to be added to the documentation parts.
    Attributes have a key and an optional value.
    The set of attributes and the validness of the attribute values shall be configurable.

.. item:: DESIGN-RELATIONS Documentation parts can be linked to each other
    :depends_on: DESIGN-ITEMIZE

    Documentation parts shall be able to link to other documentation parts.
    The set of relations shall be configurable.

.. item:: DESIGN-AUTO_REVERSE Automatic creation of reverse relations
    :depends_on: DESIGN-RELATIONS

    When a documentation part <A> is related to a documentation part <B> (forward relation), the reverse
    relation from documentation part <B> to documentation part <A> shall be automatically created.

.. item:: DESIGN-LIST Listing documentation parts
    :depends_on: DESIGN-ITEMIZE

    A list of documentation parts matching a certain query shall be able to be retrieved.

.. item:: DESIGN-COVERAGE Calculation of coverage for relations between documentation parts
    :depends_on: DESIGN-RELATIONS

    The plugin shall be able to calculate the coverage for a certain type of relation between
    documentation parts.

.. item:: DESIGN-MATRIX Auto-generation of a traceability matrix
    :depends_on: DESIGN-RELATIONS

    The relations between documentation parts shall be able to be queried, and an overview matrix
    shall be able to be generated.

.. item:: DESIGN-TREE Auto-generation of a traceability tree
    :depends_on: DESIGN-RELATIONS

    The relations between documentation parts shall be able to be queried, and an overview tree
    shall be able to be generated.

.. item:: DESIGN-ATTRIBUTES_MATRIX Overview of attributes on documentation parts
    :depends_on: DESIGN-ATTRIBUTES

    An overview table of the attribute values for documentation parts shall be generated.

-------------------
Traceability matrix
-------------------

Tree of design
==============

.. item-tree:: Design tree
    :top: DESIGN
    :top_relation_filter: depends_on
    :type: impacts_on

Design reverse coverage
=======================

.. item-matrix:: Trace design to requirements
    :source: DESIGN
    :target: RQT
    :sourcetitle: Design
    :targettitle: Requirements
    :nocaptions:
    :stats:

Implementation coverage
=======================

.. item-matrix:: Trace design to implementation
    :source: DESIGN
    :target: IMPL
    :sourcetitle: Design
    :targettitle: Implementation
    :nocaptions:
    :stats:

