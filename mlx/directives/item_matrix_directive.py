from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from mlx.traceability import report_warning
from mlx.traceability_item_element import ItemElement, REGEXP_EXTERNAL_RELATIONSHIP
from mlx.traceable_item import TraceableItem

class ItemMatrix(ItemElement):
    '''Matrix for cross referencing documentation items'''

    def perform_traceability_replacement(self, app, collection):
        """
        Creates table with related items, printing their target references. Only source and target items matching
        respective regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        env = app.builder.env
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


class ItemMatrixDirective(Directive):
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
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'target': directives.unchanged,
                   'source': directives.unchanged,
                   'targettitle': directives.unchanged,
                   'sourcetitle': directives.unchanged,
                   'type': directives.unchanged,
                   'stats': directives.flag,
                   'nocaptions': directives.flag}
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

        # Process title (optional argument)
        if self.arguments:
            item_matrix_node['title'] = self.arguments[0]
        else:
            item_matrix_node['title'] = 'Traceability matrix of items'

        # Add found attributes to item. Attribute data is a single string.
        item_matrix_node['filter-attributes'] = {}
        for attr in TraceableItem.defined_attributes.keys():
            if attr in self.options:
                item_matrix_node['filter-attributes'][attr] = self.options[attr]

        # Process ``target`` & ``source`` options
        for option in ('target', 'source'):
            if option in self.options:
                item_matrix_node[option] = self.options[option]
            else:
                item_matrix_node[option] = ''

        # Process ``type`` option, given as a string with relationship types
        # separated by space. It is converted to a list.
        if 'type' in self.options:
            item_matrix_node['type'] = self.options['type'].split()
        else:
            item_matrix_node['type'] = []

        # Check if given relationships are in configuration
        for rel in item_matrix_node['type']:
            if rel not in env.traceability_collection.iter_relations():
                report_warning(env, 'Traceability: unknown relation for item-matrix: %s' % rel,
                               env.docname, self.lineno)

        # Check statistics flag
        if 'stats' in self.options:
            item_matrix_node['stats'] = True
        else:
            item_matrix_node['stats'] = False

        # Check nocaptions flag
        if 'nocaptions' in self.options:
            item_matrix_node['nocaptions'] = True
        elif app.config.traceability_matrix_no_captions:
            item_matrix_node['nocaptions'] = True
        else:
            item_matrix_node['nocaptions'] = False

        # Check source title
        if 'sourcetitle' in self.options:
            item_matrix_node['sourcetitle'] = self.options['sourcetitle']
        else:
            item_matrix_node['sourcetitle'] = 'Source'

        # Check target title
        if 'targettitle' in self.options:
            item_matrix_node['targettitle'] = self.options['targettitle']
        else:
            item_matrix_node['targettitle'] = 'Target'

        return [item_matrix_node]
