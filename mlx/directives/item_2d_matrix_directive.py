from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class Item2DMatrix(TraceableBaseNode):
    '''Matrix for cross referencing documentation items in 2 dimensions'''

    def perform_replacement(self, app, collection):
        """
        Creates table with related items, printing their target references. Only source and target items matching
        respective regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        source_ids = collection.get_items(self['source'], self['filter-attributes'])
        target_ids = collection.get_items(self['target'])
        top_node = self.create_top_node(self['title'])
        table = nodes.table()
        if self.get('classes'):
            table.get('classes').extend(self.get('classes'))
        tgroup = nodes.tgroup()
        colspecs = [nodes.colspec(colwidth=5)]
        hrow = nodes.row('', nodes.entry('', nodes.paragraph('', '')))
        for source_id in source_ids:
            colspecs.append(nodes.colspec(colwidth=5))
            src_cell = self.make_internal_item_ref(app, source_id, False)
            hrow.append(nodes.entry('', src_cell))
        tgroup += colspecs
        tgroup += nodes.thead('', hrow)
        tbody = nodes.tbody()
        for target_id in target_ids:
            row = nodes.row()
            tgt_cell = nodes.entry()
            tgt_cell += self.make_internal_item_ref(app, target_id, False)
            row += tgt_cell
            for source_id in source_ids:
                cell = nodes.entry()
                p_node = nodes.paragraph()
                if collection.are_related(source_id, self['type'], target_id):
                    txt = self['hit']
                else:
                    txt = self['miss']
                p_node += nodes.Text(txt)
                cell += p_node
                row += cell
            tbody += row
        tgroup += tbody
        table += tgroup
        top_node += table
        self.replace_self(top_node)


class Item2DMatrixDirective(TraceableBaseDirective):
    """
    Directive to generate a 2D-matrix of item cross-references, based on
    a given set of relationship types.

    Syntax::

      .. item-2d-matrix:: title
         :target: regexp
         :source: regexp
         :<<attribute>>: regexp
         :type: <<relationship>> ...

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'class': directives.class_option,
        'target': directives.unchanged,
        'source': directives.unchanged,
        'hit': directives.unchanged,
        'miss': directives.unchanged,
        'type': directives.unchanged,  # a string with relationship types separated by space
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env

        node = Item2DMatrix('')
        node['document'] = env.docname
        node['line'] = self.lineno

        if self.options.get('class'):
            node.get('classes').extend(self.options.get('class'))

        self.process_title(node, '2D traceability matrix of items')

        self.process_options(node,
                             {'target': '',
                              'source': '',
                              'type': [],
                              'hit': 'x',
                              'miss': '',
                              })

        self.add_found_attributes(node)

        self.check_relationships(node['type'], env)

        return [node]
