from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from mlx.traceability_item_element import ItemElement
from mlx.traceable_item import TraceableItem

class ItemList(ItemElement):
    '''List of documentation items'''

    def perform_traceability_replacement(self, app, collection):
        """ Create list with target references. Only items matching list regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        item_ids = collection.get_items(self['filter'], self['filter-attributes'])
        showcaptions = not self['nocaptions']
        top_node = self.create_top_node(self['title'])
        ul_node = nodes.bullet_list()
        for i in item_ids:
            bullet_list_item = nodes.list_item()
            p_node = nodes.paragraph()
            p_node.append(self.make_internal_item_ref(app, i, showcaptions))
            bullet_list_item.append(p_node)
            ul_node.append(bullet_list_item)
        top_node += ul_node
        self.replace_self(top_node)


class ItemListDirective(Directive):
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
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'filter': directives.unchanged,
                   'nocaptions': directives.flag}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        item_list_node = ItemList('')
        item_list_node['document'] = env.docname
        item_list_node['line'] = self.lineno

        # Process title (optional argument)
        if self.arguments:
            item_list_node['title'] = self.arguments[0]
        else:
            item_list_node['title'] = 'List of items'

        # Process ``filter`` option
        if 'filter' in self.options:
            item_list_node['filter'] = self.options['filter']
        else:
            item_list_node['filter'] = ''

        # Add found attributes to item. Attribute data is a single string.
        item_list_node['filter-attributes'] = {}
        for attr in TraceableItem.defined_attributes.keys():
            if attr in self.options:
                item_list_node['filter-attributes'][attr] = self.options[attr]

        # Check nocaptions flag
        if 'nocaptions' in self.options:
            item_list_node['nocaptions'] = True
        elif app.config.traceability_list_no_captions:
            item_list_node['nocaptions'] = True
        else:
            item_list_node['nocaptions'] = False

        return [item_list_node]
