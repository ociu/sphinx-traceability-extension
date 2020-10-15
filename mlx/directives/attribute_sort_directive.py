from docutils.parsers.rst import directives

from mlx.traceability import report_warning
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class AttributeSort(TraceableBaseNode):
    """Node that configures the order of filtered items' attributes in the generated output."""

    def perform_replacement(self, app, collection):
        """ Processes the attribute-sort items.

        The AttributeSort node has no final representation, so it is removed from the tree.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        ignored_items = collection.add_attribute_sorting_rule(self['filter'], self['sort'])
        for item in ignored_items:
            report_warning("The sorting of the attributes of item {} has already been configured by {}; ignoring {}"
                           .format(item.id, item.attribute_order, self['sort']), self['document'], self['line'])
        self.replace_self([])


class AttributeSortDirective(TraceableBaseDirective):
    """
    Directive to store the configuration of the order of filtered items' attributes.

    The node will be responsible for applying the configuration to the Item. First, all directives must be parsed.

    Syntax::

      .. attribute-sort::
         :filter: regex
         :sort: list_of_attributes
    """
    # Options
    option_spec = {
        'filter': directives.unchanged,
        'sort': directives.unchanged,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. Just store the configuration. """
        env = self.state.document.settings.env

        node = AttributeSort('')
        node['document'] = env.docname
        node['line'] = self.lineno

        self.process_options(
            node,
            {
                'sort':   {'default': []},
                'filter': {'default': r"\S+"},
            },
        )
        return [node]
