from sphinx.locale import _
from docutils import nodes
from sphinx.util.compat import Directive
from docutils.parsers.rst import directives
from sphinx.util.compat import make_admonition
from sphinx.roles import XRefRole
from sphinx import addnodes
from sphinx.util.nodes import make_refnode
import re

# -----------------------------------------------------------------------------
# Declare new node types (based on others): item, item_list, item_matrix

class item(nodes.Admonition, nodes.Element):
    pass

class item_list(nodes.General, nodes.Element):
    pass

class item_matrix(nodes.General, nodes.Element):
    pass

# visit/depart visitor functions for item output generation: same as admonition

def visit_item_node(self, node):
    self.visit_admonition(node)

def depart_item_node(self, node):
    self.depart_admonition(node)
    
# -----------------------------------------------------------------------------
# Pending item cross reference node

class pending_item_xref(nodes.Inline, nodes.Element):
    """
    Node for item cross-references that cannot be resolved without complete
    information about all documents.

    """
    pass

# -----------------------------------------------------------------------------
# Directives

class ItemDirective(Directive):
    """
    Directive to declare items and their traceability relationships.

    Syntax::

      .. item:: item_id [item_caption]
         :trace: [<<stereotype>>] other_item_id ...

         [item_content]

    When run, for each item, two nodes will be returned:
    
    * A target node
    * An admonition node
    
    Also ``traceability_all_items`` storage is filled with item information

    """
    # Required argument: id
    required_arguments = 1
    # Optional argument: caption (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options: the typical ones plus ``trace`` 
    option_spec = {'class': directives.class_option,
                   'trace': directives.unchanged}
    # Content allowed
    has_content = True

    def run(self):
        env = self.state.document.settings.env
        caption = ''
        trace = []
        messages = []
        
        targetid = self.arguments[0]
        targetnode = nodes.target('', '', ids=[targetid])
        
        # Item caption is the text following the mandatory id argument
        if len(self.arguments) > 1:
            caption = self.arguments[1]

        # Trace info is a string of item ids separated by space
        # It is converted to a list of item ids
        if 'trace' in self.options:
            trace = self.options['trace'].split(' ')
            
        ad = make_admonition(item, self.name, [targetid], self.options,
                             self.content, self.lineno, self.content_offset,
                             self.block_text, self.state, self.state_machine)

        if not hasattr(env, 'traceability_all_items'):
            env.traceability_all_items = {}
        
        if targetid not in env.traceability_all_items:
            env.traceability_all_items[targetid] =  {
                'docname': env.docname,
                'lineno': self.lineno,
                'item': ad[0].deepcopy(),
                'target': targetnode,
                'caption': caption,
                'trace' : trace
            }
        else:
            messages = [self.state.document.reporter.error(
                'Traceability: duplicated item %s' % targetid,
                line=self.lineno)]
                
        return [targetnode] + ad + messages


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
    Directive to generate a matrix of item cross-references, based on ``trace``
    relationships.
    
    Syntax::

      .. item-matrix:: title
         :target: regexp
         :source: regexp
         :type: <<stereotype>> ...

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

        # Process ``type`` option, given as a string with <<...>> stereotypes
        # separated by space. It is converted to a list.
        if 'type' in self.options:
            item_matrix_node['type'] = self.options['type'].split(' ')

        return [item_matrix_node]


# -----------------------------------------------------------------------------
# Event handlers

def purge_items(app, env, docname):
    """
    Clean, if existing, ``item`` entries in ``traceability_all_items`` 
    environment variable, for all the source docs being purged.
    
    This function should be triggered upon ``env-purge-doc`` event.

    """
    if not hasattr(env, 'traceability_all_items'):
        return
    keys = env.traceability_all_items.keys()
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

    # Item matrix:
    # Create table with related items, printing their target references.
    # Only source and target items matching respective regexp shall be included
    for node in doctree.traverse(item_matrix):
        content = []
        for target_item in env.traceability_all_items:
            if re.match(node['target'], target_item):
                content.append( make_item_ref(app, env, fromdocname, 
                                     env.traceability_all_items[target_item]))
                
                for source_item in env.traceability_all_items:
                    if re.match(node['source'], source_item) and \
                    target_item in \
                    env.traceability_all_items[source_item]['trace']:
                        content.append( make_item_ref(app, env, fromdocname, 
                                     env.traceability_all_items[source_item]))

        node.replace_self(content)

    # Item list: 
    # Create list with target references. Only items matching list regexp
    # shall be included
    for node in doctree.traverse(item_list):
        content = []
        for item in env.traceability_all_items:
            if re.match(node['filter'], item):
                content.append( make_item_ref(app, env, fromdocname, 
                                         env.traceability_all_items[item]))
        node.replace_self(content)

    # Resolve item cross references (from ``item`` role)
    for node in doctree.traverse(pending_item_xref):
        if node['reftarget'] in env.traceability_all_items:
            item_info = env.traceability_all_items[node['reftarget']]
            node.replace_self( make_refnode(app.builder,
                                            fromdocname,
                                            item_info['docname'], 
                                            item_info['target']['refid'],
                                            node[0].deepcopy()))
        else:
            node.replace_self([])
            env.warn_node('Traceability: item %s not found' %
                           node['reftarget'], node)

# -----------------------------------------------------------------------------
# Utility functions

def make_item_ref(app, env, fromdocname, item_info):
    """
    Creates a reference node for an item, embedded in a paragraph. Reference
    text adds also a caption if it exists, between parenthesis.
    """

    id = item_info['target']['refid']

    if  item_info['caption'] != '':
        caption = ' (' + item_info['caption'] + ')'
    else:
        caption = ''
    
    para = nodes.paragraph()
    filename = env.doc2path(item_info['docname'], base=None)
    newnode = nodes.reference('', '')
    innernode = nodes.emphasis(id + caption , id + caption)
    newnode['refdocname'] = item_info['docname']
    newnode['refuri'] = app.builder.get_relative_uri(
                                fromdocname, item_info['docname'])
    newnode['refuri'] += '#' + id
    newnode.append(innernode)
    para += newnode

    return para

# -----------------------------------------------------------------------------
# Extension setup

def setup(app):

    app.add_node(item_matrix)
    app.add_node(item_list)
    app.add_node(item,
                 html=(visit_item_node, depart_item_node),
                 latex=(visit_item_node, depart_item_node),
                 text=(visit_item_node, depart_item_node))

    app.add_directive('item', ItemDirective)
    app.add_directive('item-list', ItemListDirective)
    app.add_directive('item-matrix', ItemMatrixDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('env-purge-doc', purge_items)

    app.add_role('item', XRefRole(nodeclass=pending_item_xref,
                                   innernodeclass=nodes.emphasis,
                                   warn_dangling=True))

