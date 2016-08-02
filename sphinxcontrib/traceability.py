# -*- coding: utf-8 -*-

from __future__ import print_function
from docutils import nodes
from sphinx.util.compat import Directive
from docutils.parsers.rst import directives
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.environment import NoUri
from sphinx.errors import ExtensionError
from textwrap import dedent
import re

# External relationship: starts with ext_
# An external relationship is a relationship where the item to link to is not in the
# traceability system, but on an external tool. Translating the link to a clickable
# hyperlink is done through the config traceability_external_relationship_to_url.
regexp_external_relationship = re.compile('^ext_.*')
external_link_fieldname = 'field'

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
    * A custom node with id + caption, to be replaced with relationship links
    * A node containing the content of the item

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

        itemnode = item('')
        itemnode['id'] = targetid

        # Item caption is the text following the mandatory id argument.
        # Caption should be considered a line of text. Remove line breaks.
        if len(self.arguments) > 1:
            caption = self.arguments[1].replace('\n', ' ')

        # Store item info
        if targetid in env.traceability_all_items and env.traceability_all_items[targetid]['placeholder'] is False:
            # Duplicate items not allowed. Duplicate will even not be shown
            messages = [self.state.document.reporter.error(
                'Traceability: duplicated item %s' % targetid,
                line=self.lineno)]
        else:
            if targetid not in env.traceability_all_items:
                env.traceability_all_items[targetid] = {}
            env.traceability_all_items[targetid]['id'] = targetid
            env.traceability_all_items[targetid]['placeholder'] = False
            env.traceability_all_items[targetid]['type'] = self.name
            env.traceability_all_items[targetid]['class'] = self.options.get('class', [])
            env.traceability_all_items[targetid]['docname'] = env.docname
            env.traceability_all_items[targetid]['lineno'] = self.lineno
            env.traceability_all_items[targetid]['target'] = targetnode
            env.traceability_all_items[targetid]['caption'] = caption
            env.traceability_all_items[targetid]['content'] = '\n'.join(self.content)

            # Add empty relationships to item.
            initialize_relationships_for_item(env, targetid)

            # Add found relationships to item. All relationship data is a string of 
            # item ids separated by space. It is splitted in a list of item ids
            for rel in list(env.relationships.keys()):
                if rel in self.options:
                    revrel = env.relationships[rel]
                    related_ids = self.options[rel].split()
                    for related_id in related_ids:
                        env.traceability_all_items[targetid][rel].append(related_id)
                        # Check if the reverse relationship exists (non empty string)
                        if not revrel:
                            continue
                        # If the related item does not exist yet, create a placeholder item
                        if (related_id not in env.traceability_all_items):
                            env.traceability_all_items[related_id] = {
                                    'id': related_id,
                                    'placeholder': True,
                                    'type': self.name,
                                    'class': self.options.get('class', []),
                                    'docname': 'placeholder'
                            }
                            initialize_relationships_for_item(env, related_id)
                        # Also add the reverse relationship to the related item
                        env.traceability_all_items[related_id][revrel].append(targetid)

        # Output content of item to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template,
            self.state_machine.document.attributes['source'])

        return [targetnode, itemnode] + messages


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

def process_item_nodes(app, doctree, fromdocname):
    """
    This function should be triggered upon ``doctree-resolved event``

    Replace all item_list nodes with a list of the collected items.
    Augment each item with a backlink to the original location.

    """
    env = app.builder.env

    all_item_ids = sorted(env.traceability_all_items, key=naturalsortkey)

    # Sanity: check if all items that are referenced indeed exist, when it is no external reference
    for source_id in all_item_ids:
        source_item = env.traceability_all_items[source_id]
        for relationship in env.relationships:
            if not regexp_external_relationship.search(relationship):
                for target_id in source_item[relationship]:
                    if target_id not in env.traceability_all_items or \
                            env.traceability_all_items[target_id]['placeholder'] is True:
                        raise ExtensionError('Item ' + target_id + ' is not defined ')

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

        for source_id in all_item_ids:
            if re.match(node['source'], source_id):
                source_item = env.traceability_all_items[source_id]
                row = nodes.row()
                left = nodes.entry()
                left += make_internal_item_ref(app, env, fromdocname,
                                      env.traceability_all_items[source_id])
                right = nodes.entry()
                for relationship in node['type']:
                    if regexp_external_relationship.search(relationship):
                        for target_id in source_item[relationship]:
                            right += make_external_item_ref(app, env, target_id, relationship)
                for target_id in all_item_ids:
                    target_item = env.traceability_all_items[target_id]
                    if (re.match(node['target'], target_id) and
                            are_related(
                                env, source_id, target_id, node['type'])):
                        right += make_internal_item_ref(
                            app, env, fromdocname,
                            env.traceability_all_items[target_id])
                row += left
                row += right
                tbody += row

        node.replace_self(table)

    # Item list:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(item_list):
        content = nodes.bullet_list()
        for i in all_item_ids:
            if re.match(node['filter'], i):
                bullet_list_item = nodes.list_item()
                paragraph = nodes.paragraph()
                paragraph.append(
                    make_internal_item_ref(app, env, fromdocname,
                                  env.traceability_all_items[i]))
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

    # Item: replace item nodes, with admonition, list of relationships
    for node in doctree.traverse(item):
        currentitem = env.traceability_all_items[node['id']]
        cont = nodes.container()
        admon = nodes.admonition()
        title = nodes.title()
        header = currentitem['id']
        if currentitem['caption']:
            header += ' : ' + currentitem['caption']
        txt = nodes.Text(header)
        title.append(txt)
        admon.append(title)
        cont.append(admon)
        if app.config.traceability_render_relationship_per_item:
            par = nodes.paragraph()
            dl = nodes.definition_list()
            for rel in sorted(list(env.relationships.keys())):
                if rel in currentitem and currentitem[rel]:
                    dli = nodes.definition_list_item()
                    dt = nodes.term()
                    if rel in app.config.traceability_relationship_to_string:
                        relstr = app.config.traceability_relationship_to_string[rel]
                    else:
                        continue
                    txt = nodes.Text(relstr)
                    dt.append(txt)
                    dli.append(dt)
                    for tgt in currentitem[rel]:
                        dd = nodes.definition()
                        p = nodes.paragraph()
                        if regexp_external_relationship.search(rel):
                            link = make_external_item_ref(app, env, tgt, rel)
                        else:
                            link = make_internal_item_ref(app, env, fromdocname, env.traceability_all_items[tgt], False)
                        p.append(link)
                        dd.append(p)
                        dli.append(dd)
                    dl.append(dli)
            par.append(dl)
            cont.append(par)
        ## Note: content should be displayed during read of RST file, as it contains other RST objects
        node.replace_self(cont)


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
        # When reverse relationship exists, add it as well
        if app.config.traceability_relationships[rel]:
            env.relationships[app.config.traceability_relationships[rel]] = rel

    for rel in sorted(list(env.relationships.keys())):
        ItemDirective.option_spec[rel] = directives.unchanged


def initialize_environment(app):
    """
    Perform initializations needed before the build process starts.
    """
    env = app.builder.env

    # Assure ``traceability_all_items`` will always be there.
    # It needs to be empty on every (re-)build. As the script automatically
    # generates placeholders when parsing the reverse relationships, the
    # database of items needs to be empty on every re-build.
    env.traceability_all_items = {}

    update_available_item_relationships(app)


# -----------------------------------------------------------------------------
# Utility functions

def initialize_relationships_for_item(env, id):
    for rel in list(env.relationships.keys()):
        if rel:
            if rel not in env.traceability_all_items[id]:
                env.traceability_all_items[id][rel] = []

def make_external_item_ref(app, env, targettext, relationship):
    if relationship not in app.config.traceability_external_relationship_to_url:
        return
    para = nodes.paragraph()
    link = nodes.reference()
    txt = nodes.Text(targettext)
    tgt_strs = targettext.split(':') #syntax = field1:field2:field3:...
    url = app.config.traceability_external_relationship_to_url[relationship]
    cnt = 0
    for tgt_str in tgt_strs:
        cnt += 1
        url = url.replace(external_link_fieldname+str(cnt), tgt_str)
    link['refuri'] = url
    link.append(txt)
    para += link
    return para
 
def make_internal_item_ref(app, env, fromdocname, item_info, caption=True):
    """
    Creates a reference node for an item, embedded in a
    paragraph. Reference text adds also a caption if it exists.

    """
    id = item_info['target']['refid']

    if item_info['caption'] != '' and caption:
        caption = ' : ' + item_info['caption']
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

    There is not need to check the reverse relationship, as these are
    added to the dict during the parsing of the documents.
    """
    if not relationships:
        relationships = list(env.relationships.keys())

    for rel in relationships:
        if target in env.traceability_all_items[source][rel]:
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
                          'trace': 'backtrace',
                          'ext_toolname': ''},
                         'env')

    # Configuration for translating the relationship keywords to rendered text
    app.add_config_value('traceability_relationship_to_string',
                         {'fulfills': 'Fulfills',
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
                          'ext_toolname': 'Referento to toolname'},
                        'env')

    # Configuration for translating external relationship to url
    app.add_config_value('traceability_external_relationship_to_url',
                         {'ext_toolname': 'http://toolname.company.com/field1/workitem?field2'},
                        'env')

    # Configuration for enabling the rendering of the relations on every item
    app.add_config_value('traceability_render_relationship_per_item',
                         False, 'env')

    app.add_node(item_matrix)
    app.add_node(item_list)
    app.add_node(item)

    app.add_directive('item', ItemDirective)
    app.add_directive('item-list', ItemListDirective)
    app.add_directive('item-matrix', ItemMatrixDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('builder-inited', initialize_environment)

    app.add_role('item', XRefRole(nodeclass=pending_item_xref,
                                  innernodeclass=nodes.emphasis,
                                  warn_dangling=True))
