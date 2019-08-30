from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.builders.latex import LaTeXBuilder

from mlx.traceability import report_warning
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class ItemTree(TraceableBaseNode):
    '''Tree-view on documentation items'''

    def perform_replacement(self, app, collection):
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
                    ul_node.append(self._generate_bullet_list_tree(app, collection, i, showcaptions))
            top_node += ul_node
        self.replace_self(top_node)

    def _generate_bullet_list_tree(self, app, collection, item_id, captions=True):
        '''
        Generates a bullet list tree for the given item ID.

        This function returns the given item ID as a bullet item node, makes a child bulleted list, and adds all
        of the matching child items to it.
        '''
        # First add current item_id
        bullet_list_item = nodes.list_item()
        bullet_list_item['id'] = nodes.make_id(item_id)
        p_node = nodes.paragraph()
        p_node.set_class('thumb')
        bullet_list_item.append(p_node)
        bullet_list_item.append(self.make_internal_item_ref(app, item_id, captions))
        bullet_list_item.set_class('has-children')
        bullet_list_item.set_class('collapsed')
        childcontent = nodes.bullet_list()
        childcontent.set_class('bonsai')
        # Then recurse one level, and add dependencies
        for relation in self['type']:
            tgts = collection.get_item(item_id).iter_targets(relation)
            for target in tgts:
                # print('%s has child %s for relation %s' % (item_id, target, relation))
                if collection.get_item(target).attributes_match(self['filter-attributes']):
                    childcontent.append(self._generate_bullet_list_tree(app, collection, target, captions))
        bullet_list_item.append(childcontent)
        return bullet_list_item


class ItemTreeDirective(TraceableBaseDirective):
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
    # Options
    option_spec = {
        'class': directives.class_option,
        'top': directives.unchanged,
        'top_relation_filter': directives.unchanged,  # a string with relationship types separated by space
        'type': directives.unchanged,  # a string with relationship types separated by space
        'nocaptions': directives.flag,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        item_tree_node = ItemTree('')
        item_tree_node['document'] = env.docname
        item_tree_node['line'] = self.lineno

        self.process_title(item_tree_node, 'Tree of items')

        self.process_options(item_tree_node,
                             {'top': '',
                              'top_relation_filter': [],
                              'type': [],
                              })

        self.add_found_attributes(item_tree_node)

        self.check_relationships(item_tree_node['top_relation_filter'], env)

        # Check if given relationships are in configuration
        # Combination of forward + matching reverse relationship cannot be in the same list, as it will give
        # endless treeview (and endless recursion in python --> exception)
        for rel in item_tree_node['type']:
            if rel not in env.traceability_collection.iter_relations():
                report_warning('Traceability: unknown relation for item-tree: %s' % rel, env.docname, self.lineno)
                continue
            if env.traceability_collection.get_reverse_relation(rel) in item_tree_node['type']:
                report_warning('Traceability: combination of forward+reverse relations for item-tree: %s' % rel,
                               env.docname, self.lineno)
                raise ValueError('Traceability: combination of forward+reverse relations for item-tree: %s' % rel)

        self.check_no_captions_flag(item_tree_node, app.config.traceability_tree_no_captions)

        return [item_tree_node]
