Sphinx traceability extension
=============================

.. image:: https://badge.fury.io/py/sphinxcontrib-traceability.svg
    :target: https://badge.fury.io/py/sphinxcontrib-traceability

Traceability extension for Sphinx documentation generator.

This extension adds directives and roles that serve to identify and
relate portions of Sphinx documents and create lists and traceability
matrices based on them.

It brings Sphinx the capability to work as a pretty decent
document-oriented requirements management tool. Outside of the
requirements domain, it can also be used for a wide range of
documentation needs. Interesting features such as code-documentation
traceability comes also out of the box.

Directives
----------

::

  .. item:: item_id [item_caption]
     :<<relationship>>:  other_item_id ...
     ...
  
     [item_content]

This directive identifies with ``item_id`` the portion of a document
contained by the directive itself (``item_content``). If no
``item_content`` is defined, the directive just marks with ``item_id``
the position of the document where it is defined. An optional text can
be defined with ``item_caption`` and it will be used in cross
references in combination with ``item_id``.

The extension also checks for uniqueness of item identifiers through
all files of a Sphinx project, in a similar way to standard Sphinx
references.

The directive allows multiple ``:<<relationship>>:`` options that can
set a list of item identifiers (space separated) the item traces
to. The name of the option itself indicates the type of the
relationship. For example::

  .. item:: SW_REQ_001 
     :addresses: SYS_REQ_001 SYS_REQ_002
     :tested_by: SW_TEST_005
     :allocated_to: SW_CSU_004
     ...
   
There is a predefined set of relationship names that can be used (the
most typical in the systems / software engineering world). If no
specific relationship type is to be set, just the generic ``:trace:``
relationship name can be used.

A configuration variable, ``traceability_relationships``, can be used to
extend and customize the set of available relationships. A configuration
variable, ``traceability_relationship_to_string``, needs to be defined in
order to translate the relationship tags to readable text. See
`Configuration`_ for details.

::

  .. item-list:: title
     :filter: regexp

This directive generates in place a list of items. A regular
expression can be set with option ``:filter:``, so that only items
whose identifier matches the expression are written in the list.

::

  .. item-matrix:: title
     :source: regexp
     :target: regexp
     :type: <<relationship>> ...
 
This directive generates in place a traceability matrix of item
cross-references. ``:source:`` and ``:target:`` options can be used to
filter matrix contents. Also content can be filtered based on
traceability relationships.


Roles
-----

Whenever an item needs to be referenced in documentation, it can be
done with the ``:item:`` role. This item works the same way as any
other Sphinx cross-reference role. By default, item identifier (or
caption, if existing) shall be used in generated link text, but it can
be overwritten with ``:role:`Text <target>``` Sphinx syntax.


Automatic reverse relationships
-------------------------------

When setting a relationship from one item to another, this extension
always considers the reverse relationship and sets it automatically
from the latter to the former.

To do it, the internal relationship dictionary will always require
a name for the reverse relationship. For bidirectional relationships,
the same name shall be used. Examples:

- depends_on: impacts_on
- parent: child
- sibling: sibling
- trace: backtrace

This is a very effective way to make traceability matrices flexible
and easy, as often matrices are requested in both directions. A
traceability matrix from source A to target B according a relationship
will have its automatic reverse matrix form B to A using its reverse
relationship.

External relations
------------------

The plugin supports defining relationships to external tools. The default
configuration holds an example ``ext_toolname`` relationship, with no
reverse relationship. Using this directive, one can link to other documents.
The plugin will insert a http reference, which can be configured through the
``traceability_external_relationship_to_url`` configuration variable. External
relationships are defined to have a 'ext_' prefix. As the generated http
reference can contain multiple fields per reference, the fields are seperated
by a semicolon. See `Configuration`_ for details.

Configuration
-------------

``traceability_relationships`` configuration variable follows the rules
above. It is a dictionary with relationship/reverse pairs.

This is the set of predefined relationships (mostly related with
standard UML relationships):

- fulfills: fulfilled_by
- depends_on: impacts_on
- implements: implemented_by
- realizes: realized_by
- validates: validated_by
- trace: backtrace (this is kept mainly for backwards compatibility)
- ext_toolname: None (external relationships should not have a reverse
  relationship)

``traceability_relationship_to_string`` configuration variable is needed
in order to translate the relationship tags to readable format.

By default an item is rendered as an admonition containing the id and the
given caption. The ``traceability_render_relationship_per_item`` configuration
variable allows to print a list of relationships to other items on every
rendered item.

In `External relations`_ the linking to external http pages is explained. The
``traceability_external_relationship_to_url`` translates a relationship to
a url. Use field1, field2, etc for indicating where which field of the target
id should be put.

Examples
--------

There is an `examples` folder with some Sphinx projects you can run.
