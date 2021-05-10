import re
from collections import namedtuple, OrderedDict

from docutils import nodes
from docutils.parsers.rst import directives
from natsort import natsorted

from mlx.traceability_exception import report_warning, TraceabilityException
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


def group_choice(argument):
    """Conversion function for the "group" option."""
    return directives.choice(argument, ('top', 'bottom'))


class ItemMatrix(TraceableBaseNode):
    '''Matrix for cross referencing documentation items'''
    LinkedItems = namedtuple("LinkedItems", "intermediates targets")

    def perform_replacement(self, app, collection):
        """
        Creates table with related items, printing their target references. Only source and target items matching
        respective regexp shall be included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        # The 'target' attribute might be empty, in which case a catch-all is implied. In this case, we set
        # number_of_columns to 2 (one source, one target). In other cases, it's the number of target settings + 1 source
        # column + 1 intermediate column if a title has been configured for it
        show_intermediate = bool(self['intermediatetitle']) and bool(self['intermediate'])
        number_of_columns = max(2, len(self['target']) + 1) + int(show_intermediate)
        Rows = namedtuple('Rows', "sorted covered uncovered")
        source_ids = collection.get_items(self['source'], self['filter-attributes'])
        targets_with_ids = []
        for target_regex in self['target']:
            targets_with_ids.append(collection.get_items(target_regex))
        top_node = self.create_top_node(self['title'])
        table = nodes.table()
        if self.get('classes'):
            table.get('classes').extend(self.get('classes'))
        tgroup = nodes.tgroup()

        # Column and heading setup
        tgroup += [nodes.colspec(colwidth=5) for _ in range(number_of_columns)]
        titles = [self['sourcetitle'], *self['targettitle']]
        if show_intermediate:
            titles.insert(1, self['intermediatetitle'].strip())
        headings = [nodes.entry('', nodes.paragraph('', title)) for title in titles]
        tgroup += nodes.thead('', nodes.row('', *headings))
        table += tgroup

        # External relationships are treated a bit special in item-matrices:
        # - External references are only shown if explicitly requested in the "type" configuration
        # - No target filtering is done on external references
        mapping_via_intermediate = {}
        if not self['type']:
            # if no explicit relationships were given, we consider all of them (except for external ones)
            relationships = [rel for rel in collection.iter_relations() if not self.is_relation_external(rel)]
            external_relationships = []
        else:
            relationships = self['type'].split(' ')
            external_relationships = [rel for rel in relationships if self.is_relation_external(rel)]
            if ' | ' in self['type']:
                mapping_via_intermediate = self.linking_via_intermediate(source_ids, targets_with_ids, collection)

        count_covered = 0
        rows = Rows([], [], [])
        for source_id in source_ids:
            source_item = collection.get_item(source_id)
            if self['sourcetype'] and not source_item.has_relations(self['sourcetype']):
                continue
            covered = False
            left = nodes.entry()
            left += self.make_internal_item_ref(app, source_id)
            rights = [nodes.entry('') for _ in range(number_of_columns - 1)]
            if mapping_via_intermediate:
                covered = source_id in mapping_via_intermediate
                if covered:
                    self.add_all_targets(rights, mapping_via_intermediate[source_id], app,
                                         show_intermediate=show_intermediate)
            else:
                has_external_target = self.add_external_targets(rights, source_item, external_relationships, app)
                has_internal_target = self.add_internal_targets(rights, source_id, targets_with_ids, relationships,
                                                                collection, app)
                covered = has_external_target or has_internal_target

            self._store_row(rows, left, rights, covered, self['onlycovered'])

        if not source_ids:
            # try to use external targets as source
            for ext_rel in external_relationships:
                external_targets = collection.get_external_targets(self['source'], ext_rel)
                # natural sorting on source
                for ext_source, target_ids in OrderedDict(natsorted(external_targets.items())).items():
                    covered = False
                    left = nodes.entry()
                    left += self.make_external_item_ref(app, ext_source, ext_rel)
                    rights = [nodes.entry('') for _ in range(number_of_columns - 1)]
                    covered = self._fill_target_cells(app, rights, target_ids)
                    self._store_row(rows, left, rights, covered, self['onlycovered'])

        tgroup += self._build_table_body(rows, self['group'])

        count_total = len(rows.covered) + len(rows.uncovered)
        count_covered = len(rows.covered)
        try:
            percentage = int(100 * count_covered / count_total)
        except ZeroDivisionError:
            percentage = 0
        disp = 'Statistics: {cover} out of {total} covered: {pct}%'.format(cover=count_covered,
                                                                           total=count_total,
                                                                           pct=percentage)
        if self['stats']:
            if self['onlycovered']:
                disp += ' (uncovered items are hidden)'
            p_node = nodes.paragraph()
            txt = nodes.Text(disp)
            p_node += txt
            top_node += p_node

        top_node += table
        self.replace_self(top_node)

    @staticmethod
    def _build_table_body(rows, group):
        """ Creates the table body and fills it with rows, grouping when desired

        Args:
            rows (Rows): Rows namedtuple object
            group (str): Group option, falsy to disable grouping, 'top' or 'bottom' otherwise

        Returns:
            nodes.tbody: Filled table body
        """
        tbody = nodes.tbody()
        if not group:
            tbody += rows.sorted
        elif group == 'top':
            tbody += rows.uncovered
            tbody += rows.covered
        elif group == 'bottom':
            tbody += rows.covered
            tbody += rows.uncovered
        return tbody

    def add_all_targets(self, rights, linked_items, app, show_intermediate=False):
        """ Adds links to internal targets and, when configured, links to intermediates first

            rights (list): List of empty cells (node.entry) to replace with target links and, when enabled, links to
                intermediates first
            linked_items (LinkedItems): Namedtuple that contains all IDs of intermediate and target items
            app (sphinx.application.Sphinx): Sphinx application object
            show_intermediate (bool): True to add a column for intermediate item(s) per source item
        """
        if show_intermediate:
            for intermediate_id in linked_items.intermediates:
                rights[0] += self.make_internal_item_ref(app, intermediate_id)
        for idx, target_ids in enumerate(linked_items.targets, start=int(show_intermediate)):
            for target_id in target_ids:
                rights[idx] += self.make_internal_item_ref(app, target_id)

    def add_external_targets(self, rights, source_item, external_relationships, app):
        """ Adds links to external targets for given source to the list of target cells

        Args:
            rights (list): List of empty cells (node.entry) to replace with target link(s) when covered
            source_item (TraceableItem): Source item
            external_relationships (list): List of all valid external relationships between source and target(s)
            app (sphinx.application.Sphinx): Sphinx application object

        Returns:
            bool: True if one or more external targets have been found for the given source item, False otherwise
        """
        has_external_target = False
        for external_relationship in external_relationships:
            for target_id in source_item.iter_targets(external_relationship):
                ext_item_ref = self.make_external_item_ref(app, target_id, external_relationship)
                for right in rights:
                    right += ext_item_ref
                has_external_target = True
        return has_external_target

    def add_internal_targets(self, rights, source_id, targets_with_ids, relationships, collection, app):
        """ Adds links to internal targets for given source to the list of target cells

        Args:
            rights (list): List of empty cells (node.entry) to replace with target link(s) when covered
            source_id (str): Item ID of source item
            targets_with_ids (list): List of lists per target, listing target IDs to take into consideration
            relationships (list): List of all valid relationships between source and target(s)
            collection (TraceableCollection): Collection of TraceableItems
            app (sphinx.application.Sphinx): Sphinx application object

        Returns:
            bool: True if one or more internal targets have been found for the given source item, False otherwise
        """
        has_internal_target = False
        for idx, target_ids in enumerate(targets_with_ids):
            for target_id in target_ids:
                if collection.are_related(source_id, relationships, target_id):
                    rights[idx] += self.make_internal_item_ref(app, target_id)
                    has_internal_target = True
        return has_internal_target

    def linking_via_intermediate(self, source_ids, targets_with_ids, collection):
        """ Maps source IDs to IDs of target items that are linked via an itermediate item per target

        Only covered source IDs are stored.

        Args:
            source_ids (list): List of item IDs of source items
            targets_with_ids (list): List of lists per target, listing target IDs to take into consideration
            collection (TraceableCollection): Collection of TraceableItems

        Returns:
            dict: Mapping of source IDs as key with as value a namedtuple that contains intermediate
                and target item IDs (set)
        """
        links_with_relationships = []
        for relationships_str in self['type'].split(' | '):
            links_with_relationships.append(relationships_str.split(' '))
        if len(links_with_relationships) > 2:
            raise TraceabilityException("Type option of item-matrix must not contain more than one '|' "
                                        "character; got {}".format(self['type']),
                                        docname=self["document"])
        # reverse relationship(s) specified for linking source to intermediate
        for idx, rel in enumerate(links_with_relationships[0]):
            links_with_relationships[0][idx] = collection.get_reverse_relation(rel)

        source_to_links_map = {}
        excluded_source_ids = set()
        for intermediate_id in collection.get_items(self['intermediate'], sort=bool(self['intermediatetitle'])):
            intermediate_item = collection.get_item(intermediate_id)

            potential_source_ids = set()
            for reverse_rel in links_with_relationships[0]:
                potential_source_ids.update(intermediate_item.iter_targets(reverse_rel, sort=False))
            # apply :source: filter
            potential_source_ids = potential_source_ids.intersection(source_ids)
            potential_source_ids = potential_source_ids.difference(excluded_source_ids)
            if not potential_source_ids:
                continue

            potential_target_ids = set()
            for forward_rel in links_with_relationships[1]:
                potential_target_ids.update(intermediate_item.iter_targets(forward_rel, sort=False))
            if not potential_target_ids:
                if self['coveredintermediates']:
                    excluded_source_ids.update(potential_source_ids)
                continue
            # apply :target: filter
            covered = False
            actual_targets = []
            for target_ids in targets_with_ids:
                linked_target_ids = potential_target_ids.intersection(target_ids)
                if linked_target_ids:
                    covered = True
                actual_targets.append(linked_target_ids)

            if covered:
                self._store_targets(source_to_links_map, potential_source_ids, actual_targets, intermediate_id)
            elif self['coveredintermediates']:
                excluded_source_ids.update(potential_source_ids)
        for source_id in excluded_source_ids:
            source_to_links_map.pop(source_id, None)
        return source_to_links_map

    def _store_targets(self, source_to_links_map, source_ids, targets_with_ids, intermediate_id):
        """ Extends given mapping with target IDs per target as value for each source ID as key

        Args:
            source_to_links_map (dict): Mapping of source IDs as key with as value a namedtuple that contains
                intermediate and target item IDs (set)
            source_ids (set): Source IDs to store targets for
            targets_with_ids (list): List of linked target item IDs (set) per target
            intermediate_id (str): ID of intermediate item that links the given source items to the given target items
        """
        for source_id in source_ids:
            if source_id not in source_to_links_map:
                source_to_links_map[source_id] = self.LinkedItems([intermediate_id], targets_with_ids)
            else:
                source_to_links_map[source_id].intermediates.append(intermediate_id)
                for idx, target_ids in enumerate(targets_with_ids):
                    source_to_links_map[source_id].targets[idx].update(target_ids)

    @staticmethod
    def _store_row(rows, left, rights, covered, onlycovered):
        """ Stores the leftmost cell and righthand cells in a row in the given Rows object.

        Args:
            rows (Rows): Rows namedtuple object to extend
            left (nodes.entry): Leftmost cell, to be added to the row first
            rights (list[nodes.entry]): List of cells, to be added to the row last
            covered (bool): True if the row shall be stored in the covered attribute, False for uncovered attribute
            onlycovered (bool): True if rows with an uncovered source item shall not be added to the sorted rows attr,
                False to add all rows
        """
        row = nodes.row()
        row += left
        row += rights

        if covered:
            rows.covered.append(row)
            rows.sorted.append(row)
        else:
            rows.uncovered.append(row)
            if not onlycovered:
                rows.sorted.append(row)

    def _fill_target_cells(self, app, target_cells, item_ids):
        """ Fills target cells with linked items, filtered by target option.

        Returns whether the source has been covered or not.

        Args:
            app: Sphinx application object to use
            target_cells (list): List of empty cells
            item_ids (list): List of item IDs

        Returns:
            bool: True if a target cell contains an item, False otherwise
        """
        covered = False
        for idx, target_regex in enumerate(self['target']):
            for target_id in item_ids:
                if re.match(target_regex, target_id):
                    target_cells[idx] += self.make_internal_item_ref(app, target_id)
                    covered = True
        return covered


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
         :sourcetype: <<relationship>> ...
         :group: top | bottom
         :onlycovered:
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
        'intermediate': directives.unchanged,
        'targettitle': directives.unchanged,
        'sourcetitle': directives.unchanged,
        'intermediatetitle': directives.unchanged,
        'type': directives.unchanged,  # a string with relationship types separated by space
        'sourcetype': directives.unchanged,  # a string with relationship types separated by space
        'group': group_choice,
        'onlycovered': directives.flag,
        'coveredintermediates': directives.flag,
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

        self.process_options(
            item_matrix_node,
            {
                'target':            {'default': ['']},
                'intermediate':      {'default': ''},
                'source':            {'default': ''},
                'targettitle':       {'default': ['Target'], 'delimiter': ','},
                'sourcetitle':       {'default': 'Source'},
                'intermediatetitle': {'default': ''},
                'type':              {'default': ''},
                'sourcetype':        {'default': []},
            },
        )

        if item_matrix_node['intermediate'] and ' | ' not in item_matrix_node['type']:
            raise TraceabilityException("The :intermediate: option is used, expected at least two relationships "
                                        "separated by ' | ' in the :type: option; got {!r}"
                                        .format(item_matrix_node['type']),
                                        docname=env.docname)

        # Process ``group`` option, given as a string that is either top or bottom or empty ().
        item_matrix_node['group'] = self.options.get('group', '')

        number_of_targets = len(item_matrix_node['target'])
        number_of_targettitles = len(item_matrix_node['targettitle'])
        if number_of_targets > 1 and number_of_targets != number_of_targettitles:
            report_warning("Item-matrix directive should have the same number of 'target' attributes as 'target-title' "
                           "attributes. Got target: {targets} and targettitle: {titles}"
                           .format(targets=item_matrix_node['target'], titles=item_matrix_node['targettitle']),
                           env.docname, self.lineno)

        if item_matrix_node['type']:
            self.check_relationships(item_matrix_node['type'].replace(' | ', ' ').split(' '), env)
        self.check_relationships(item_matrix_node['sourcetype'], env)

        self.check_option_presence(item_matrix_node, 'onlycovered')
        self.check_option_presence(item_matrix_node, 'coveredintermediates')
        self.check_option_presence(item_matrix_node, 'stats')

        self.check_caption_flags(item_matrix_node, app.config.traceability_matrix_no_captions)

        return [item_matrix_node]
