from docutils.parsers.rst import directives

from mlx.traceability import report_warning
from mlx.traceability_exception import TraceabilityException
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class ItemLink(TraceableBaseNode):
    '''Linking of documentation items'''

    def perform_replacement(self, app, collection):
        """ Processes the item-link items. The ItemLink node has no final representation, so is removed from the tree.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        self.replace_self([])


class ItemLinkDirective(TraceableBaseDirective):
    """
    Directive to add additional relations between lists of items.

    Syntax::

      .. item-link::
         :sources: list_of_items
         :targets: list_of_items
         :type: relationship_type

    """
    # Options
    option_spec = {
        'sources': directives.unchanged,
        'targets': directives.unchanged,
        'type': directives.unchanged,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env

        node = ItemLink('')
        node['document'] = env.docname
        node['line'] = self.lineno

        process_options_success = self.process_options(
            node,
            {
                'sources': {'default': []},
                'targets': {'default': []},
                'type':    {'default': ''},
            },
            docname=env.docname
        )
        if not process_options_success:
            return []

        # Processing of the item-link items. They get added as additional relationships
        # to the existing items. Should be done before converting anything to docutils.
        for source in node['sources']:
            for target in node['targets']:
                try:
                    env.traceability_collection.add_relation(source, node['type'], target)
                except TraceabilityException as err:
                    report_warning(err, env.docname, self.lineno)

        # The ItemLink node has no final representation, so is removed from the tree
        return [node]
