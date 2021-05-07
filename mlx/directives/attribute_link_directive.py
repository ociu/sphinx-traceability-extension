from docutils.parsers.rst import directives

from mlx.traceability_exception import TraceabilityException, report_warning
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class AttributeLink(TraceableBaseNode):
    """Node that adds one or more attributes to one or more items."""

    def perform_replacement(self, app, collection):
        """ Processes the attribute-link items.

        The AttributeLink node has no final representation, so it is removed from the tree.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        filtered_item_ids = collection.get_items(self['filter'])
        for attribute, value in self['filter-attributes'].items():
            for item_id in filtered_item_ids:
                item = collection.get_item(item_id)
                try:
                    item.add_attribute(attribute, value)
                except TraceabilityException as err:
                    report_warning(err, self['document'], self['line'])
        self.replace_self([])


class AttributeLinkDirective(TraceableBaseDirective):
    """ Directive to add attributes to items outside of the items' definition.

    The node will be responsible for applying the configuration to the Item. First, all directives must be parsed.

    Syntax::

      .. attribute-link::
         :filter: regex
         :<<attribute>>: attribute_value
    """
    # Options
    option_spec = {
        'filter': directives.unchanged,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. Just store the configuration. """
        env = self.state.document.settings.env

        node = AttributeLink('')
        node['document'] = env.docname
        node['line'] = self.lineno

        self.process_options(
            node,
            {
                'filter': {'default': r"\S+"},
            },
        )
        node['filter'] = node['filter'].replace('\n', '').strip()
        self.add_found_attributes(node)

        return [node]
