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

        @startuml
        class TraceableBaseClass {
            + str id
            + str name
            + str caption
            + str docname
            + int lineno
            + docutils.nodes.Node node
            + str content

            + __init__(name)
            + update(other)
            + to_dict()
            + self_test()
        }

        class TraceableItem {
            + dict explicit_relations
            + dict implicit_relations
            + dict attributes
            # bool placeholder

            + __init__(item_id, placeholder=False)
            + __str__(explicit=True, implicit=True)
            + is_placeholder()
            + add_target(relation, target, implicit=False)
            + remove_targets(target_id, explicit=False, implicit=True)
            + iter_targets(relation, explicit=True, implicit=True)
            + iter_relations()
            + define_attribute(attr)
            + add_attribute(attr, value, overwrite=True)
            + remove_attribute(attr)
            + get_attribute(attr)
            + get_attributes(attrs)
            + iter_attributes()
            + is_match(regex)
            + attributes_match(attributes)
            + is_related(relations, target_id)
        }

        class TraceableAttribute {
            + str value

            + __init__(attr_id, value)
            + can_accept(value)
        }

        class TraceableCollection {
            + dict relations
            + dict items

            + __init__()
            + __str__()
            + add_relation_pair(forward, reverse='')
            + get_reverse_relation(forward)
            + iter_relations()
            + add_item(item)
            + get_item(item_id)
            + iter_items()
            + has_item(item_id)
            + add_relation(source_id, relation, target_id)
            + export(f_name)
            + self_test(docname=None)
            + are_related(source_id, relations, target_id)
            + get_items(regex, attributes={}, sortattributes=None, reverse=False)
        }

        abstract class TraceableBaseDirective {
            + {static} final_argument_whitespace = True

            + {abstract} run()
            + process_title(node, default_title='')
            + get_caption()
            + add_found_attributes(node)
            + remove_unknown_attributes(attributes, description, env)
            + check_relationships(relationships, env)
            + check_no_captions_flag(node, no_captions_config)
            + process_options(node, options, env=None)
            + check_option_presence(node, option)
        }

        class Item2DMatrixDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ItemAttributeDirective {
            + {static} required_arguments = 1
            + {static} optional_arguments = 1
            + {static} has_content = True
        }

        class ItemAttributesMatrixDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ItemDirective {
            + {static} required_arguments = 1
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = True

            # store_item_info(target_id, env)
            # add_relation_to_ids(relation, source_id, related_ids, env)
            # add_attributes(item, env)
        }

        class ItemLinkDirective {
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ItemListDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ItemMatrixDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ItemPieChartDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False

            # process_id_set(node, env)
            # process_label_set(node)
            # process_attribute(node, env)
        }

        class ItemTreeDirective {
            + {static} optional_arguments = 1
            + {static} dict option_spec
            + {static} has_content = False
        }

        class ChecklistItemDirective {
            + {static} dict query_results
        }

        class AttributeSortDirective {
            + {static} dict option_spec
            + {static} has_content = False
        }

        abstract class TraceableBaseNode {
            + {abstract} perform_replacement(app, collection)
            + {static} create_top_node(title)
            + make_internal_item_ref(app, item_id, caption=True)
            + {static} make_external_item_ref(app, target_text, relationship)
            + is_item_top_level(env, item_id)
            + make_attribute_ref(app, attr_id, value='')
            + has_warned_about_undefined(item_info, env)
            # {static} find_colors_for_class(hyperlink_colors, item_id)
        }

        class Item2DMatrix {
        }

        class ItemAttribute {
        }

        class ItemAttributesMatrix {
        }

        class Item {
            # {static} item = None

            # process_attributes(dl_node, app)
            # process_relationships(collection, *args)
            # list_targets_for_relation(relation, targets, dl_node, app)
        }

        class ItemLink {
        }

        class ItemList {
        }

        class ItemMatrix {
        }

        class ItemPieChart {
            + {static} collection = None
            + {static} relationships = []
            + {static} priorities = {}
            + {static} attribute_id = ''
            + {static} linked_attributes = {}

            + loop_relationships(top_source_id, source_item, pattern, match_function)
            + build_pie_chart(chart_labels, env)
            # set_priorities()
            # set_attribute_id()
            # match_covered(top_source_id, nested_source_item)
            # match_attribute_values(top_source_id, nested_target_item)
            # prepare_labels_and_values(lower_labels, attributes)
            # {static} get_statistics(count_uncovered, count_total)
        }

        class ItemTree {
            # generate_bullet_list_tree(app, collection, item_id, captions=True)
        }

        class AttributeSort {
        }

        class PendingItemXref {
        }

        TraceableBaseClass <|-- TraceableItem
        TraceableBaseClass <|-- TraceableAttribute
        TraceableItem "1" o-- "N" TraceableAttribute
        TraceableCollection "1" o-- "N" TraceableItem
        sphinx.environment.BuildEnvironment "1" o-- "1" TraceableCollection
        docutils.parsers.rst.Directive <|-- TraceableBaseDirective
        TraceableBaseDirective <|-- Item2DMatrixDirective
        TraceableBaseDirective <|-- ItemAttributeDirective
        TraceableBaseDirective <|-- ItemAttributesMatrixDirective
        TraceableBaseDirective <|-- ItemDirective
        TraceableBaseDirective <|-- ItemLinkDirective
        TraceableBaseDirective <|-- ItemListDirective
        TraceableBaseDirective <|-- ItemMatrixDirective
        TraceableBaseDirective <|-- ItemPieChartDirective
        TraceableBaseDirective <|-- ItemTreeDirective
        ItemDirective <|-- ChecklistItemDirective
        TraceableBaseNode <|-- docutils.nodes.General
        TraceableBaseNode <|-- docutils.nodes.Element
        TraceableBaseNode <|-- Item2DMatrix
        TraceableBaseNode <|-- ItemAttribute
        TraceableBaseNode <|-- ItemAttributesMatrix
        TraceableBaseNode <|-- Item
        TraceableBaseNode <|-- ItemLink
        TraceableBaseNode <|-- ItemList
        TraceableBaseNode <|-- ItemMatrix
        TraceableBaseNode <|-- ItemPieChart
        TraceableBaseNode <|-- ItemTree
        TraceableBaseNode <|-- PendingItemXref
        Item2DMatrixDirective "1" *-- "1" Item2DMatrix
        ItemAttributeDirective "1" *-- "1" ItemAttribute
        ItemAttributesMatrixDirective "1" *-- "1" ItemAttributesMatrix
        ItemDirective "1" *-- "1" Item
        ItemLinkDirective "1" *-- "1" ItemLink
        ItemListDirective "1" *-- "1" ItemList
        ItemMatrixDirective "1" *-- "1" ItemMatrix
        ItemPieChartDirective "1" *-- "1" ItemPieChart
        ItemTreeDirective "1" *-- "1" ItemTree
        AttributeSortDirective "1" *-- "1" AttributeSort
        Exception <|-- TraceabilityException
        Exception <|-- MultipleTraceabilityExceptions
        @enduml

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

.. item:: DESIGN-CONTENT Content of documentation part
    :depends_on: DESIGN-ITEMIZE

    The content of the `item` directive is used as the content of the documentation part.
    The caption is stored in the `TraceableItem` object. The content is forwarded through the sphinx
    parser. So other plugins and/or the native sphinx tool performs conversions from reStructuredText
    (rst) syntax to docutils nodes.

.. item:: DESIGN-ATTRIBUTES Documentation parts can have attributes
    :depends_on: DESIGN-ITEMIZE

    Attributes can be added to the documentation parts.
    Attributes have a key and an optional value.
    The set of attributes, their order and the validness of the attribute values are configurable.

.. item:: DESIGN-RELATIONS Documentation parts can be linked to each other
    :depends_on: DESIGN-ITEMIZE

    Documentation parts can be linked to other documentation parts.
    The set of relations is configurable.

.. item:: DESIGN-AUTO_REVERSE Automatic creation of reverse relations
    :depends_on: DESIGN-RELATIONS

    When a documentation part <A> is related to a documentation part <B> (forward relation), the reverse
    relation from documentation part <B> to documentation part <A> gets created automatically.

.. item:: DESIGN-LIST Listing documentation parts
    :depends_on: DESIGN-ITEMIZE

    A list of documentation parts matching a certain query can be retrieved.

.. item:: DESIGN-COVERAGE Calculation of coverage for relations between documentation parts
    :depends_on: DESIGN-RELATIONS

    The plugin is able to calculate the coverage for a certain type of relation between
    documentation parts.

.. item:: DESIGN-MATRIX Auto-generation of a traceability matrix
    :depends_on: DESIGN-RELATIONS

    The relations between documentation parts can be queried, and an overview matrix can be generated.

.. item:: DESIGN-TREE Auto-generation of a traceability tree
    :depends_on: DESIGN-RELATIONS

    The relations between documentation parts can be queried, and an overview tree can be generated.

.. item:: DESIGN-ATTRIBUTES_MATRIX Overview of attributes on documentation parts
    :depends_on: DESIGN-ATTRIBUTES

    An overview table of the attribute values for documentation parts can be generated.

.. item:: DESIGN-ATTRIBUTE_SORT Custom sorting of items' attributes
    :depends_on: DESIGN-ATTRIBUTES

    The plugin has a directive that allows configurability of the order of items' attributes.

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
