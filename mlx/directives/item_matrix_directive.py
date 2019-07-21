from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode, REGEXP_EXTERNAL_RELATIONSHIP


class ItemMatrix(TraceableBaseNode):
    '''Matrix for cross referencing documentation items'''

    def perform_replacement(self, app, collection):
        """
        Creates table with related items, printing their target references. Only source and target items matching
        respective regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        showcaptions = not self['nocaptions']
        source_ids = collection.get_items(self['source'], self['filter-attributes'])
        target_ids = collection.get_items(self['target'])
        top_node = self.create_top_node(self['title'])
        table = nodes.table()
        if self.get('classes'):
            table.get('classes').extend(self.get('classes'))
        tgroup = nodes.tgroup()
        left_colspec = nodes.colspec(colwidth=5)
        right_colspec = nodes.colspec(colwidth=5)
        tgroup += [left_colspec, right_colspec]
        tgroup += nodes.thead('', nodes.row(
            '',
            nodes.entry('', nodes.paragraph('', self['sourcetitle'])),
            nodes.entry('', nodes.paragraph('', self['targettitle']))))
        tbody = nodes.tbody()
        tgroup += tbody
        table += tgroup

        relationships = self['type']
        if not relationships:
            relationships = collection.iter_relations()

        count_total = 0
        count_covered = 0

        for source_id in source_ids:
            source_item = collection.get_item(source_id)
            count_total += 1
            covered = False
            row = nodes.row()
            left = nodes.entry()
            left += self.make_internal_item_ref(app, source_id, showcaptions)
            right = nodes.entry()
            for relationship in relationships:
                if REGEXP_EXTERNAL_RELATIONSHIP.search(relationship):
                    for target_id in source_item.iter_targets(relationship):
                        right += self.make_external_item_ref(app, target_id, relationship)
                        covered = True
            for target_id in target_ids:
                if collection.are_related(source_id, relationships, target_id):
                    right += self.make_internal_item_ref(app, target_id, showcaptions)
                    covered = True
            if covered:
                count_covered += 1
            row += left
            row += right
            tbody += row

        try:
            percentage = int(100 * count_covered / count_total)
        except ZeroDivisionError:
            percentage = 0
        disp = 'Statistics: {cover} out of {total} covered: {pct}%'.format(cover=count_covered,
                                                                           total=count_total,
                                                                           pct=percentage)
        if self['stats']:
            p_node = nodes.paragraph()
            txt = nodes.Text(disp)
            p_node += txt
            top_node += p_node

        top_node += table
        self.replace_self(top_node)


class ItemMatrixDirective(TraceableBaseDirective):
    """
    Directive to generate a matrix of item cross-references, based on
    a given set of relationship types.

    Syntax::

      .. item-matrix:: title
         :target: regexp
         :source: regexp
         :<<attribute>>: regexp
         :targettitle: Target column header
         :sourcetitle: Source column header
         :type: <<relationship>> ...
         :stats:
         :nocaptions:
    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'class': directives.class_option,
        'target': directives.unchanged,
        'source': directives.unchanged,
        'targettitle': directives.unchanged,
        'sourcetitle': directives.unchanged,
        'type': directives.unchanged,  # a string with relationship types separated by space
        'stats': directives.flag,
        'nocaptions': directives.flag,
    }
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        item_matrix_node = ItemMatrix('')
        item_matrix_node['document'] = env.docname
        item_matrix_node['line'] = self.lineno

        if self.options.get('class'):
            item_matrix_node.get('classes').extend(self.options.get('class'))

        self.process_title(item_matrix_node, 'Traceability matrix of items')

        self.add_found_attributes(item_matrix_node)

        self.process_options(item_matrix_node,
                             {'target': '',
                              'source': '',
                              'targettitle': 'Target',
                              'sourcetitle': 'Source',
                              'type': [],
                              })

        self.check_relationships(item_matrix_node['type'], env)

        self.check_option_presence(item_matrix_node, 'stats')

        self.check_no_captions_flag(item_matrix_node, app.config.traceability_matrix_no_captions)

        return [item_matrix_node]
