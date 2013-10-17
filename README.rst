Sphinx traceability extension
=============================

Traceability extension for Sphinx documentation generator.

This extension adds directives and roles that serve to identify and
relate portions of Sphinx documents and create lists and traceability
matrices based on them.

It brings Sphinx the capability to be used as a pretty decent
document-oriented requirements management tool. Outside of the
requirements domain, it can be also used for a wide range of
documentation needs. Interesting features such as code-documentation
traceability comes also out of the box.

Directives
----------

::

  .. item:: item_id [item_caption]
     :trace: [<<stereotype>>] other_item_id ...

     [item_content]

This directive identifies with `item_id` the portion of a document
contained by the directive itself (`item_content`). If no
`item_content` is defined, the directive just marks with `item_id` the
position of the document where it is defined. An optional text can be
defined with `item_caption` and it will be used in cross references
instead of `item_id`.

The extension also checks for uniqueness of item identifiers through
all files of a Sphinx project, in a similar way to standard Sphinx
references.

The `:trace:` option can set a list of item identifiers (space
separated) the item traces to. Optional stereotypes can be set
with the typical UML notation simply putting them in the list, before
the items to which the stereotype applies.

::

  .. itemlist:: title
     :filter: regexp

This directive generates in place a list of items. A regular
expression can be set with option `:filter:`, so that only items
whose identifier matches the expression are written in the list.

::

  .. item_matrix:: title
     :target: regexp
     :source: regexp
     :type: <<stereotype>> ...
 
This directive generates in place a traceability matrix of item
cross-references. `:target:` and `:source:` options can be used to
filter matrix contents. Also content can be filtered based on
traceability relationships stereotypes.


Roles
-----

Whenever an item needs to be referenced in documentation, it can be
done with the `:item:` role. This item works the same way as any other
Sphinx cross-reference role. By default, item identifier (or caption,
if existing) shall be used in generated link text, but it can be
overwritten with `:role:\`Text <target>\`` Sphinx syntax.


Example
-------

There is an `examples` folder with some Sphinx projects you can run.
