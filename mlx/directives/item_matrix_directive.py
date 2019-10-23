from collections import namedtuple
from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceability_exception import report_warning
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
        Rows = namedtuple('Rows', "covered uncovered")
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
        rows_container = Rows([], [])
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

            row += left
            row += right

            if covered:
                count_covered += 1
                rows_container.covered.append(row)
            else:
                rows_container.uncovered.append(row)

            if not self['group']:
                tbody += row

        if self['group'] == 'top':
            tbody += rows_container.uncovered
            tbody += rows_container.covered
        elif self['group'] == 'bottom':
            tbody += rows_container.covered
            tbody += rows_container.uncovered

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
         :group: top | bottom
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
        'group': directives.unchanged,
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

        # Process ``group`` option, given as a string that is either top or bottom or empty ().
        if 'group' in self.options:
            group_attr = self.options['group']
            if group_attr == 'bottom':
                item_matrix_node['group'] = 'bottom'
            else:
                if group_attr and group_attr != 'top':
                    report_warning("Argument for 'group' attribute should be 'top' or 'bottom'; got '{}'. "
                                   "Using default 'top'.".format(group_attr), env.docname, self.lineno)
                item_matrix_node['group'] = 'top'
        else:
            item_matrix_node['group'] = ''

        self.check_relationships(item_matrix_node['type'], env)

        self.check_option_presence(item_matrix_node, 'stats')

        self.check_no_captions_flag(item_matrix_node, app.config.traceability_matrix_no_captions)

        return [item_matrix_node]
