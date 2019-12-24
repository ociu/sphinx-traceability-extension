import re
from hashlib import sha256
from os import environ, mkdir, path

from docutils import nodes
from docutils.parsers.rst import directives
import matplotlib as mpl
if not environ.get('DISPLAY'):
    mpl.use('Agg')
import matplotlib.pyplot as plt  # pylint: disable=wrong-import-order

from mlx.traceability import report_warning
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode
from mlx.traceable_item import TraceableItem


def pct_wrapper(sizes):
    """ Helper function for matplotlib which returns the percentage and the absolute size of the slice.

    Args:
        sizes (list): List containing the amount of elements per slice.
    """
    def make_pct(pct):
        absolute = int(round(pct / 100 * sum(sizes)))
        return "{:.0f}%\n({:d})".format(pct, absolute)
    return make_pct


class ItemPieChart(TraceableBaseNode):
    '''Pie chart on documentation items'''
    collection = None
    relationships = []
    priorities = {}  # default priority order is 'uncovered', 'covered', 'executed', 'pass', 'fail', 'error'
    attribute_id = ''
    linked_attributes = {}  # source_id (str): attr_value (str)

    def perform_replacement(self, app, collection):
        """
        Very similar to item-matrix: but instead of creating a table, the empty cells in the right column are counted.
        Generates a pie chart with coverage percentages. Only items matching regexp in ``id_set`` option shall be
        included.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        env = app.builder.env
        top_node = self.create_top_node(self['title'])
        self.collection = collection
        self.relationships = self.collection.iter_relations()
        self._set_priorities()
        self._set_attribute_id()

        for source_id in self.collection.get_items(''):
            source_item = self.collection.get_item(source_id)
            # placeholders don't end up in any item-piechart (less duplicate warnings for missing items)
            if source_item.is_placeholder():
                continue
            if re.match(self['id_set'][0], source_id):
                self.linked_attributes[source_id] = self['label_set'][0].lower()  # default is "uncovered"
                self.loop_relationships(source_id, source_item, self['id_set'][1], self._match_covered)

        chart_labels, statistics = self._prepare_labels_and_values(list(self.priorities),
                                                                   list(self.linked_attributes.values()))
        p_node = nodes.paragraph()
        p_node += nodes.Text(statistics)
        p_node += self.build_pie_chart(chart_labels, env)
        top_node += p_node
        self.replace_self(top_node)

    def _set_priorities(self):
        """ Initializes the priorities dictionary with labels as keys and priority numbers as values. """
        for idx, label in enumerate(self['label_set']):
            self.priorities[label] = idx
        # store :<<attribute>>: arguments in reverse order in lowercase for case-insensitivity
        if self['priorities']:
            for idx, attr in enumerate([value.lower() for value in self['priorities'][::-1]],
                                       start=len(self['label_set'])):
                self.priorities[attr] = idx

    def _set_attribute_id(self):
        """ Sets the attribute_id if a third item ID in the id_set option is given. """
        if len(self['id_set']) > 2:
            self.attribute_id = self['id_set'][2]

    def loop_relationships(self, top_source_id, source_item, pattern, match_function):
        """
        Loops through all relationships and for each relationship it loops through the matches that have been found
        for the source item. If the matched item is not a placeholder and matches to the specified pattern, the
        specified function is called with the matched item as a parameter.

        Args:
            top_source_id (str): Item identifier of the top source item.
            source_item (TraceableItem): Traceable item to be used as a source for the relationship search.
            pattern (str): Regexp pattern string to be used on items that have a relationship to the source item.
            match_function (func): Function to be called when the regular expression hits.
        """
        for relationship in self.relationships:
            for target_id in source_item.iter_targets(relationship, True, True):
                target_item = self.collection.get_item(target_id)
                # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
                if not target_item or target_item.is_placeholder():
                    continue
                if re.match(pattern, target_id):
                    match_function(top_source_id, target_item)

    def _match_covered(self, top_source_id, nested_source_item):
        """
        Sets the appropriate label when the top-level relationship is accounted for. If the <<attribute>> option is
        used, it loops through all relationships again, this time with the matched item as the source.

        Args:
            top_source_id (str): Identifier of the top source item, e.g. requirement identifier.
            nested_source_item (TraceableItem): Nested traceable item to be used as a source for looping through its
                relationships, e.g. a test item.
        """
        self.linked_attributes[top_source_id] = self['label_set'][1].lower()  # default is "covered"
        if self.attribute_id:
            self.loop_relationships(top_source_id, nested_source_item, self.attribute_id, self._match_attribute_values)

    def _match_attribute_values(self, top_source_id, nested_target_item):
        """ Links the highest priority attribute value of nested relations to the top source id.

        This function is only called when the <<attribute>> option is used. It gets the attribute value from the nested
        target item and stores it as value in the dict `linked_attributes` with the top source id as key, but only if
        the priority of the attribute value is higher than what's already been stored.

        Args:
            top_source_id (str): Identifier of the top source item, e.g. requirement identifier.
            nested_target_item (TraceableItem): Nested traceable item used as a target while looping through
                relationships, e.g. a test report item.
        """
        # case-insensitivity
        attribute_value = nested_target_item.get_attribute(self['attribute']).lower()
        if attribute_value not in self.priorities:
            attribute_value = self['label_set'][2].lower()  # default is "executed"

        if top_source_id not in self.linked_attributes:
            self.linked_attributes[top_source_id] = attribute_value
        else:
            # store newly encountered attribute value if it has a higher priority
            stored_attribute_priority = self.priorities[self.linked_attributes[top_source_id]]
            latest_attribute_priority = self.priorities[attribute_value]
            if latest_attribute_priority > stored_attribute_priority:
                self.linked_attributes[top_source_id] = attribute_value

    def _prepare_labels_and_values(self, lower_labels, attributes):
        """ Keeps case-sensitivity of :<<attribute>>: arguments in labels and calculates slice size based on the
        highest-priority label for each relevant item.

        Args:
            lower_labels (list): List of unique lower-case labels (str).
            attributes (list): List of labels with the highest priority for each relevant item.

        Returns:
            (dict) Dictionary containing the slice labels as keys and slice sizes (int) as values.
            (str) Coverage statistics.
        """
        # initialize dictionary for each possible value, and count label occurences
        chart_labels = {}
        for label in lower_labels:
            chart_labels[label] = 0
        for attribute in attributes:
            chart_labels[attribute] += 1

        # get statistics before removing any labels with value 0
        statistics = self._get_statistics(chart_labels[self['label_set'][0]], len(attributes))
        # removes labels with count value equal to 0
        chart_labels = {k: v for k, v in chart_labels.items() if v}
        for priority in self['priorities']:
            if priority.lower() in chart_labels:
                value = chart_labels.pop(priority.lower())
                chart_labels[priority] = value
        return chart_labels, statistics

    @staticmethod
    def _get_statistics(count_uncovered, count_total):
        """ Returns the coverage statistics based in the number of uncovered items and total number of items.

        Args:
            count_uncovered (int): The number of uncovered items.
            count_total (int): The total number of items.

        Returns:
            (str) Coverage statistics in string representation.
        """
        count_covered = count_total - count_uncovered
        try:
            percentage = int(100 * count_covered / count_total)
        except ZeroDivisionError:
            percentage = 0
        return 'Statistics: {cover} out of {total} covered: {pct}%'.format(cover=count_covered,
                                                                           total=count_total,
                                                                           pct=percentage,)

    def build_pie_chart(self, chart_labels, env):
        """
        Builds and returns image node containing the pie chart image.

        Args:
            chart_labels (dict): Dictionary containing the slice labels as keys and slice sizes (int) as values.
            env (sphinx.environment.BuildEnvironment): Sphinx' build environment.

        Returns:
            (nodes.image) Image node containing the pie chart image.
        """
        labels = list(chart_labels)
        sizes = list(chart_labels.values())
        explode = [0] * len(labels)
        uncoverd_index = labels.index(self['label_set'][0])
        explode[uncoverd_index] = 0.05  # slightly detaches slice of first state, default is "uncovered"

        fig, axes = plt.subplots()
        axes.pie(sizes, explode=explode, labels=labels, autopct=pct_wrapper(sizes), startangle=90)
        axes.axis('equal')
        folder_name = path.join(env.app.srcdir, '_images')
        if not path.exists(folder_name):
            mkdir(folder_name)
        hash_string = ''
        for pie_slice in axes.__dict__['texts']:
            hash_string += str(pie_slice)
        hash_value = sha256(hash_string.encode()).hexdigest()  # create hash value based on chart parameters
        rel_file_path = path.join('_images', 'piechart-{}.png'.format(hash_value))
        if rel_file_path not in env.images:
            fig.savefig(path.join(env.app.srcdir, rel_file_path), format='png')
            env.images[rel_file_path] = ['_images', path.split(rel_file_path)[-1]]  # store file name in build env

        image_node = nodes.image()
        image_node['uri'] = rel_file_path
        image_node['candidates'] = '*'  # look at uri value for source path, relative to the srcdir folder
        return image_node


class ItemPieChartDirective(TraceableBaseDirective):
    """
    Directive to generate a pie chart for coverage of item cross-references.

    Syntax::

      .. item-piechart:: title
         :id_set: source_regexp target_regexp (nested_target_regexp)
         :label_set: uncovered, covered(, executed)
         :<<attribute>>: error, fail, pass ...

    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'class': directives.class_option,
        'id_set': directives.unchanged,
        'label_set': directives.unchanged,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env

        item_chart_node = ItemPieChart('')
        item_chart_node['document'] = env.docname
        item_chart_node['line'] = self.lineno

        self.process_title(item_chart_node)

        self._process_id_set(item_chart_node)

        self._process_label_set(item_chart_node)

        self._process_attribute(item_chart_node)

        return [item_chart_node]

    def _process_id_set(self, node):
        """ Processes id_set option. At least two arguments are required. Otherwise, a warning is reported. """
        if 'id_set' in self.options and len(self.options['id_set'].split()) >= 2:
            self._warn_if_comma_separated('id_set', node['document'])
            node['id_set'] = self.options['id_set'].split()
        else:
            node['id_set'] = []
            report_warning('Traceability: Expected at least two arguments in id_set.',
                           node['document'],
                           node['line'])

    def _process_label_set(self, node):
        """ Processes label_set option. If not (fully) used, default labels are used. """
        default_labels = ['uncovered', 'covered', 'executed']
        if 'label_set' in self.options:
            node['label_set'] = [x.strip(' ') for x in self.options['label_set'].split(',')]
            if len(node['label_set']) != len(node['id_set']):
                node['label_set'].extend(
                    default_labels[len(node['label_set']):len(node['id_set'])])
        else:
            id_amount = len(node['id_set'])
            node['label_set'] = default_labels[:id_amount]  # default labels

    def _process_attribute(self, node):
        """
        Processes the <<attribute>> option. Attribute data is a comma-separated list of attribute values.
        A warning is reported when this option is given while the id_set does not contan 3 IDs.
        """
        node['attribute'] = ''
        node['priorities'] = []
        for attr in TraceableItem.defined_attributes:
            if attr in self.options:
                if len(node['id_set']) == 3:
                    node['attribute'] = attr
                    node['priorities'] = [x.strip(' ') for x in self.options[attr].split(',')]
                else:
                    report_warning('Traceability: The <<attribute>> option is only viable with an id_set with 3 '
                                   'arguments.',
                                   node['document'],
                                   node['line'],)
                break
