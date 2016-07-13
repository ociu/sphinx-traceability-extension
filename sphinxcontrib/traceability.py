# -*- coding: utf-8 -*-

from __future__ import print_function
from docutils import nodes
from sphinx.util.compat import Directive
from docutils.parsers.rst import directives
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.environment import NoUri
from jinja2 import Template
from textwrap import dedent
import re

# -----------------------------------------------------------------------------
# Declare new node types (based on others): item, item_list, item_matrix


class item(nodes.General, nodes.Element):
    pass


class item_list(nodes.General, nodes.Element):
    pass


class item_matrix(nodes.General, nodes.Element):
    pass


# -----------------------------------------------------------------------------
# Pending item cross reference node


class pending_item_xref(nodes.Inline, nodes.Element):
    """
    Node for item cross-references that cannot be resolved without
    complete information about all documents.

    """
    pass


# -----------------------------------------------------------------------------
# Directives


class ItemDirective(Directive):
    """
    Directive to declare items and their traceability relationships.

    Syntax::

      .. item:: item_id [item_caption]
         :<<relationship>>:  other_item_id ...
         ...

         [item_content]

    When run, for each item, two nodes will be returned:

    * A target node
    * A custom node generated from a template (by default: term & definition)

    Also ``traceability_all_items`` storage is filled with item information

    """
    # Required argument: id
    required_arguments = 1
    # Optional argument: caption (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options: the typical ones plus every relationship (and reverse)
    # defined in env.config.traceability_relationships
    option_spec = {'class': directives.class_option}
    # Content allowed
    has_content = True

    def run(self):
        env = self.state.document.settings.env
        caption = ''
        messages = []

        targetid = self.arguments[0]
        targetnode = nodes.target('', '', ids=[targetid])

        # Item caption is the text following the mandatory id argument.
        # Caption should be considered a line of text. Remove line breaks.
        if len(self.arguments) > 1:
            caption = self.arguments[1].replace('\n', ' ')

        # Store item info
        if targetid not in env.traceability_all_items:
            env.traceability_all_items[targetid] = {
                'id': targetid,
                'type': self.name,
                'class': self.options.get('class', []),
                'docname': env.docname,
                'lineno': self.lineno,
                'target': targetnode,
                'caption': caption,
                'content': '\n'.join(self.content)
            }
            # Add relationships to item. All relationship data is a string of
            # item ids separated by space. It is splitted in a list of item ids
            for rel in list(env.relationships.keys()):
                if rel in self.options:
                    env.traceability_all_items[targetid][rel] = \
                        self.options[rel].split()
                else:
                    env.traceability_all_items[targetid][rel] = []

        else:
            # Duplicate items not allowed. Duplicate will even not be shown
            messages = [self.state.document.reporter.error(
                'Traceability: duplicated item %s' % targetid,
                line=self.lineno)]

        # Render template
        template = Template(dedent(env.config.traceability_item_template))
        self.state_machine.insert_input(
            template.render(**env.traceability_all_items[targetid]).split('\n'),
            self.state_machine.document.attributes['source'])

        return [targetnode] + messages


class ItemListDirective(Directive):
    """
    Directive to generate a list of items.

    Syntax::

      .. item-list:: title
         :filter: regexp

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'filter': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        item_list_node = item_list('')

        # Process title (optional argument)
        if len(self.arguments) > 0:
            item_list_node['title'] = self.arguments[0]

        # Process ``filter`` option
        if 'filter' in self.options:
            item_list_node['filter'] = self.options['filter']
        else:
            item_list_node['filter'] = ''

        return [item_list_node]


class ItemMatrixDirective(Directive):
    """
    Directive to generate a matrix of item cross-references, based on
    a given set of relationship types.

    Syntax::

      .. item-matrix:: title
         :target: regexp
         :source: regexp
         :type: <<relationship>> ...

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'target': directives.unchanged,
                   'source': directives.unchanged,
                   'type': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        item_matrix_node = item_matrix('')

        # Process title (optional argument)
        if len(self.arguments) > 0:
            item_matrix_node['title'] = self.arguments[0]

        # Process ``target`` & ``source`` options
        for option in ('target', 'source'):
            if option in self.options:
                item_matrix_node[option] = self.options[option]
            else:
                item_matrix_node[option] = ''

        # Process ``type`` option, given as a string with relationship types
        # separated by space. It is converted to a list.
        if 'type' in self.options:
            item_matrix_node['type'] = self.options['type'].split()
        else:
            item_matrix_node['type'] = []

        return [item_matrix_node]


# -----------------------------------------------------------------------------
# Event handlers

def purge_items(app, env, docname):
    """
    Clean, if existing, ``item`` entries in ``traceability_all_items``
    environment variable, for all the source docs being purged.

    This function should be triggered upon ``env-purge-doc`` event.

    """
    keys = list(env.traceability_all_items.keys())
    for key in keys:
        if env.traceability_all_items[key]['docname'] == docname:
            del env.traceability_all_items[key]


def process_item_nodes(app, doctree, fromdocname):
    """
    This function should be triggered upon ``doctree-resolved event``

    Replace all item_list nodes with a list of the collected items.
    Augment each item with a backlink to the original location.

    """
    env = app.builder.env

    all_items = sorted(env.traceability_all_items, key=naturalsortkey)

    # Item matrix:
    # Create table with related items, printing their target references.
    # Only source and target items matching respective regexp shall be included
    for node in doctree.traverse(item_matrix):
        table = nodes.table()
        tgroup = nodes.tgroup()
        left_colspec = nodes.colspec(colwidth=5)
        right_colspec = nodes.colspec(colwidth=5)
        tgroup += [left_colspec, right_colspec]
        tgroup += nodes.thead('', nodes.row(
            '',
            nodes.entry('', nodes.paragraph('', 'Source')),
            nodes.entry('', nodes.paragraph('', 'Target'))))
        tbody = nodes.tbody()
        tgroup += tbody
        table += tgroup

        for source_item in all_items:
            if re.match(node['source'], source_item):
                row = nodes.row()
                left = nodes.entry()
                left += make_item_ref(app, env, fromdocname,
                                      env.traceability_all_items[source_item])
                right = nodes.entry()
                for target_item in all_items:
                    if (re.match(node['target'], target_item) and
                            are_related(
                                env, source_item, target_item, node['type'])):
                        right += make_item_ref(
                            app, env, fromdocname,
                            env.traceability_all_items[target_item])
                row += left
                row += right
                tbody += row

        node.replace_self(table)

    # Item list:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(item_list):
        content = nodes.bullet_list()
        for item in all_items:
            if re.match(node['filter'], item):
                bullet_list_item = nodes.list_item()
                paragraph = nodes.paragraph()
                paragraph.append(
                    make_item_ref(app, env, fromdocname,
                                  env.traceability_all_items[item]))
                bullet_list_item.append(paragraph)
                content.append(bullet_list_item)

        node.replace_self(content)

    # Resolve item cross references (from ``item`` role)
    for node in doctree.traverse(pending_item_xref):
        # Create a dummy reference to be used if target reference fails
        new_node = make_refnode(app.builder,
                                fromdocname,
                                fromdocname,
                                'ITEM_NOT_FOUND',
                                node[0].deepcopy(),
                                node['reftarget'] + '??')
        # If target exists, try to create the reference
        if node['reftarget'] in env.traceability_all_items:
            item_info = env.traceability_all_items[node['reftarget']]
            try:
                new_node = make_refnode(app.builder,
                                        fromdocname,
                                        item_info['docname'],
                                        item_info['target']['refid'],
                                        node[0].deepcopy(),
                                        node['reftarget'])
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output :(
                pass

        else:
            env.warn_node(
                'Traceability: item %s not found' % node['reftarget'], node)

        node.replace_self(new_node)


def update_available_item_relationships(app):
    """
    Update directive option_spec with custom relationships defined in
    configuration file ``traceability_relationships`` variable.  Both
    keys (relationships) and values (reverse relationships) are added.

    This handler should be called upon builder initialization, before
    processing any directive.

    Function also sets an environment variable ``relationships`` with
    the full list of relationships (with reverse relationships also as
    keys)

    """
    env = app.builder.env
    env.relationships = {}

    for rel in list(app.config.traceability_relationships.keys()):
        env.relationships[rel] = app.config.traceability_relationships[rel]
        env.relationships[app.config.traceability_relationships[rel]] = rel

    for rel in sorted(list(env.relationships.keys())):
        ItemDirective.option_spec[rel] = directives.unchanged


def initialize_environment(app):
    """
    Perform initializations needed before the build process starts.
    """
    env = app.builder.env

    # Assure ``traceability_all_items`` will always be there.
    if not hasattr(env, 'traceability_all_items'):
        env.traceability_all_items = {}

    update_available_item_relationships(app)


# -----------------------------------------------------------------------------
# Utility functions

def make_item_ref(app, env, fromdocname, item_info):
    """
    Creates a reference node for an item, embedded in a
    paragraph. Reference text adds also a caption if it exists.

    """
    id = item_info['target']['refid']

    if item_info['caption'] != '':
        caption = ', ' + item_info['caption']
    else:
        caption = ''

    para = nodes.paragraph()
    newnode = nodes.reference('', '')
    innernode = nodes.emphasis(id + caption, id + caption)
    newnode['refdocname'] = item_info['docname']
    try:
        newnode['refuri'] = app.builder.get_relative_uri(fromdocname,
                                                         item_info['docname'])
        newnode['refuri'] += '#' + id
    except NoUri:
        # ignore if no URI can be determined, e.g. for LaTeX output :(
        pass
    newnode.append(innernode)
    para += newnode

    return para


def naturalsortkey(s):
    """Natural sort order"""
    return [int(part) if part.isdigit() else part
            for part in re.split('([0-9]+)', s)]


def are_related(env, source, target, relationships):
    """
    Returns ``True`` if ``source`` and ``target`` items are related
    according a list, ``relationships``, of relationship types.
    ``False`` is returned otherwise

    If the list of relationship types is empty, all available
    relationship types are to be considered.

    """
    if not relationships:
        relationships = list(env.relationships.keys())

    for rel in relationships:
        if (target in env.traceability_all_items[source][rel] or
            source in
                env.traceability_all_items[target][env.relationships[rel]]):
            return True

    return False


# -----------------------------------------------------------------------------
# Extension setup

def setup(app):

    # Create default relationships dictionary. Can be customized in conf.py
    app.add_config_value('traceability_relationships',
                         {'fulfills': 'fulfilled_by',
                          'depends_on': 'impacts_on',
                          'implements': 'implemented_by',
                          'realizes': 'realized_by',
                          'validates': 'validated_by',
                          'trace': 'backtrace'},
                         'env')

    # Customizable templates
    app.add_config_value('traceability_item_template',
                         """
                         {{ id }}
                         {%- if caption %}
                             **{{ caption }}**
                         {% endif %}
                             {{ content|indent(4) }}
                         """,
                         'env')

    app.add_node(item_matrix)
    app.add_node(item_list)
    app.add_node(item)

    app.add_directive('item', ItemDirective)
    app.add_directive('item-list', ItemListDirective)
    app.add_directive('item-matrix', ItemMatrixDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('env-purge-doc', purge_items)
    app.connect('builder-inited', initialize_environment)

    app.add_role('item', XRefRole(nodeclass=pending_item_xref,
                                  innernodeclass=nodes.emphasis,
                                  warn_dangling=True))
