from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class ItemList(TraceableBaseNode):
    '''List of documentation items'''

    def perform_replacement(self, app, collection):
        """ Create list with target references. Only items matching list regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        item_ids = collection.get_items(self['filter'], self['filter-attributes'])
        showcaptions = not self['nocaptions']
        top_node = self.create_top_node(self['title'])
        if item_ids:
            ul_node = nodes.bullet_list()
            for i in item_ids:
                bullet_list_item = nodes.list_item()
                p_node = nodes.paragraph()
                p_node.append(self.make_internal_item_ref(app, i, showcaptions))
                bullet_list_item.append(p_node)
                ul_node.append(bullet_list_item)
            top_node += ul_node
        self.replace_self(top_node)


class ItemListDirective(TraceableBaseDirective):
    """
    Directive to generate a list of items.

    Syntax::

      .. item-list:: title
         :filter: regexp
         :<<attribute>>: regexp
         :nocaptions:

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'class': directives.class_option,
        'filter': directives.unchanged,
        'nocaptions': directives.flag,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        item_list_node = ItemList('')
        item_list_node['document'] = env.docname
        item_list_node['line'] = self.lineno

        self.process_title(item_list_node, 'List of items')

        # Process ``filter`` option
        self.process_options(item_list_node, {'filter': ''})

        self.add_found_attributes(item_list_node)

        self.check_no_captions_flag(item_list_node, app.config.traceability_list_no_captions)

        return [item_list_node]
