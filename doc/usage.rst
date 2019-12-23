.. _traceability_usage:

=====
Usage
=====

.. contents:: `Contents`
    :depth: 3
    :local:

.. _required_sphinx_options:

-----------------------
Required sphinx options
-----------------------

By default, sphinx (*sphinx-build*) performs an incremental build: it only parses the changed files and generates
new output for changed files. As this plugin generates automatic reverse relations, the incremental build option
of sphinx needs to be disabled. This can be done using the *-E* option:

.. code-block:: bash

    sphinx-build -E <other_options>

:Rationale: The plugin allows linking documentation items through relations. If a forward relation from *item-A*
            (in *document-a.rst*) to *item-B* (in *document-b.rst*) is created, the reverse relations from
            *item-B* to *item-A* is automatically created. With incremental builds, documents only get re-generated
            when they are changed. This means the automatic reverse relation cannot be created if that *document-B*
            was not touched.
            By disabling incremental builds, it is made sure every document is updated (with automatic reverse
            relations) on every re-build.

The plugin assumes incremental builds are disabled, as this makes the implementation of the plugin much easier.

.. _traceability_usage_item:

----------------------------
Defining documentation items
----------------------------

Documentation items can be defined using the *item* directive, specifying:

- the name (id) of the documentation item
- caption or short description of the documentation item
- attributes for the documentation item
- internal/external relationships to other documentation items (details in next paragraph)
- content of documentation item including any rst content including text, images, formulas, code-blocks, etc.

.. code-block:: rest

    .. item:: SWRQT-MY_FIRST_REQUIREMENT Caption of my first requirement
        :value: 400
        :status: Approved
        :validated_by: ITEST-MY_FIRST_INTEGRATION_TEST
        :ext_polarion_reference: project_x:workitem_y
        :nocaptions:

        According to the Polarion reference, the software **shall** implement my first requirement.

Attributes can be added to the item, using the `configured attribute keys <traceability_default_config>`_
(e.g. *value* in the above example). The content of the attribute is treated as a single string and should
match the regular expression in configuration.

The relations to other documentation items can be specified as:

- a space-separated list of item ID's, or
- items can be linked to on a newline (tabulated)

.. code-block:: rest

    .. item:: SWRQT-MY_FIRST_REQUIREMENT Caption of my first requirement
        :validated_by:
            ITEST-MY_FIRST_INTEGRATION_TEST
            ITEST-MY_SECOND_INTEGRATION_TEST

The output will contain hyperlinks to all related items. By default, the caption for the target item is displayed for
each of these related items. With the option *nocaptions* these captions can be omitted.

.. _adding_relations:

------------------------------------------------
Adding relations outside of the item definitions
------------------------------------------------

In some cases, it's useful to add relations outside of the definition of the items
involved. In that case, you can use the ``item-link`` directive as follows:

.. code-block:: rest

    .. item-link::
        :sources: RQT1 RQT2
        :targets: TST3 TST4 TST5
        :type: validates

This directive has no representation in the documentation build output. It will
just add an additional relationship to the items mentioned in ``sources`` and
``targets``.

--------------------------------
Adding description to attributes
--------------------------------

Section :ref:`traceability_config_attributes` explain how attributes can be added to the configuration. It is possible
to add content to the attributes. A detailed description can be added to an attribute definition:

- The name (id) of the attribute needs to match the configured attribute. This name is not case sensitive.
- Caption or short description of the attribute.
- Content of attribute including any rst content including text, images, formulas, code-blocks, etc.

.. code-block:: rest

    .. item-attribute:: status The status of a requirement

        The status of the requirement explains whether it is *draft*, *under-review*, *approved* or *invalid*.

.. _traceability_usage_item_linking:

----------------------------------
Manual link to documentation items
----------------------------------

Manual links in RST documentation to any of the documentation items is possible using the *:item:* role:

.. code-block:: rest

    For validating the :item:`SWRQT-MY_FIRST_REQUIREMENT`, we plan to use setup x in the y configuration.

.. _traceability_usage_item_list:

--------------------------------
Flat list of documentation items
--------------------------------

A flat list of documentation items can be generated using a Python regular expression filter:

.. code-block:: rest

    .. item-list:: All software requirements
        :filter: SWRQT
        :status: Appr
        :nocaptions:

where *SWRQT* (*filter* argument) can be replaced by any Python regular expression. Documentation items matching
their ID to the given regular expression end up in the list.

where *status* can be replaced by any configured attribute, and *Appr* can be replaced by any Python regular
expression. Documentation items where the *status* attribute matches the given regular expression end up in the list.

By default, the caption for every item in the list is shown. By providing the *nocaptions* flag, the
caption can be omitted. This gives a smaller list, but also less details.

.. _traceability_usage_item_attributes_matrix:

---------------------------------------------
Matrix with attributes of documentation items
---------------------------------------------

A matrix listing the attributes of documentation items can be generated using:

.. code-block:: rest

    .. item-attributes-matrix:: Attributes for requirements
        :filter: SWRQT
        :status: Appr
        :attributes: status
        :sort: status
        :reverse:
        :transpose:
        :nocaptions:

where the *filter* argument can be replaced by any Python regular expression. Documentation items matching
their ID to the given regular expression end up in the list.

where *status* can be replaced by any configured attribute, and *Appr* can be replaced by any Python regular
expression. Documentation items where the *status* attribute matches the given regular expression end up in the list.

where *attributes* argument is a space-separated list of attributes that should be matched in the matrix.

Above arguments can be avoided, or left empty, in which case the table will contain all attributes for all
documentation items.

Documentation items matching their ID to the given *filter* regular expression end up as rows in the generated table.
The matching attribute values end up as columns in the generated table. Documentation items
that don't have a value for a certain attribute will have an empty cell at the corresponding location.

By default, the caption for every item in the table is shown. By providing the *nocaptions* flag, the
caption can be omitted. This gives a smaller table, but also less details.

By default, items are sorted naturally based on their name. With the *sort* argument it is possible to sort on one
or more attribute values alphabetically. When providing multiple attributes to sort on, the attribute keys are
space-separated. With the *reverse* argument, the sorting is reversed.

By default, the attribute names are listed the header row and every item takes up a row. Depending on the number of
items and attributes it could be better to transpose the generated matrix (swap columns for row) by providing the
*transpose* flag.

Optionally, the *class* attribute can be specified to customize table output, especially useful when rendering to
LaTeX. Normally the *longtable* class is used when the number of rows is greater than 30 which allows long tables to
span multiple pages. By setting *class* to *longtable* manually, you can force the use of this environment.

.. _traceability_usage_item_matrix:

------------------------------------------
Traceability matrix of documentation items
------------------------------------------

A traceability matrix of documentation items can be generated using:

.. code-block:: rest

    .. item-matrix:: Requirements to test case description traceability
        :source: SWRQT
        :target: [IU]TEST
        :status: Appr
        :sourcetitle: Software requirements
        :targettitle: Integration and unit test cases
        :type: validated_by
        :group: bottom
        :nocaptions:
        :stats:


where the *source* and *target* arguments can be replaced by any Python regular expression.

where *status* can be replaced by any configured attribute, and *Appr* can be replaced by any Python regular
expression. Only documentation items where the *status* attribute matches the given regular expression end up in
the *source* part of the matrix. The attribute value is **not** used as a filter on the *target* part.

The *type* argument
is a space-separated list of relationships that should be matched in the matrix. The *sourcetitle* and *targettitle*
arguments are the titles of the columns in the generated matrix.

Documentation items matching their ID to the given *source* regular expression end up in the left column of the
generated table. Documentation items matching their ID to the given *target* regular expression with a matching
relationship (see *type* argument) will end up in the right column of the generated table.

By default, the caption for every item in the table is shown. By providing the *nocaptions* flag, the
caption can be omitted. This gives a smaller table, but also less details.

By providing the *stats* flag, some statistics (coverage percentage) are calculated and displayed above the
matrix. The plugin counts the number of items having a target item in the target-column (=covered or allocated),
and the number of items having no target in the target-column (=not covered or allocated). And calculates a
coverage/allocation percentage from these counts. If the *stats* flag is not given, this percentage is not
displayed.

The *group* argument can be used to group source items that don't have any target items. You can explicitly specify to
have them grouped at the *top* or *bottom* of the matrix. If no argument is given, they will be grouped at the top.

Optionally, the *class* attribute can be specified to customize table output, especially useful when rendering to
LaTeX. Normally the *longtable* class is used when the number of rows is greater than 30 which allows long tables to
span multiple pages. By setting *class* to *longtable* manually, you can force the use of this environment.

.. _traceability_usage_2d_matrix:

--------------------------------
2D-matrix of documentation items
--------------------------------

A 2D-matrix of documentation items can be generated using:

.. code-block:: rest

    .. item-2d-matrix:: Requirements to test case description traceability
        :source: SWRQT
        :target: [IU]TEST
        :status: Appr
        :hit: x
        :miss:
        :type: validated_by

where the *source* and *target* arguments can be replaced by any Python regular expression.

where *status* can be replaced by any configured attribute, and *Appr* can be replaced by any Python regular
expression. Only documentation items where the *status* attribute matches the given regular expression end up in
the *source* part of the matrix. The attribute value is **not** used as a filter on the *target* part.

The *type* argument is a space-separated list of relationships that should be matched in the matrix.

Documentation items matching their ID to the given *source* regular expression end up as columns of the
generated table. Documentation items matching their ID to the given *target* regular expression end up as
rows of the generated table. Where source and target items have a matching relationship (see *type* argument)
an 'x' will be placed in the cell at co-ordinates of source/target.

Captions for items in the 2D table are never shown, as it would give a too heavy loaded table.

Optionally, the *class* attribute can be specified to customize table output, especially useful when rendering to
LaTeX. Normally the *longtable* class is used when the number of rows is greater than 30 which allows long tables to
span multiple pages. By setting *class* to *longtable* manually, you can force the use of this environment.

.. _traceability_usage_item_tree:

-----------------------------
Documentation items tree-view
-----------------------------

Note: this feature is not supported when building for latex/pdf.

A tree-view of documentation items can be generated using:

.. code-block:: rest

    .. item-tree:: Requirements tree view
        :top: SWRQT
        :top_relation_filter: depends_on
        :status: Appr
        :type: impacts_on validated_by
        :nocaptions:

where the *top* argument can be replaced by any Python regular expression. The *top_relation_filter* and *type*
arguments are space-separated lists of relationships.

The directive generates an expandable tree of links to documentation items. A nested bullet list is generated
with, at the top level, the top level documentation items. These are the ones matching their ID to the *top*
regular expression and not having any relation of *top_relation_filter* kind to a documentation item matching the same
*top* regular expression against its ID.

The *status* can be replaced by any configured attribute, and *Appr* can be replaced by any Python regular
expression. Only documentation items where the *status* attribute matches the given regular expression end up in
the tree.

Going deeper down this nested bullet list, the item's relationships are checked: if there is a *type*
relationship (*type* is a space-separated list of relationships), it gets added as a one-level-deeper item in
the nested bullet list. This action is repeated recursively.

.. warning::

    The *type* is a list of relationships, which cannot hold the forward and reverse relationship of a pair.
    This would give endless repetition of the same nesting and endless recursion in Python. The plugin
    checks the *item-tree* directives for this mistake!

By default, the caption for every item in the tree is shown. By providing the *nocaptions* flag, the
caption can be omitted. This gives a smaller tree, but also less details.

.. _traceability_usage_piechart:

--------------------------------
Pie chart of documentation items
--------------------------------

A pie chart of documentation items can be generated using:

.. code-block:: rest

    .. item-piechart:: Test coverage of requirements with report results
        :id_set: RQT TEST TEST_REP
        :label_set: uncovered, covered, executed
        :result: error, fail, pass

where the *id_set* arguments can be replaced by any Python regular expression. The *label_set* and *result* arguments
are comma-separated lists.

The *id_set* is a list of item IDs with at least two and at most three item IDs. The first item ID is the source, the
second item ID is the target, and the optional third item ID is the target of the second. Adding a third item ID splits
up the items with an existing relationship between the first and second ID.

The optional *label_set* holds the string labels for the pie chart. For source items without a relationship to a target
item, the first label is used. For those with a relationship, but without a relationship between the second and third
ID, the second label is used. The third label is used for items with both relationships covered. This attribute is
optional. The labels in the example are the default values.

The optional *result* can be replaced by any configured attribute of the third item ID. Its arguments are possible
values of this attribute, ordered in priority from high to low. Using this option splits up the slice with the third
label. In this example an RQT item with multiple TEST items, one with a *fail* and others a *pass* as *result* value in
the TEST_REP item, will be added to the *fail* slice of the pie chart.

.. _traceability_checklist:

-----------------------------------------------------------
Defining items with a custom checklist attribute (advanced)
-----------------------------------------------------------

The plugin can add an additional attribute to a traceability item if its item ID exists in a checklist inside the
description of a merge/pull request or its item ID is used in a *checklist-result* directive. Documentation items can be
linked to a checklist by defining them with the *checklist-item* directive. This custom directive inherits all
functionality of the regular *item* directive.

.. code-block:: rest

    .. checklist-item:: PLAN-UNIT_TESTS Have you added unit tests for regression detection?


Setting the additional attribute's value
========================================

There are two different ways to set the value of the additional attribute. They can be combined, and the first has
priority over the second:

1. Use of *checkbox-result* directive

The checkboxes can be checked/unchecked from RST as well by using the *checkbox-result* directive. The item ID should be
of a checklist item and is expected to be present in a configured merge/pull request description. The caption should be
one of two configured values in *attribute_values*.

.. code-block:: rest

    .. checkbox-result:: QUE-UNIT_TESTS yes

2. Querying GitLab/GitHub

A query is sent to the GitLab/GitHub API to retrieve the status of every checkbox in the description of the configured
merge/pull request. The traceability item's ID is expected to follow the checkbox directly.
Example of a valid checklist in Markdown:

.. code-block:: rest

    - [x] PLAN-UNIT_TESTS Have you added unit tests for regression detection?
    - [ ] PLAN-PACKAGE_TEST Have you tested the package?

Configuration
=============

The configuration of this feature is stored in the configuration variable *traceability_checklist*. Only the
*attribute_*-keys are mandatory to use the *checklist-item* directive. The other configuration variables are only used
for querying GitLab/GitHub.

.. code-block:: python

    traceability_checklist = {
        'attribute_name': 'your_attribute_name',
        'attribute_to_str': 'your_attribute_to_string'),
        'attribute_values': 'your_attribute_values',  # two values, comma-separated
        'private_token': 'your_private_token',  # optional, depending on accessibility
        'api_host_name': 'https://api.github.com' or 'https://gitlab.example.com/api/v4',
        'project_id': 'the_owner/your_repo' or 'your_project_id',
        'merge_request_id': 'your_merge_request_id(s)'),  # comma-separated if more than one
        'checklist_item_regex': 'your_item_id_regex',  # optional, the default is r"\S+"
    }

If the *checklist_item_regex* is configured, a warning is reported for each item ID that matches it and is not defined
with the *checklist-item* directive.

Configuration via .env file
---------------------------
In our *conf.py* the variables are looked for in the environment first, e.g. in a ``.env`` file (by using the Python
*decouple* module).

.. code-block:: bash

    # copy example .env to your .env
    cp doc/.env.example .env

    # add env variables by adjusting the template values in .env

Common variables
----------------
- *ATTRIBUTE_NAME* is the identifier of the attribute to be added, e.g. *checked*.
- *ATTRIBUTE_TO_STRING* is the string representation (as to be rendered in html) of the attribute name, e.g. *Answer*.
- *ATTRIBUTE_VALUES* are two comma-separated attribute values, e.g. *yes,no*. The first value is used when the checkbox is checked and the second value when unchecked.

Query-specific variables
------------------------
GitLab
``````
- *PRIVATE_TOKEN* is your personal access token that has API access.
- *API_HOST_NAME* is the host name of the API, e.g. *https://gitlab.example.com/api/v4*
- *PROJECT_ID* is the ID of the project.
- *MERGE_REQUEST_ID* is the internal ID of the merge request.

GitHub
``````
- *PRIVATE_TOKEN* is not needed for public repositories. Otherwise, it must be a `personal access token`_ with the access to the targeted scope.
- *API_HOST_NAME* is the host name of the GitHub REST API v3: *https://api.github.com*
- *PROJECT_ID* defines the repository by specifying *owner* and *repo* separated by a forward slash, e.g. *melexis/sphinx-traceability-extension*.
- *MERGE_REQUEST_ID* is the pull request number.

.. _`personal access token`: https://github.blog/2013-05-16-personal-api-tokens/
