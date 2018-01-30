# -*- coding: utf-8 -*-

'''
Traceability plugin

Sphinx extension for restructured text that added traceable documentation items.
See readme for more details.
'''

from __future__ import print_function
import re
from docutils.parsers.rst import Directive
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.environment import NoUri
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.utils import get_source_line
from mlx.traceable_item import TraceableCollection, TraceableItem, TraceabilityException, MultipleTraceabilityExceptions
from sphinx import __version__ as sphinx_version
if sphinx_version >= '1.6.0':
    from sphinx.util.logging import getLogger

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
        if lineno is not None:
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


class Item2DMatrix(nodes.General, nodes.Element):
    '''Matrix for cross referencing documentation items in 2 dimensions'''
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

    Also ``traceability_collection`` storage is filled with item information

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

        targetid = self.arguments[0]
        targetnode = nodes.target('', '', ids=[targetid])

        itemnode = Item('')
        itemnode['id'] = targetid

        # Item caption is the text following the mandatory id argument.
        # Caption should be considered a line of text. Remove line breaks.
        if len(self.arguments) > 1:
            caption = self.arguments[1].replace('\n', ' ')

        try:
            # Store item info
            item = TraceableItem(targetid)
            item.set_document(env.docname, self.lineno)
            item.bind_node(targetnode)
            item.set_caption(caption)
            item.set_content('\n'.join(self.content))
            env.traceability_collection.add_item(item)

            # Add found relationships to item. All relationship data is a string of
            # item ids separated by space. It is splitted in a list of item ids
            for rel in env.traceability_collection.iter_relations():
                if rel in self.options:
                    related_ids = self.options[rel].split()
                    for related_id in related_ids:
                        env.traceability_collection.add_relation(targetid, rel, related_id)

            # Custom callback for modifying items
            if app.config.traceability_callback_per_item:
                app.config.traceability_callback_per_item(targetid, env.traceability_collection)
        except TraceabilityException as err:
            report_warning(env, err, env.docname, self.lineno)

        # Output content of item to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template, self.state_machine.document.attributes['source'])

        return [targetnode, itemnode]


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
        else:
            item_list_node['title'] = 'List of items'

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
         :targettitle: Target column header
         :sourcetitle: Source column header
         :type: <<relationship>> ...
         :stats:

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'target': directives.unchanged,
                   'source': directives.unchanged,
                   'targettitle': directives.unchanged,
                   'sourcetitle': directives.unchanged,
                   'type': directives.unchanged,
                   'stats': directives.flag}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        item_matrix_node = ItemMatrix('')

        # Process title (optional argument)
        if len(self.arguments) > 0:
            item_matrix_node['title'] = self.arguments[0]
        else:
            item_matrix_node['title'] = 'Traceability matrix of items'

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
            if rel not in env.traceability_collection.iter_relations():
                report_warning(env, 'Traceability: unknown relation for item-matrix: %s' % rel,
                               env.docname, self.lineno)

        # Check statistics flag
        if 'stats' in self.options:
            item_matrix_node['stats'] = True
        else:
            item_matrix_node['stats'] = False

        # Check source title
        if 'sourcetitle' in self.options:
            item_matrix_node['sourcetitle'] = self.options['sourcetitle']
        else:
            item_matrix_node['sourcetitle'] = 'Source'

        # Check target title
        if 'targettitle' in self.options:
            item_matrix_node['targettitle'] = self.options['targettitle']
        else:
            item_matrix_node['targettitle'] = 'Target'

        return [item_matrix_node]


class Item2DMatrixDirective(Directive):
    """
    Directive to generate a 2D-matrix of item cross-references, based on
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
                   'hit': directives.unchanged,
                   'miss': directives.unchanged,
                   'type': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        node = Item2DMatrix('')

        # Process title (optional argument)
        if len(self.arguments) > 0:
            node['title'] = self.arguments[0]
        else:
            node['title'] = '2D traceability matrix of items'

        # Process ``target`` & ``source`` options
        for option in ('target', 'source'):
            if option in self.options:
                node[option] = self.options[option]
            else:
                node[option] = ''

        # Process ``type`` option, given as a string with relationship types
        # separated by space. It is converted to a list.
        if 'type' in self.options:
            node['type'] = self.options['type'].split()
        else:
            node['type'] = []

        # Check if given relationships are in configuration
        for rel in node['type']:
            if rel not in env.traceability_collection.iter_relations():
                report_warning(env, 'Traceability: unknown relation for item-2d-matrix: %s' % rel,
                               env.docname, self.lineno)

        # Check hit string
        if 'hit' in self.options:
            node['hit'] = self.options['hit']
        else:
            node['hit'] = 'x'

        # Check miss string
        if 'miss' in self.options:
            node['miss'] = self.options['miss']
        else:
            node['miss'] = ''

        return [node]


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
        else:
            item_tree_node['title'] = 'Tree of items'

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
            if rel not in env.traceability_collection.iter_relations():
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
            if rel not in env.traceability_collection.iter_relations():
                report_warning(env, 'Traceability: unknown relation for item-tree: %s' % rel, env.docname, self.lineno)
                continue
            if env.traceability_collection.get_reverse_relation(rel) in item_tree_node['type']:
                report_warning(env, 'Traceability: combination of forward+reverse relations for item-tree: %s' % rel,
                               env.docname, self.lineno)
                raise ValueError('Traceability: combination of forward+reverse relations for item-tree: %s' % rel)

        return [item_tree_node]


# -----------------------------------------------------------------------------
# Event handlers

def perform_consistency_check(app, doctree):

    '''
    New in sphinx 1.6: consistency checker callback

    Used to perform the self-test on the collection of items
    '''
    env = app.builder.env

    try:
        env.traceability_collection.self_test()
    except TraceabilityException as err:
        report_warning(env, err, err.get_document())
    except MultipleTraceabilityExceptions as errs:
        for err in errs.iter():
            report_warning(env, err, err.get_document())


def process_item_nodes(app, doctree, fromdocname):
    """
    This function should be triggered upon ``doctree-resolved event``

    Replace all ItemList nodes with a list of the collected items.
    Augment each item with a backlink to the original location.

    """
    env = app.builder.env

    if sphinx_version < '1.6.0':
        try:
            env.traceability_collection.self_test(fromdocname)
        except TraceabilityException as err:
            report_warning(env, err, fromdocname)
        except MultipleTraceabilityExceptions as errs:
            for err in errs.iter():
                report_warning(env, err, err.get_document())

    all_item_ids = env.traceability_collection.iter_items()

    # Item matrix:
    # Create table with related items, printing their target references.
    # Only source and target items matching respective regexp shall be included
    for node in doctree.traverse(ItemMatrix):
        top_node = nodes.container()
        admon_node = nodes.admonition()
        title_node = nodes.title()
        title_node += nodes.Text(node['title'])
        admon_node += title_node
        top_node += admon_node
        table = nodes.table()
        tgroup = nodes.tgroup()
        left_colspec = nodes.colspec(colwidth=5)
        right_colspec = nodes.colspec(colwidth=5)
        tgroup += [left_colspec, right_colspec]
        tgroup += nodes.thead('', nodes.row(
            '',
            nodes.entry('', nodes.paragraph('', node['sourcetitle'])),
            nodes.entry('', nodes.paragraph('', node['targettitle']))))
        tbody = nodes.tbody()
        tgroup += tbody
        table += tgroup

        relationships = node['type']
        if not relationships:
            relationships = env.traceability_collection.iter_relations()

        count_total = 0
        count_covered = 0

        for source_id in all_item_ids:
            source_item = env.traceability_collection.get_item(source_id)
            # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
            if source_item.is_placeholder():
                continue
            if re.match(node['source'], source_id):
                count_total += 1
                covered = False
                row = nodes.row()
                left = nodes.entry()
                left += make_internal_item_ref(app, node, fromdocname, source_id)
                right = nodes.entry()
                for relationship in relationships:
                    if REGEXP_EXTERNAL_RELATIONSHIP.search(relationship):
                        for target_id in source_item.iter_targets(relationship):
                            right += make_external_item_ref(app, target_id, relationship)
                            covered = True
                for target_id in all_item_ids:
                    target_item = env.traceability_collection.get_item(target_id)
                    # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
                    if not target_item or target_item.is_placeholder():
                        continue
                    if (re.match(node['target'], target_id) and
                            are_related(env, source_id, target_id, relationships)):
                        right += make_internal_item_ref(app, node, fromdocname, target_id)
                        covered = True
                if covered:
                    count_covered += 1
                row += left
                row += right
                tbody += row

        try:
            percentage = int(100 * count_covered / count_total)
        except ZeroDivisionError:
            percentage = 0
        disp = 'Statistics: {cover} out of {total} covered: {pct}%'.format(cover=count_covered,
                                                                           total=count_total,
                                                                           pct=percentage)
        if node['stats']:
            p_node = nodes.paragraph()
            txt = nodes.Text(disp)
            p_node += txt
            top_node += p_node

        top_node += table
        node.replace_self(top_node)

    # Item 2D matrix:
    # Create table with related items, printing their target references.
    # Only source and target items matching respective regexp shall be included
    for node in doctree.traverse(Item2DMatrix):
        source_ids = env.traceability_collection.get_matches(node['source'])
        target_ids = env.traceability_collection.get_matches(node['target'])
        top_node = nodes.container()
        admon_node = nodes.admonition()
        title_node = nodes.title()
        title_node += nodes.Text(node['title'])
        admon_node += title_node
        top_node += admon_node
        table = nodes.table()
        tgroup = nodes.tgroup()
        colspecs = [nodes.colspec(colwidth=5)]
        hrow = nodes.row('', nodes.entry('', nodes.paragraph('', '')))
        for source_id in source_ids:
            colspecs.append(nodes.colspec(colwidth=5))
            src_cell = make_internal_item_ref(app, node, fromdocname, source_id, False)
            hrow.append(nodes.entry('', src_cell))
        tgroup += colspecs
        tgroup += nodes.thead('', hrow)
        tbody = nodes.tbody()
        for target_id in target_ids:
            row = nodes.row()
            tgt_cell = nodes.entry()
            tgt_cell += make_internal_item_ref(app, node, fromdocname, target_id, False)
            row += tgt_cell
            for source_id in source_ids:
                cell = nodes.entry()
                p_node = nodes.paragraph()
                if env.traceability_collection.are_related(source_id, node['type'], target_id):
                    txt = node['hit']
                else:
                    txt = node['miss']
                p_node += nodes.Text(txt)
                cell += p_node
                row += cell
            tbody += row
        tgroup += tbody
        table += tgroup
        top_node += table
        node.replace_self(top_node)

    # Item list:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(ItemList):
        top_node = nodes.container()
        admon_node = nodes.admonition()
        title_node = nodes.title()
        title_node += nodes.Text(node['title'])
        admon_node += title_node
        top_node += admon_node
        ul_node = nodes.bullet_list()
        for i in all_item_ids:
            # placeholders don't end up in any item-list (less duplicate warnings for missing items)
            if env.traceability_collection.get_item(i).is_placeholder():
                continue
            if re.match(node['filter'], i):
                bullet_list_item = nodes.list_item()
                p_node = nodes.paragraph()
                p_node.append(make_internal_item_ref(app, node, fromdocname, i))
                bullet_list_item.append(p_node)
                ul_node.append(bullet_list_item)

        top_node += ul_node
        node.replace_self(top_node)

    # Item tree:
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(ItemTree):
        top_node = nodes.container()
        admon_node = nodes.admonition()
        title_node = nodes.title()
        title_node += nodes.Text(node['title'])
        admon_node += title_node
        top_node += admon_node
        ul_node = nodes.bullet_list()
        ul_node.set_class('bonsai')
        for i in all_item_ids:
            # placeholders don't end up in any item-tree (less duplicate warnings for missing items)
            if env.traceability_collection.get_item(i).is_placeholder():
                continue
            if re.match(node['top'], i):
                if is_item_top_level(env, i, node['top'], node['top_relation_filter']):
                    ul_node.append(generate_bullet_list_tree(app, env, node, fromdocname, i))
        top_node += ul_node
        node.replace_self(top_node)

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
        item_info = env.traceability_collection.get_item(node['reftarget'])
        if item_info:
            if item_info.is_placeholder():
                docname, lineno = get_source_line(node)
                report_warning(env, 'Traceability: cannot link to %s, item is not defined' % item_info.get_id(),
                               docname, lineno)
            else:
                try:
                    new_node = make_refnode(app.builder,
                                            fromdocname,
                                            item_info.docname,
                                            item_info.node['refid'],
                                            node[0].deepcopy(),
                                            node['reftarget'])
                except NoUri:
                    # ignore if no URI can be determined, e.g. for LaTeX output :(
                    pass

        else:
            docname, lineno = get_source_line(node)
            report_warning(env, 'Traceability: item %s not found' % node['reftarget'],
                           docname, lineno)

        node.replace_self(new_node)

    # Item: replace item nodes, with admonition, list of relationships
    for node in doctree.traverse(Item):
        currentitem = env.traceability_collection.get_item(node['id'])
        cont = nodes.container()
        admon = nodes.admonition()
        title = nodes.title()
        header = currentitem.get_id()
        if currentitem.caption:
            header += ' : ' + currentitem.caption
        txt = nodes.Text(header)
        title.append(txt)
        admon.append(title)
        cont.append(admon)
        if app.config.traceability_render_relationship_per_item:
            par_node = nodes.paragraph()
            dl_node = nodes.definition_list()
            for rel in env.traceability_collection.iter_relations():
                tgts = currentitem.iter_targets(rel)
                if tgts:
                    li_node = nodes.definition_list_item()
                    dt_node = nodes.term()
                    if rel in app.config.traceability_relationship_to_string:
                        relstr = app.config.traceability_relationship_to_string[rel]
                    else:
                        continue
                    txt = nodes.Text(relstr)
                    dt_node.append(txt)
                    li_node.append(dt_node)
                    for tgt in tgts:
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
        # Note: content should be displayed during read of RST file, as it contains other RST objects
        node.replace_self(cont)


def init_available_relationships(app):
    """
    Update directive option_spec with custom relationships defined in
    configuration file ``traceability_relationships`` variable.  Both
    keys (relationships) and values (reverse relationships) are added.

    This handler should be called upon builder initialization, before
    processing any directive.

    Function also passes relationships to traceability collection.
    """
    env = app.builder.env

    for rel in list(app.config.traceability_relationships.keys()):
        revrel = app.config.traceability_relationships[rel]
        env.traceability_collection.add_relation_pair(rel, revrel)
        ItemDirective.option_spec[rel] = directives.unchanged
        if revrel:
            ItemDirective.option_spec[revrel] = directives.unchanged


def initialize_environment(app):
    """
    Perform initializations needed before the build process starts.
    """
    env = app.builder.env

    # Assure ``traceability_collection`` will always be there.
    # It needs to be empty on every (re-)build. As the script automatically
    # generates placeholders when parsing the reverse relationships, the
    # database of items needs to be empty on every re-build.
    env.traceability_collection = TraceableCollection()

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
    item = env.traceability_collection.get_item(itemid)
    for relation in relations:
        tgts = item.iter_targets(relation)
        for tgt in tgts:
            if re.match(topregex, tgt):
                return False
    return True


def generate_bullet_list_tree(app, env, node, fromdocname, itemid):
    '''
    Generate a bullet list tree for the given item id

    This function returns the given itemid as a bullet item node, makes a child bulleted list, and adds all
    of the matching child items to it.
    '''
    # First add current itemid
    bullet_list_item = nodes.list_item()
    bullet_list_item['id'] = nodes.make_id(itemid)
    p_node = nodes.paragraph()
    p_node.set_class('thumb')
    bullet_list_item.append(p_node)
    bullet_list_item.append(make_internal_item_ref(app, node, fromdocname, itemid))
    bullet_list_item.set_class('has-children')
    bullet_list_item.set_class('collapsed')
    childcontent = nodes.bullet_list()
    childcontent.set_class('bonsai')
    # Then recurse one level, and add dependencies
    for relation in node['type']:
        tgts = env.traceability_collection.get_item(itemid).iter_targets(relation)
        for target in tgts:
            # print('%s has child %s for relation %s' % (itemid, target, relation))
            childcontent.append(generate_bullet_list_tree(app, env, node, fromdocname, target))
    bullet_list_item.append(childcontent)
    return bullet_list_item


def make_external_item_ref(app, targettext, relationship):
    '''Generate a reference to an external item'''
    if relationship not in app.config.traceability_external_relationship_to_url:
        return
    p_node = nodes.paragraph()
    link = nodes.reference()
    txt = nodes.Text(targettext)
    tgt_strs = targettext.split(':')  # syntax = field1:field2:field3:...
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
    item_info = env.traceability_collection.get_item(item_id)

    p_node = nodes.paragraph()

    # Only create link when target item exists, warn otherwise (in html and terminal)
    if item_info.is_placeholder():
        docname, lineno = get_source_line(node)
        report_warning(env, 'Traceability: cannot link to %s, item is not defined' % item_id,
                       docname, lineno)
        txt = nodes.Text('%s not defined, broken link' % item_id)
        p_node.append(txt)
    else:
        if item_info.caption != '' and caption:
            caption = ' : ' + item_info.caption
        else:
            caption = ''

        newnode = nodes.reference('', '')
        innernode = nodes.emphasis(item_id + caption, item_id + caption)
        newnode['refdocname'] = item_info.docname
        try:
            newnode['refuri'] = app.builder.get_relative_uri(fromdocname,
                                                             item_info.docname)
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

    There is no need to check the reverse relationship, as these are
    added to the dict during the parsing of the documents.
    """
    if not relationships:
        relationships = env.traceability_collection.iter_relations()

    sourceitem = env.traceability_collection.get_item(source)
    if not sourceitem:
        return False

    for rel in relationships:
        tgts = sourceitem.iter_targets(rel)
        if target in tgts:
            return True

    return False


# -----------------------------------------------------------------------------
# Extension setup

def setup(app):
    '''Extension setup'''

    # Javascript and stylesheet for the tree-view
    # app.add_javascript('jquery.js') #note: can only be included once
    app.add_javascript('https://cdn.rawgit.com/aexmachina/jquery-bonsai/master/jquery.bonsai.js')
    app.add_stylesheet('https://cdn.rawgit.com/aexmachina/jquery-bonsai/master/jquery.bonsai.css')
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
    app.add_directive('item-2d-matrix', Item2DMatrixDirective)
    app.add_directive('item-tree', ItemTreeDirective)

    app.connect('doctree-resolved', process_item_nodes)
    if sphinx_version >= '1.6.0':
        app.connect('env-check-consistency', perform_consistency_check)
    app.connect('builder-inited', initialize_environment)

    app.add_role('item', XRefRole(nodeclass=PendingItemXref,
                                  innernodeclass=nodes.emphasis,
                                  warn_dangling=True))
