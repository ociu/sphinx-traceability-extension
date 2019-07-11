import re
from hashlib import sha256
from os import environ, mkdir, path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
import matplotlib as mpl
if not environ.get('DISPLAY'):
    mpl.use('Agg')
import matplotlib.pyplot as plt

from mlx.traceability import report_warning
from mlx.traceability_item_element import ItemElement
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


class ItemPieChart(ItemElement):
    '''Pie chart on documentation items'''

    def perform_traceability_replacement(self, app, collection):
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
        relationships = collection.iter_relations()
        all_item_ids = collection.get_items('')

        # default priority order is 'uncovered', 'covered', 'executed', 'pass', 'fail', 'error'
        priorities = {}
        for idx, label in enumerate(self['label_set']):
            priorities[label] = idx
        # store :<<attribute>>: arguments in reverse order in lowercase for case-insensitivity
        if self['priorities']:
            for idx, attr in enumerate([value.lower() for value in self['priorities'][::-1]],
                                       start=len(self['label_set'])):
                priorities[attr] = idx

        attribute_id = ''
        if len(self['id_set']) > 2:
            attribute_id = self['id_set'][2]

        linked_attributes = {}  # source_id (str): attr_value (str)
        covered_items = {}  # source_id (str): test_items (list)

        for source_id in all_item_ids:
            source_item = collection.get_item(source_id)
            # placeholders don't end up in any item-piechart (less duplicate warnings for missing items)
            if source_item.is_placeholder():
                continue
            if re.match(self['id_set'][0], source_id):
                covered = False
                test_items = []
                linked_attributes[source_id] = list(priorities.keys())[0]  # default is "uncovered"
                for relationship in relationships:
                    tgts = source_item.iter_targets(relationship, True, True)
                    for target_id in tgts:
                        target_item = collection.get_item(target_id)
                        # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
                        if not target_item or target_item.is_placeholder():
                            continue
                        if re.match(self['id_set'][1], target_id):
                            test_items.append(target_item)
                            linked_attributes[source_id] = list(priorities.keys())[1]  # default is "covered"
                            covered = True
                if covered and attribute_id:
                    covered_items[source_id] = test_items

        # link highest priority attribute value of nested relations to source id
        for source_id, test_items in covered_items.items():
            for covering_item in test_items:
                for relationship in relationships:
                    tgts = covering_item.iter_targets(relationship, True, True)
                    for target_id in tgts:
                        target_item = collection.get_item(target_id)
                        # placeholders don't end up in any item-matrix (less duplicate warnings for missing items)
                        if not target_item or target_item.is_placeholder():
                            continue
                        if re.match(attribute_id, target_id):
                            # case-insensitivity
                            attribute_value = target_item.get_attribute(self['attribute']).lower()
                            if attribute_value not in priorities.keys():
                                attribute_value = list(priorities.keys())[2]  # default is "executed"

                            if source_id not in linked_attributes.keys():
                                linked_attributes[source_id] = attribute_value
                            else:
                                # store newly encountered attribute value if it has a higher priority
                                stored_attribute_priority = priorities[linked_attributes[source_id]]
                                latest_attribute_priority = priorities[attribute_value]
                                if latest_attribute_priority > stored_attribute_priority:
                                    linked_attributes[source_id] = attribute_value

        # initialize dictionary and increment counters for each possible value
        all_states = {}
        for priority in priorities.keys():
            all_states[priority] = 0
        for attribute in linked_attributes.values():
            all_states[attribute] += 1

        count_total = len(linked_attributes)
        count_uncovered = all_states[self['label_set'][0]]
        count_covered = count_total - count_uncovered
        try:
            percentage = int(100 * count_covered / count_total)
        except ZeroDivisionError:
            percentage = 0
        disp = 'Statistics: {cover} out of {total} covered: {pct}%'.format(cover=count_covered,
                                                                           total=count_total,
                                                                           pct=percentage,)

        # remove items with count value equal to 0
        all_states = {k: v for k, v in all_states.items() if v}
        # keep case-sensitivity of :<<attribute>>: arguments in labels of pie chart
        case_sensitive_priorities = self['priorities']
        for priority in case_sensitive_priorities:
            if priority.lower() in all_states.keys():
                value = all_states.pop(priority.lower())
                all_states[priority] = value
        labels = list(all_states.keys())

        sizes = all_states.values()
        explode = [0.05]  # slightly detaches slice of first state, default is "uncovered"
        explode.extend([0] * (len(all_states.values()) - 1))

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
        if rel_file_path not in env.images.keys():
            fig.savefig(path.join(env.app.srcdir, rel_file_path), format='png')
            env.images[rel_file_path] = ['_images', path.split(rel_file_path)[-1]]  # store file name in build env

        p_node = nodes.paragraph()
        p_node += nodes.Text(disp)
        image_node = nodes.image()
        image_node['uri'] = rel_file_path
        image_node['candidates'] = '*'  # look at uri value for source path, relative to the srcdir folder
        p_node += image_node
        top_node += p_node
        self.replace_self(top_node)


class ItemPieChartDirective(Directive):
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
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'id_set': directives.unchanged,
                   'label_set': directives.unchanged}
    # Content disallowed
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        item_chart_node = ItemPieChart('')
        item_chart_node['document'] = env.docname
        item_chart_node['line'] = self.lineno

        # Process title (optional argument)
        if self.arguments:
            item_chart_node['title'] = self.arguments[0]

        # Process ``id_set`` option
        if 'id_set' in self.options and len(self.options['id_set']) >= 2:
            item_chart_node['id_set'] = self.options['id_set'].split()
        else:
            item_chart_node['id_set'] = []
            report_warning(env, 'Traceability: Expected at least two arguments in id_set.', env.docname, self.lineno)

        # Process ``label_set`` option
        default_labels = ['uncovered', 'covered', 'executed']
        if 'label_set' in self.options:
            item_chart_node['label_set'] = [x.strip(' ') for x in self.options['label_set'].split(',')]
            if len(item_chart_node['label_set']) != len(item_chart_node['id_set']):
                item_chart_node['label_set'].extend(
                    default_labels[len(item_chart_node['label_set']):len(item_chart_node['id_set'])])
        else:
            id_amount = len(item_chart_node['id_set'])
            item_chart_node['label_set'] = default_labels[:id_amount]  # default labels

        # Add found attribute to item. Attribute data is a comma-separated list of strings
        item_chart_node['attribute'] = ''
        item_chart_node['priorities'] = []
        for attr in TraceableItem.defined_attributes.keys():
            if attr in self.options:
                if len(item_chart_node['id_set']) == 3:
                    item_chart_node['attribute'] = attr
                    item_chart_node['priorities'] = [x.strip(' ') for x in self.options[attr].split(',')]
                else:
                    report_warning(env,
                                   'Traceability: The <<attribute>> option is only viable with an id_set with 3 '
                                   'arguments.',
                                   env.docname,
                                   self.lineno,)
                break

        return [item_chart_node]
