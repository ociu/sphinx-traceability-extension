from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from mlx.traceability import report_warning
from mlx.traceability_exception import TraceabilityException
from mlx.traceability_item_element import ItemElement

class ItemLink(ItemElement):
    '''List of documentation items'''

    def perform_traceability_replacement(self, app, collection):
        """ Processes the item-link items. The ItemLink node has no final representation, so is removed from the tree.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        self.replace_self([])


class ItemLinkDirective(Directive):
    """
    Directive to add additional relations between lists of items.

    Syntax::

      .. item-link::
         :sources: list_of_items
         :targets: list_of_items
         :type: relationship_type

    """
    final_argument_whitespace = True
    # Options
    option_spec = {'sources': directives.unchanged,
                   'targets': directives.unchanged,
                   'type': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        node = ItemLink('')
        node['document'] = env.docname
        node['line'] = self.lineno
        node['sources'] = []
        node['targets'] = []
        node['type'] = None

        if 'sources' in self.options:
            node['sources'] = self.options['sources'].split()
        else:
            report_warning(env, 'sources argument required for item-link directive', env.docname, self.lineno)
            return []
        if 'targets' in self.options:
            node['targets'] = self.options['targets'].split()
        else:
            report_warning(env, 'targets argument required for item-link directive', env.docname, self.lineno)
            return []
        if 'type' in self.options:
            node['type'] = self.options['type']
        else:
            report_warning(env, 'type argument required for item-link directive', env.docname, self.lineno)
            return []

        # Processing of the item-link items. They get added as additional relationships
        # to the existing items. Should be done before converting anything to docutils.
        for source in node['sources']:
            for target in node['targets']:
                try:
                    env.traceability_collection.add_relation(source, node['type'], target)
                except TraceabilityException as err:
                    report_warning(env, err, env.docname, self.lineno)

        # The ItemLink node has no final representation, so is removed from the tree
        return [node]
