.. _traceability_config:

=============
Configuration
=============

The *conf.py* file contains the documentation configuration for your project. This file needs to be equipped in order
to configure the traceability plugin.

First the plugin needs to be enabled in the *extensions* variable:

.. code-block:: bash

    extensions = [
        'mlx.traceability',
        ...
    ]

Second the path to the static javascript assets needs to be added to the sphinx ``html_static_path``
variable.

.. code-block:: bash

    import os
    import mlx.traceability

    html_static_path = [os.path.join(os.path.dirname(mlx.traceability.__file__), 'assets')]

.. _traceability_config_attributes:

----------------
Valid attributes
----------------

Python variable *traceability_attributes* can be defined in order to override the
default configuration of the traceability plugin.
It is a *set* of attribute pairs: the *key* is the name of the attribute (can only be lowercase),
while the *value* holds the regular expression to which the attribute-value should comply.

Example of attributes and their regular expression:

.. code-block:: python

    traceability_attributes = {
        'value': '^.*$',
        'asil': '^(QM|[ABCD])$',
    }

.. _traceability_config_attribute2string:

-----------------------------
Stringification of attributes
-----------------------------

Python variable *traceability_attribute_to_string* can be defined in order to override the
default configuration of the traceability plugin.
It is a *set* of attribute stringifications: the *key* is the name of the attribute, while
the *value* holds the string representation (as to be rendered in html) of the attribute name.

Example of attribute stringification:

.. code-block:: python

    traceability_relationship_to_string = {
        'value': 'Value',
        'asil': 'ASIL',
    }

.. _traceability_config_relations:

-------------------
Valid relationships
-------------------

Python variable *traceability_relationsips* can be defined in order to override the
default configuration of the traceability plugin.
It is a *set* of relationship pairs: the *key* is the name of the forward relationship, while the *value* holds the
name of the corresponding reverse relationship. Both can only be lowercase.

Relationships with prefix *ext_* are treated in a different way: they are handled as external relationships and don't
need a reverse relationship.

Example of internal and external relationship pairs:

.. code-block:: python

    traceability_relationships = {
        'validates': 'validated_by',
        'ext_polarion_reference': ''
    }

.. _traceability_config_relation2string:

--------------------------------
Stringification of relationships
--------------------------------

Python variable *traceability_relationship_to_string* can be defined in order to override the
default configuration of the traceability plugin.
It is a *set* of relationship stringifications: the *key* is the name of the (forward or reverse) relationship, while
the *value* holds the string representation (as to be rendered in html) of the relationship.

Example of internal and external relationship stringification:

.. code-block:: python

    traceability_relationship_to_string = {
        'validates': 'Validates',
        'validated_by': 'Validated by',
        'ext_polarion_reference': 'Polarion reference'
    }

.. _traceability_config_ext2url:

----------------------------------------
External relationship to URL translation
----------------------------------------

External relationships need to be translated to URL's while rendering. For each defined external relationship,
an entry in the Python *set* named *traceability_external_relationship_to_url* is needed. The URL generation
is templated using the *fieldx* keyword, where x is a number incrementing from 1 onwards for each value in the URL
that needs to be replaced.

Example configuration of URL translation of external relationship using 2 fields:

.. code-block:: python

    traceability_external_relationship_to_url = {
        'ext_polarion_reference': 'https://melexis.polarion.com/polarion/#/project/field1/workitem?id=field2',
    }

.. _traceability_config_render_relations:

---------------------------------------------------
Rendering of relationships per documentation object
---------------------------------------------------

When rendering the documentation objects, the user has the option to include/exclude the rendering of the
relationships to other documentation objects. This can be done through the Python variable
*traceability_render_relationship_per_item* which is *boolean*: a value of ``True`` will enable rendering
of relationships per documentation object, while a value of ``False`` will disable this rendering.

Example configuration of enable rendering relationships per item:

.. code-block:: python

    traceability_render_relationship_per_item = True

------------------------------------------------
Rendering of attributes per documentation object
------------------------------------------------

The rendering of attributes of documentation objects can be controlled through the *boolean* variable
*traceability_render_attributes_per_item*: rendering of attributes is enabled by setting it to ``True`` (the default)
while a value of ``False`` will prevent the attribute list from being rendered.

Example configuration of disabling per item attribute rendering:

.. code-block:: python

    traceability_render_attributes_per_item = False

-------------------------------------------------------------------------------------
Ability to collapse the list of relationships and attributes per documentation object
-------------------------------------------------------------------------------------

A button is added to each documentation object that has rendered relationships and/or attributes to be able to show and
hide these traceability links. The *boolean* configuration variable *traceability_collapse_links* allows selecting
between hiding and showing the list of links for all items on page load: setting its value to ``True`` results in the
list of links being hidden (collapsed) on page load, while a value of ``False`` results in the list being shown
(uncollapsed)(the default).

Example configuration of hiding the traceability links on page load:

.. code-block:: python

    traceability_collapse_links = True

.. _traceability_config_no_captions:

-----------
No captions
-----------

By default, the output will contain hyperlinks to all related items. By default, the caption for the target
item is displayed for each of the related items. The captions can be omitted at configuration level (see
this section) and at directive level (see e.g. :ref:`traceability_usage_item_matrix`).

No captions for item
====================

Example configuration of disabling the rendering of captions on item:

.. code-block:: python

    traceability_item_no_captions = True

No captions for item-list
=========================

Example configuration of disabling the rendering of captions on item-list:

.. code-block:: python

    traceability_list_no_captions = True

No captions for item-matrix
===========================

Example configuration of disabling the rendering of captions on item-matrix:

.. code-block:: python

    traceability_matrix_no_captions = True

No captions for item-attributes-matrix
======================================

Example configuration of disabling the rendering of captions on item-attributes-matrix:

.. code-block:: python

    traceability_attributes_matrix_no_captions = True

No captions for item-tree
=========================

Example configuration of disabling the rendering of captions on item-tree:

.. code-block:: python

    traceability_tree_no_captions = True

.. _traceability_config_export:

------
Export
------

The plugin allows exporting the documentation items.

Export to JSON
==============

As a preliminary test feature, the plugin allows to export the documentation items to a JSON database. The feature
can be enabled by setting the configuration to your JSON-file to export to. Note, the JSON-file is overwritten
(not appended) on every build of the documentation.

.. code-block:: python

    traceability_json_export_path = '/path/to/your/database.json'

As a preliminary feature, the database only contains per documentation item:

- the id,
- the caption,
- the document name and line number,
- the relations to other items.

The actual content (RST content with images, formulas, etc) of the item is currently not stored.

.. note:: Requires sphinx >= 1.6.0

.. _traceability_config_callback:

----------------------------
Callback per item (advanced)
----------------------------

The plugin allows parsing and modifying documentation objects 'behind the scenes' using a callback. The callback
has this prototype:

.. code-block:: python

    def traceability_my_callback_per_item(name, all_items):
        '''
        Custom callback on items

        :param name: Name (id) of the item currently being parsed
        :param all_items: Set of all items that are parsed so far
        '''
        return

The callback is executed while parsing the documentation item from your rst-file. Note that not all items are
available at the time this callback executes, the *all_items* parameter is a growing set of documentation objects.

Example of no callback per item:

.. code-block:: python

    traceability_callback_per_item = None

.. _traceability_config_link_colors:

------------------------------
Custom colors for linked items
------------------------------

The plugin allows customization of the colors of traceable items in order to easily recognize the type of item which is
linked to. A dictionary in the configuration file defines the regexp, which is used to match item IDs, as key and a
tuple of 1-3 color defining strings as value. The first color is used for the default hyperlink state, the second color
is used for the hover and active states, and the third color is used to override the default color of the visted state.
Leaving a color empty results in the use of the default html style. The top regexp has the highest priority. To support
Python versions lower than 3.7, we use an :code:`OrderedDict` to have a deterministic order for prioritizing regexes.

.. code-block:: python

    traceability_hyperlink_colors = OrderedDict([
        (r'^(RQT|r[\d]+', ('#7F00FF', '#b369ff')),
        (r'^[IU]TEST_REP', ('rgba(255, 0, 0, 1)', 'rgba(255, 0, 0, 0.7)', 'rgb(200, 0, 0)')),
        (r'^[IU]TEST', ('goldenrod', 'hsl(43, 62%, 58%)', 'darkgoldenrod')),
        (r'^SYS_', ('', 'springgreen', '')),
        (r'^SRS_', ('', 'orange', '')),
    ])

.. _traceability_default_config:

--------------
Default config
--------------

The plugin itself holds a default config that can be used for any traceability documenting project:

.. code-block:: python

    traceability_callback_per_item = None
    traceability_attributes = {
        'value': '^.*$',
        'asil': '^(QM|[ABCD])$',
        'aspice': '^[123]$',
        'status': '^.*$',
        'result': '(?i)^(pass|fail|error)$'
    }
    traceability_attribute_to_string = {
        'value': 'Value',
        'asil': 'ASIL',
        'aspice': 'ASPICE',
        'status': 'Status'
    }
    traceability_relationships = {
        'fulfills': 'fulfilled_by',
        'depends_on': 'impacts_on',
        'implements': 'implemented_by',
        'realizes': 'realized_by',
        'validates': 'validated_by',
        'trace': 'backtrace',
        'ext_toolname': ''
    }
    traceability_relationship_to_string = {
        'fulfills': 'Fulfills',
        'fulfilled_by': 'Fulfilled by',
        'depends_on': 'Depends on',
        'impacts_on': 'Impacts on',
        'implements': 'Implements',
        'implemented_by': 'Implemented by',
        'realizes': 'Realizes',
        'realized_by': 'Realized by',
        'validates': 'Validates',
        'validated_by': 'Validated by',
        'trace': 'Traces',
        'backtrace': 'Back traces',
        'ext_toolname': 'Reference to toolname'
    }
    traceability_external_relationship_to_url = {
        'ext_toolname': 'http://toolname.company.com/field1/workitem?field2'
    }
    traceability_render_relationship_per_item = False

This default configuration, which is built into the plugin, can be overridden through the conf.py of your project.

For Melexis.SWCC silicon projects, the SWCC process holds a default configuration in the *config/traceability_config.py*
file. For each of the above configuration variables, the default configuration file holds a variable with *swcc_*
prefix. Taking the default configuration is as easy as assiging the above configuration value with the *swcc_* variable.
Overriding a configuration is as easy as assigning your own values to a configuration value.

Example of accepting default configuration for relationships, while disabling (override) rendering of relationships
per documentation object:

.. code-block:: python

    sys.path.insert(0, os.path.abspath('<path_to_process_submodule>/config'))

    from traceability_config import swcc_traceability_attributes
    from traceability_config import swcc_traceability_relationships
    from traceability_config import swcc_traceability_relationship_to_string

    traceability_attributes = swcc_traceability_attributes
    traceability_relationships = swcc_traceability_relationships
    traceability_relationship_to_string = swcc_traceability_relationship_to_string
    traceability_render_relationship_per_item = False
