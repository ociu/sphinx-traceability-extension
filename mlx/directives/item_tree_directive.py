from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.builders.latex import LaTeXBuilder

from mlx.traceability import report_warning
from mlx.traceability_item_element import ItemElement
from mlx.traceable_item import TraceableItem


class ItemTree(ItemElement):
    '''Tree-view on documentation items'''

    def perform_traceability_replacement(self, app, collection):
        """ Performs the node replacement.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        top_item_ids = collection.get_items(self['top'], self['filter-attributes'])
        showcaptions = not self['nocaptions']
        top_node = self.create_top_node(self['title'])
        if isinstance(app.builder, LaTeXBuilder):
            p_node = nodes.paragraph()
            p_node.append(nodes.Text('Item tree is not supported in latex builder'))
            top_node.append(p_node)
        else:
            ul_node = nodes.bullet_list()
            ul_node.set_class('bonsai')
            for i in top_item_ids:
                if self.is_item_top_level(app.env, i):
                    ul_node.append(self.generate_bullet_list_tree(app, collection, i, showcaptions))
            top_node += ul_node
        self.replace_self(top_node)


class ItemTreeDirective(Directive):
    """
    Directive to generate a treeview of items, based on
    a given set of relationship types.

    Syntax::

      .. item-tree:: title
         :top: regexp
         :top_relation_filter: <<relationship>> ...
         :<<attribute>>: regexp
         :type: <<relationship>> ...
         :nocaptions:

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'top': directives.unchanged,
                   'top_relation_filter': directives.unchanged,
                   'type': directives.unchanged,
                   'nocaptions': directives.flag}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        item_tree_node = ItemTree('')
        item_tree_node['document'] = env.docname
        item_tree_node['line'] = self.lineno

        # Process title (optional argument)
        if self.arguments:
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

        # Add found attributes to item. Attribute data is a single string.
        item_tree_node['filter-attributes'] = {}
        for attr in TraceableItem.defined_attributes.keys():
            if attr in self.options:
                item_tree_node['filter-attributes'][attr] = self.options[attr]

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

        # Check nocaptions flag
        if 'nocaptions' in self.options:
            item_tree_node['nocaptions'] = True
        elif app.config.traceability_tree_no_captions:
            item_tree_node['nocaptions'] = True
        else:
            item_tree_node['nocaptions'] = False

        return [item_tree_node]
