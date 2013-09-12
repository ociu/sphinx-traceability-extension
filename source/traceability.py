from sphinx.locale import _
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.compat import make_admonition

# ------------------------------------------------------------------------------
# Declare new node types (based on others): item, itemlist

class item(nodes.Admonition, nodes.Element):
    pass

class itemlist(nodes.General, nodes.Element):
    pass


# visit/depart visitor functions for item output generation: same as admonition

def visit_item_node(self, node):
    self.visit_admonition(node)

def depart_item_node(self, node):
    self.depart_admonition(node)

# ------------------------------------------------------------------------------
# Directives

class ItemDirective(Directive):

    # this enables content in the directive
    has_content = True

    def run(self):
        env = self.state.document.settings.env

        targetid = "item-%d" % env.new_serialno('item')
        targetnode = nodes.target('', '', ids=[targetid])

        ad = make_admonition(item, self.name, [_('Item')], self.options,
                             self.content, self.lineno, self.content_offset,
                             self.block_text, self.state, self.state_machine)

        if not hasattr(env, 'traceability_all_items'):
            env.traceability_all_items = []
        env.traceability_all_items.append({
            'docname': env.docname,
            'lineno': self.lineno,
            'item': ad[0].deepcopy(),
            'target': targetnode,
        })

        return [targetnode] + ad

class ItemlistDirective(Directive):

    def run(self):
        return [itemlist('')]

# ------------------------------------------------------------------------------
# Event handlers

def purge_items(app, env, docname):

    # Clean, if existing, ``item`` entries in ``traceability_all_items`` 
    # environment variable, for all the source docs that have changed
    if not hasattr(env, 'traceability_all_items'):
        return
    env.traceability_all_items = [item for item in env.traceability_all_items
                          if item['docname'] != docname]


def process_item_nodes(app, doctree, fromdocname):

    if not app.config.traceability_include_item_ids:
        for node in doctree.traverse(item):
            node.parent.remove(node)

    # Replace all itemlist nodes with a list of the collected items.
    # Augment each item with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(itemlist):
        if not app.config.traceability_include_item_ids:
            node.replace_self([])
            continue

        content = []

        for item_info in env.traceability_all_items:
            para = nodes.paragraph()
            filename = env.doc2path(item_info['docname'], base=None)
            description = (
                _('(The original entry is located in %s, line %d and can be found ') %
                (filename, item_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis(_('here'), _('here'))
            newnode['refdocname'] = item_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, item_info['docname'])
            newnode['refuri'] += '#' + item_info['target']['refid']
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the itemlist
            content.append(item_info['item'])
            content.append(para)

        node.replace_self(content)

# ------------------------------------------------------------------------------
# Extension setup

def setup(app):

    app.add_config_value('traceability_include_item_ids', False, False)

    app.add_node(itemlist)
    app.add_node(item,
                 html=(visit_item_node, depart_item_node),
                 latex=(visit_item_node, depart_item_node),
                 text=(visit_item_node, depart_item_node))

    app.add_directive('item', ItemDirective)
    app.add_directive('itemlist', ItemlistDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('env-purge-doc', purge_items)
