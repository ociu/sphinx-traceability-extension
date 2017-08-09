# -*- coding: utf-8 -*-

'''
Traceability plugin

Sphinx extension for restructured text that added traceable documentation items.
See readme for more details.
'''

from __future__ import print_function
import re
from sphinx.util.compat import Directive
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx import __version__ as sphinx_version
if sphinx_version >= '1.6.0':
    from sphinx.util.logging import getLogger
from sphinx.environment import NoUri
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.utils import get_source_line

# External relationship: starts with ext_
# An external relationship is a relationship where the item to link to is not in the
# traceability system, but on an external tool. Translating the link to a clickable
# hyperlink is done through the config traceability_external_relationship_to_url.
REGEXP_EXTERNAL_RELATIONSHIP = re.compile('^ext_.*')
EXTERNAL_LINK_FIELDNAME = 'field'

def report_warning(env, msg, docname, lineno=None):
    '''Convenience function for logging a warning

    Args:
        msg (str): Message of the warning
        docname (str): Name of the document on which the error occured
        lineno (str): Line number in the document on which the error occured
    '''
    if sphinx_version >= '1.6.0':
        logger = getLogger(__name__)
        if lineno:
            logger.warning(msg, location=(docname, lineno))
        else:
            logger.warning(msg, location=docname)
    else:
        env.warn(docname, msg, lineno=lineno)

# -----------------------------------------------------------------------------
# Declare new node types (based on others): Item, ItemList, ItemMatrix, ItemTree


class Item(nodes.General, nodes.Element):
    '''Documentation item'''
    pass


class ItemList(nodes.General, nodes.Element):
    '''List of documentation items'''
    pass


class ItemMatrix(nodes.General, nodes.Element):
    '''Matrix for cross referencing documentation items'''
    pass

class ItemTree(nodes.General, nodes.Element):
    '''Tree-view on documentation items'''
    pass


# -----------------------------------------------------------------------------
# Pending item cross reference node


class PendingItemXref(nodes.Inline, nodes.Element):
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
        app = env.app
        caption = ''
        messages = []

        targetid = self.arguments[0]
        targetnode = nodes.target('', '', ids=[targetid])

        itemnode = Item('')
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
            initialize_relationships(env, targetid)

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
                            }
                            initialize_relationships(env, related_id)
                        # Also add the reverse relationship to the related item
                        env.traceability_all_items[related_id][revrel].append(targetid)

            # Custom callback for modifying items
            if app.config.traceability_callback_per_item:
                app.config.traceability_callback_per_item(targetid, env.traceability_all_items)

        # Output content of item to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template, self.state_machine.document.attributes['source'])

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
        item_list_node = ItemList('')

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
        env = self.state.document.settings.env

        item_matrix_node = ItemMatrix('')

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

        # Check if given relationships are in configuration
        for rel in item_matrix_node['type']:
            if rel not in env.relationships:
                report_warning(env, 'Traceability: unknown relation for item-matrix: %s' % rel, env.docname, self.lineno)

        return [item_matrix_node]

class ItemTreeDirective(Directive):
    """
    Directive to generate a treeview of items, based on
    a given set of relationship types.

    Syntax::

      .. item-tree:: title
         :top: regexp
         :top_relation_filter: <<relationship>> ...
         :type: <<relationship>> ...

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'top': directives.unchanged,
                   'top_relation_filter': directives.unchanged,
                   'type': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        item_tree_node = ItemTree('')

        # Process title (optional argument)
        if len(self.arguments) > 0:
            item_tree_node['title'] = self.arguments[0]

        # Process ``top`` option
        if 'top' in self.options:
            item_tree_node['top'] = self.options['top']
        else:
            item_tree_node['top'] = ''

        # Process ``top_relation_filter`` option, given as a string with relationship types
        # separated by space. It is converted to a list.
        if 'top_relation_filter' in self.options:
            item_tree_node['top_relation_filter'] = self.options['top_relation_filter'].split()
        else:
            item_tree_node['top_relation_filter'] = ''

        # Check if given relationships are in configuration
        for rel in item_tree_node['top_relation_filter']:
            if rel not in env.relationships:
                report_warning(env, 'Traceability: unknown relation for item-tree: %s' % rel, env.docname, self.lineno)

        # Process ``type`` option, given as a string with relationship types
        # separated by space. It is converted to a list.
        if 'type' in self.options:
            item_tree_node['type'] = self.options['type'].split()
        else:
            item_tree_node['type'] = []

        # Check if given relationships are in configuration
        # Combination of forward + matching reverse relationship cannot be in the same list, as it will give
        # endless treeview (and endless recursion in python --> exception)
        for rel in item_tree_node['type']:
            if rel not in env.relationships:
                report_warning(env, 'Traceability: unknown relation for item-tree: %s' % rel, env.docname, self.lineno)
                continue
            if env.relationships[rel] in item_tree_node['type']:
                report_warning(env, 'Traceability: combination of forward+reverse relations for item-tree: %s' % rel, env.docname, self.lineno)
                raise ValueError('Traceability: combination of forward+reverse relations for item-tree: %s' % rel)

        return [item_tree_node]


# -----------------------------------------------------------------------------
# Event handlers

def process_item_nodes(app, doctree, fromdocname):
    """
    This function should be triggered upon ``doctree-resolved event``

    Replace all ItemList nodes with a list of the collected items.
    Augment each item with a backlink to the original location.

    """
    env = app.builder.env

    all_item_ids = sorted(env.traceability_all_items, key=naturalsortkey)

    # Item matrix:
    # Create table with related items, printing their target references.
    # Only source and target items matching respective regexp shall be included
    for node in doctree.traverse(ItemMatrix):
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
            source_item = env.traceability_all_items[source_id]
            # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
            if source_item['placeholder'] is True:
                continue
            if re.match(node['source'], source_id):
                row = nodes.row()
                left = nodes.entry()
                left += make_internal_item_ref(app, node, fromdocname, source_id)
                right = nodes.entry()
                for relationship in node['type']:
                    if REGEXP_EXTERNAL_RELATIONSHIP.search(relationship):
                        for target_id in source_item[relationship]:
                            right += make_external_item_ref(app, target_id, relationship)
                for target_id in all_item_ids:
                    target_item = env.traceability_all_items[target_id]
                    # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
                    if target_item['placeholder'] is True:
                        continue
                    if (re.match(node['target'], target_id) and
                            are_related(
                                env, source_id, target_id, node['type'])):
                        right += make_internal_item_ref(app, node, fromdocname, target_id)
                row += left
                row += right
                tbody += row

        node.replace_self(table)

    # Item list:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(ItemList):
        ul_node = nodes.bullet_list()
        for i in all_item_ids:
            # placeholders don't end up in any item-list (less duplicate warnings for missing items)
            if env.traceability_all_items[i]['placeholder'] is True:
                continue
            if re.match(node['filter'], i):
                bullet_list_item = nodes.list_item()
                p_node = nodes.paragraph()
                p_node.append(make_internal_item_ref(app, node, fromdocname, i))
                bullet_list_item.append(p_node)
                ul_node.append(bullet_list_item)

        node.replace_self(ul_node)

    # Item tree:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(ItemTree):
        ul_node = nodes.bullet_list()
        ul_node.set_class('bonsai')
        for i in all_item_ids:
            # placeholders don't end up in any item-tree (less duplicate warnings for missing items)
            if env.traceability_all_items[i]['placeholder'] is True:
                continue
            if re.match(node['top'], i):
                if is_item_top_level(env, i, node['top'], node['top_relation_filter']):
                    ul_node.append(generate_bullet_list_tree(app, env, node, fromdocname, i))
        node.replace_self(ul_node)

    # Resolve item cross references (from ``item`` role)
    for node in doctree.traverse(PendingItemXref):
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
            if item_info['placeholder'] is True:
                report_warning(env, 'Traceability: cannot link to %s, item is not defined' % item_info['id'], fromdocname, get_source_line(node))
            else:
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
            report_warning(env, 'Traceability: item %s not found' % node['reftarget'], fromdocname, get_source_line(node))

        node.replace_self(new_node)

    # Item: replace item nodes, with admonition, list of relationships
    for node in doctree.traverse(Item):
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
            par_node = nodes.paragraph()
            dl_node = nodes.definition_list()
            for rel in sorted(list(env.relationships.keys())):
                if rel in currentitem and currentitem[rel]:
                    li_node = nodes.definition_list_item()
                    dt_node = nodes.term()
                    if rel in app.config.traceability_relationship_to_string:
                        relstr = app.config.traceability_relationship_to_string[rel]
                    else:
                        continue
                    txt = nodes.Text(relstr)
                    dt_node.append(txt)
                    li_node.append(dt_node)
                    for tgt in currentitem[rel]:
                        dd_node = nodes.definition()
                        p_node = nodes.paragraph()
                        if REGEXP_EXTERNAL_RELATIONSHIP.search(rel):
                            link = make_external_item_ref(app, tgt, rel)
                        else:
                            link = make_internal_item_ref(app, node, fromdocname, tgt, True)
                        p_node.append(link)
                        dd_node.append(p_node)
                        li_node.append(dd_node)
                    dl_node.append(li_node)
            par_node.append(dl_node)
            cont.append(par_node)
        ## Note: content should be displayed during read of RST file, as it contains other RST objects
        node.replace_self(cont)


def init_available_relationships(app):
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

    init_available_relationships(app)

    # LaTeX-support: since we generate empty tags, we need to relax the verbosity of that error
    if 'preamble' not in app.config.latex_elements:
        app.config.latex_elements['preamble'] = ''
    app.config.latex_elements['preamble'] += '''\
\\makeatletter
\\let\@noitemerr\\relax
\\makeatother'''



# -----------------------------------------------------------------------------
# Utility functions

def is_item_top_level(env, itemid, topregex, relations):
    '''
    Check if item with given itemid is a top level item

    True, if the item is a top level item:
        - given relation does not exist for given item,
        - or given relation exists, but targets don't match the 'top' regexp.
    False, otherwise.
    '''
    for relation in relations:
        if relation not in env.relationships:
            continue
        if env.traceability_all_items[itemid][relation]:
            for tgt in env.traceability_all_items[itemid][relation]:
                if re.match(topregex, tgt):
                    return False
    return True

def generate_bullet_list_tree(app, env, node, fromdocname, itemid):
    '''
    Generate a bullet list tree for the given item id

    This function returns the given itemid as a bullet item node, makes a child bulleted list, and adds all
    of the matching child items to it.
    '''
    #First add current itemid
    bullet_list_item = nodes.list_item()
    bullet_list_item['id'] = nodes.make_id(itemid)
    #bullet_list_item.set_attribute('id', nodes.make_id(itemid))
    p_node = nodes.paragraph()
    p_node.set_class('thumb')
    bullet_list_item.append(p_node)
    bullet_list_item.append(make_internal_item_ref(app, node, fromdocname, itemid))
    bullet_list_item.set_class('has-children')
    bullet_list_item.set_class('collapsed')
    childcontent = nodes.bullet_list()
    childcontent.set_class('bonsai')
    #Then recurse one level, and add dependencies
    for relation in node['type']:
        if relation not in env.relationships:
            continue
        if not env.traceability_all_items[itemid][relation]:
            continue
        for target in env.traceability_all_items[itemid][relation]:
            #print('%s has child %s for relation %s' % (itemid, target, relation))
            childcontent.append(generate_bullet_list_tree(app, env, node, fromdocname, target))
    bullet_list_item.append(childcontent)
    return bullet_list_item

def initialize_relationships(env, itemid):
    '''Initialize given itemid with empty list of relationships'''
    for rel in list(env.relationships.keys()):
        if rel:
            if rel not in env.traceability_all_items[itemid]:
                env.traceability_all_items[itemid][rel] = []

def make_external_item_ref(app, targettext, relationship):
    '''Generate a reference to an external item'''
    if relationship not in app.config.traceability_external_relationship_to_url:
        return
    p_node = nodes.paragraph()
    link = nodes.reference()
    txt = nodes.Text(targettext)
    tgt_strs = targettext.split(':') #syntax = field1:field2:field3:...
    url = app.config.traceability_external_relationship_to_url[relationship]
    cnt = 0
    for tgt_str in tgt_strs:
        cnt += 1
        url = url.replace(EXTERNAL_LINK_FIELDNAME+str(cnt), tgt_str)
    link['refuri'] = url
    link.append(txt)
    targetid = nodes.make_id(targettext)
    target = nodes.target('', '', ids=[targetid])
    p_node += target
    p_node += link
    return p_node

def make_internal_item_ref(app, node, fromdocname, item_id, caption=True):
    """
    Creates a reference node for an item, embedded in a
    paragraph. Reference text adds also a caption if it exists.

    """
    env = app.builder.env
    item_info = env.traceability_all_items[item_id]

    p_node = nodes.paragraph()

    # Only create link when target item exists, warn otherwise (in html and terminal)
    if item_info['placeholder'] is True:
        report_warning(env, 'Traceability: cannot link to %s, item is not defined' % item_id, fromdocname, get_source_line(node))
        txt = nodes.Text('%s not defined, broken link' % item_id)
        p_node.append(txt)
    else:
        if item_info['caption'] != '' and caption:
            caption = ' : ' + item_info['caption']
        else:
            caption = ''

        newnode = nodes.reference('', '')
        innernode = nodes.emphasis(item_id + caption, item_id + caption)
        newnode['refdocname'] = item_info['docname']
        try:
            newnode['refuri'] = app.builder.get_relative_uri(fromdocname,
                                                             item_info['docname'])
            newnode['refuri'] += '#' + item_id
        except NoUri:
            # ignore if no URI can be determined, e.g. for LaTeX output :(
            pass
        newnode.append(innernode)
        p_node += newnode

    return p_node


def naturalsortkey(text):
    """Natural sort order"""
    return [int(part) if part.isdigit() else part
            for part in re.split('([0-9]+)', text)]


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

    if source not in env.traceability_all_items:
        return False

    for rel in relationships:
        if rel not in env.traceability_all_items[source]:
            continue
        if target in env.traceability_all_items[source][rel]:
            return True

    return False


# -----------------------------------------------------------------------------
# Extension setup

def setup(app):
    '''Extension setup'''

    # Javascript and stylesheet for the tree-view
    # app.add_javascript('jquery.js') #note: can only be included once
    app.add_javascript('http://simonwade.me/assets/bower_components/jquery-bonsai/jquery.bonsai.js')
    app.add_stylesheet('http://simonwade.me/assets/bower_components/jquery-bonsai/jquery.bonsai.css')
    app.add_javascript('traceability.js')

    # Configuration for adapting items through a callback
    app.add_config_value('traceability_callback_per_item',
                         None, 'env')

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

    app.add_node(ItemTree)
    app.add_node(ItemMatrix)
    app.add_node(ItemList)
    app.add_node(Item)

    app.add_directive('item', ItemDirective)
    app.add_directive('item-list', ItemListDirective)
    app.add_directive('item-matrix', ItemMatrixDirective)
    app.add_directive('item-tree', ItemTreeDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('builder-inited', initialize_environment)

    app.add_role('item', XRefRole(nodeclass=PendingItemXref,
                                  innernodeclass=nodes.emphasis,
                                  warn_dangling=True))

