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
traceability come also out of the box.

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
references instead of ``item_id``.

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
extend and customize the set of available relationships. See
`Configuration`_ for details.

New directive names can be easily added in the configuration file with
the standard Sphinx function ``app.add_directive``. They will be equivalent
to ``item`` but have two big benefits:

- Better document readibility using meaningful names. For example, the 
  previous software requirement could be directly written as::
  
    .. requirement:: SW_REQ_001 
       :addresses: SYS_REQ_001 SYS_REQ_002
       :tested_by: SW_TEST_005
       :allocated_to: SW_CSU_004
       ...
     
- Custom templates can be defined for them. This adds a lot of flexibility.

See `Advanced configuration`_ for more details and example configuration
code.

::

  .. item-list::
     :filter: regexp

This directive generates in place a list of items. A regular
expression can be set with option ``:filter:``, so that only items
whose identifier matches the expression are written in the list.

::

  .. item-matrix:: title
     :source-title: source title
     :source: regexp
     :target-title: target title
     :target: regexp
     :type: <<relationship>> ...
 
This directive generates in place a traceability matrix of item
cross-references. ``:source:`` and ``:target:`` options can be used to
filter matrix contents. Also content can be filtered based on
traceability relationships. Optional titles can be set for the matrix
itself and for both columns (*"Source"* and *"Target"* are used by
default).


Roles
-----

Whenever an item needs to be referenced in documentation, it can be
done with the ``:item:`` role. This item works the same way as any
other Sphinx cross-reference role. By default, item identifier (or
caption, if existing) shall be used in generated link text, but it can
be overwritten with ``:role:`Text <target>``` Sphinx syntax.


More on relationships
---------------------

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

``traceability_data`` configuration variable can be used to add more
options to the item to represent internal data or attributes apart
from relationships. It is a dictionary with name/function pairs. It
follows exactly the same rules as the standard Sphinx and Docutils
``option_spec`` dictionary. Built-in or custom validation/ conversion
functions can be used. See Docutils' `Option Conversion Functions`_.

.. _Option Conversion Functions:
   https://docutils.sourceforge.io/docs/howto/rst-directives.html
   #option-conversion-functions


Advanced configuration
----------------------

In order to add new directive names, a ``setup`` function
should be added to the configuration file with one call to
``app.add_directive`` per directive. Example:

.. code:: python

  def setup(app):

      from traceability import ItemDirective
      app.add_directive('requirement', ItemDirective)
      app.add_directive('test-case', ItemDirective)
      ...


By default, items are written as term/definition tuples, but this is
fully customizable by defining ``traceability_item_template``
configuration variable.  It uses `Jinja2 templating language
<https://jinja.palletsprojects.com>`_.

The template can be customized for each different ``item`` based
directive names. Example:

.. code:: python

   traceability_item_template = """
       {% if type == 'requirement' %}
       :superscript:`[{{ id }}` {{ caption }}:
       {{ content }} :subscript:`{{ id }}]`
       {% else %}
       {{ id }}
       {%- if caption %}
           **{{ caption }}**
       {% endif %}
           {{ content|indent(4) }}
       {% endif %}
       """

Code above makes the ``requirement`` directive be shown as its caption
& content surrounded with  tags ``[<id>`` at the beginning and
``<id>]`` at the end. The rest will be generated as term/definition
tuples, optionally showing its caption.

As an aid for template creation, in verbose mode (putting
``SPHINXOPTS="-v"`` in the Makefile or after the make command) the
extension will print the content generated by the template for every
item.


Examples
--------

There is an `examples` folder with some Sphinx projects you can run.
