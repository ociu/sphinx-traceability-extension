# -*- coding: utf-8 -*-

'''
Traceability plugin

Sphinx extension for reStructuredText that added traceable documentation items.
See readme for more details.
'''

from collections import OrderedDict, namedtuple
from re import fullmatch, match
from os import path

from requests import Session
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.errors import NoUri
from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceable_attribute import TraceableAttribute
from mlx.traceable_base_node import TraceableBaseNode
from mlx.traceable_item import TraceableItem
from mlx.traceable_collection import TraceableCollection
from mlx.traceability_exception import TraceabilityException, MultipleTraceabilityExceptions, report_warning
from mlx.directives.attribute_sort_directive import AttributeSort, AttributeSortDirective
from mlx.directives.checkbox_result_directive import CheckboxResultDirective
from mlx.directives.checklist_item_directive import ChecklistItemDirective
from mlx.directives.item_directive import Item, ItemDirective
from mlx.directives.item_2d_matrix_directive import Item2DMatrix, Item2DMatrixDirective
from mlx.directives.item_attribute_directive import ItemAttribute, ItemAttributeDirective
from mlx.directives.item_attributes_matrix_directive import ItemAttributesMatrix, ItemAttributesMatrixDirective
from mlx.directives.item_link_directive import ItemLink, ItemLinkDirective
from mlx.directives.item_list_directive import ItemList, ItemListDirective
from mlx.directives.item_matrix_directive import ItemMatrix, ItemMatrixDirective
from mlx.directives.item_pie_chart_directive import ItemPieChart, ItemPieChartDirective
from mlx.directives.item_tree_directive import ItemTree, ItemTreeDirective

ItemInfo = namedtuple('ItemInfo', 'attr_val mr_id')


def generate_color_css(app, hyperlink_colors):
    """ Generates CSS file that defines the colors for each hyperlink state for each configured regex.

    Args:
        app: Sphinx application object to use.
        hyperlink_colors (OrderedDict): Ordered dict with regex strings as keys and list/tuple of strings as values.
    """
    class_names = app.config.traceability_class_names
    with open(path.join(path.dirname(__file__), 'assets', 'hyperlink_colors.css'), 'w') as css_file:
        for regex, colors in hyperlink_colors.items():
            colors = tuple(colors)
            if len(colors) > 3:
                report_warning("Regex '%s' can take a maximum of 3 colors in traceability_hyperlink_colors." % regex)
            else:
                build_class_name(colors, class_names)
                write_color_commands(css_file, colors, class_names[colors])


def write_color_commands(css_file, colors, class_name):
    """
    Write a color command in the file for each color in the given tuple. The CSS identifier is fetched from the global
    `class_names` dictionary. The first color is used for the default hyperlink state, the second color for the active
    and the hover state, and the third color for the visited state. No CSS code is written when the color is an empty
    string.

    Args:
        css_file (file): Open writeable file object.
        colors (tuple): Tuple of strings representing colors.
        class_name (str): CSS class identifier to use.
    """
    for idx, color in enumerate(colors):
        if idx == 0:
            selectors = ".{0}".format(class_name)
        elif idx == 1:
            selectors = ".{0}:active,\n.{0}:hover".format(class_name)
        else:
            selectors = ".{0}:visited".format(class_name)
        if color:
            css_file.write("%s {\n\tcolor: %s;\n}\n" % (selectors, color))


def build_class_name(inputs, class_names):
    """
    Builds class name based on a tuple of strings that represent a color in CSS. Adds this name as value to the
    dictionary `class_names` with the input tuple as key.

    Args:
        inputs (tuple): Tuple of strings.
        class_names (dict): Dictionary with tuple of color strings as key and corresponding class_name string as value.
    """
    name = '_'.join(inputs)
    trans_table = str.maketrans("#,.%", "h-dp", " ()")
    name = name.translate(trans_table)
    class_names[inputs] = name.lower()


# -----------------------------------------------------------------------------
# Pending item cross reference node


class PendingItemXref(TraceableBaseNode):
    """Node for item cross-references that cannot be resolved without complete information about all documents."""

    def perform_replacement(self, app, collection):
        """ Resolves item cross references (from ``item`` role).

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        # Create a dummy reference to be used if target reference fails
        new_node = make_refnode(app.builder,
                                self['document'],
                                self['document'],
                                'ITEM_NOT_FOUND',
                                self[0].deepcopy(),
                                self['reftarget'] + '??')
        # If target exists, try to create the reference
        item_info = collection.get_item(self['reftarget'])
        if item_info:
            if not self.has_warned_about_undefined(item_info):
                notification_item_id = app.config.traceability_notifications.get('undefined-reference')
                node = self._try_make_refnode(app, item_info.docname, item_info.node['refid'])
                if node is None and notification_item_id:
                    node = self._redirect_undefined_reference(app, notification_item_id)
                if node is not None:
                    new_node = node
        else:
            report_warning('Traceability: item %s not found' % self['reftarget'], self['document'], self['line'])
        self.replace_self(new_node)

    def _redirect_undefined_reference(self, app, notification_item_id):
        """ Uses the configured item ID to create the reference if the item exists.

        Returns None and reports a warning if the item doesn't exist.

        Args:
            app: Sphinx application object to use.
            notification_item_id (str): ID of the item to create the reference to.

        Returns:
            nodes.reference/None: Returns the reference node if a link was successfully made, None otherwise.
        """
        node = None
        notification_item = app.env.traceability_collection.get_item(notification_item_id)
        if notification_item:
            node = self._try_make_refnode(app, notification_item.docname, notification_item_id)
        else:
            report_warning("Failed to redirect undefined reference %r to %r as this configured item does not exist"
                           % (self['reftarget'], notification_item_id))
        return node

    def _try_make_refnode(self, app, docname, refid):
        """ Tries to create a reference node that points to the given document name and reference id.

        Args:
            app: Sphinx application object to use.
            docname (str): Name of the document that contains the reference.
            refid (str): Item ID of the reference.

        Returns:
            nodes.reference/None: Returns the reference node if a link was successfully made, None otherwise.
        """
        try:
            return make_refnode(app.builder,
                                self['document'],
                                docname,
                                refid,
                                self[0].deepcopy(),
                                self['reftarget'])
        except NoUri:
            return None


# -----------------------------------------------------------------------------
# Event handlers

def perform_consistency_check(app, doctree):

    '''
    New in sphinx 1.6: consistency checker callback

    Used to perform the self-test on the collection of items
    '''
    env = app.builder.env

    try:
        env.traceability_collection.self_test()
    except TraceabilityException as err:
        report_warning(str(err), err.get_document())
    except MultipleTraceabilityExceptions as errs:
        for err in errs.iter():
            report_warning(str(err), err.get_document())

    if app.config.traceability_json_export_path:
        fname = app.config.traceability_json_export_path
        env.traceability_collection.export(fname)

    if app.config.traceability_hyperlink_colors:
        app.add_stylesheet('hyperlink_colors.css')
        generate_color_css(app, app.config.traceability_hyperlink_colors)


def process_item_nodes(app, doctree, fromdocname):
    """
    This function should be triggered upon ``doctree-resolved event``

    Replace all ItemList nodes with a list of the collected items.
    Augment each item with a backlink to the original location.

    If the ``checklist_item_regex`` is configured, a warning is reported
    for each item ID that matches it and is not defined as a checklist-item.
    """
    env = app.builder.env

    for node_class in (AttributeSort, ItemLink, ItemMatrix, ItemPieChart, ItemAttributesMatrix, Item2DMatrix, ItemList,
                       ItemTree, ItemAttribute, Item):  # order is important: e.g. AttributeSort before Item
        for node in doctree.traverse(node_class):
            node.perform_replacement(app, env.traceability_collection)

    for node in doctree.traverse(PendingItemXref):
        node['document'] = fromdocname
        node['line'] = node.line
        node.perform_replacement(app, env.traceability_collection)

    regex = app.config.traceability_checklist.get('checklist_item_regex')
    if regex is not None and app.config.traceability_checklist['has_checklist_items']:
        for item_id in list(ChecklistItemDirective.query_results):
            if fullmatch(regex, item_id):
                item_info = ChecklistItemDirective.query_results.pop(item_id)
                report_warning("List item {!r} in merge/pull request {} is not defined as a checklist-item."
                               .format(item_id, item_info.mr_id))


def init_available_relationships(app):
    """
    Update directive option_spec with custom attributes defined in
    configuration file ``traceability_attributes`` variable.
    Report a warning when the custom attribute overlaps with a
    directive option, in which case the custom attribute will be
    ignored in that directive.

    Update directive option_spec with custom relationships defined in
    configuration file ``traceability_relationships`` variable. Both
    keys (relationships) and values (reverse relationships) are added.

    This handler should be called upon builder initialization, before
    processing any directive.

    Function also passes relationships to traceability collection.
    """
    env = app.builder.env
    directive_classes = (
        ItemDirective,
        ItemListDirective,
        ItemMatrixDirective,
        ItemPieChartDirective,
        ItemAttributesMatrixDirective,
        Item2DMatrixDirective,
        ItemTreeDirective,
    )

    for attr in app.config.traceability_attributes:
        conflicting_directives = []
        for directive_class in directive_classes:
            if attr in directive_class.option_spec:
                conflicting_directives.append(directive_class.__name__)
                directive_class.conflicting_options.append(attr)
            else:
                directive_class.option_spec[attr] = directives.unchanged
        define_attribute(attr, app)
        if conflicting_directives:
            report_warning("Your custom attribute {!r} overlaps with an option of directive(s) {!r} in which your "
                           "attribute definition will be ignored.".format(attr, conflicting_directives))

    for rel in app.config.traceability_relationships:
        revrel = app.config.traceability_relationships[rel]
        env.traceability_collection.add_relation_pair(rel, revrel)
        ItemDirective.option_spec[rel] = directives.unchanged
        if revrel:
            ItemDirective.option_spec[revrel] = directives.unchanged


def initialize_environment(app):
    """
    Perform initializations needed before the build process starts.
    """
    env = app.builder.env

    # Assure ``traceability_collection`` will always be there.
    # It needs to be empty on every (re-)build. As the script automatically
    # generates placeholders when parsing the reverse relationships, the
    # database of items needs to be empty on every re-build.
    env.traceability_collection = TraceableCollection()

    app.config.traceability_checklist['has_checklist_items'] = False
    add_checklist_attribute(app.config.traceability_checklist,
                            app.config.traceability_attributes,
                            app.config.traceability_attribute_to_string)

    init_available_relationships(app)

    # LaTeX-support: since we generate empty tags, we need to relax the verbosity of that error
    if 'preamble' not in app.config.latex_elements:
        app.config.latex_elements['preamble'] = ''
    app.config.latex_elements['preamble'] += (
        r'\makeatletter'
        r'\let\@noitemerr\relax'
        r'\makeatother'
    )


# ----------------------------------------------------------------------------
# Event handler helper functions
def add_checklist_attribute(checklist_config, attributes_config, attribute_to_string_config):
    """
    Adds the specified attribute for checklist items to the application configuration variables.
    Sets the checklist_item_regex if it's not configured.

    Reports a warning if the value for 'attribute_values' is not a string of two comma-separated attribute values.

    Args:
        checklist_config (dict): Dictionary containing the attribute configuration parameters for checklist items.
        attributes_config (dict): Dictionary containing the attribute configuration parameters for regular items.
        attribute_to_string_config (dict): Dictionary mapping an attribute to its string representation.
    """
    missing_keys = 0
    for key in ('attribute_name', 'attribute_to_str', 'attribute_values'):
        missing_keys += 1 if not checklist_config.get(key) else 0

    if missing_keys:
        checklist_config['configured'] = False
    else:
        checklist_config['configured'] = True
        if not checklist_config.get('checklist_item_regex'):
            checklist_config['checklist_item_regex'] = r"\S+"

        attr_values = checklist_config['attribute_values'].split(',')
        if len(attr_values) != 2:
            raise TraceabilityException("Checklist attribute values must be two comma-separated strings; got '{}'."
                                        .format(checklist_config['attribute_values']))
        else:
            regexp = "({}|{})".format(attr_values[0], attr_values[1])
            attributes_config[checklist_config['attribute_name']] = regexp
            attribute_to_string_config[checklist_config['attribute_name']] = checklist_config['attribute_to_str']
            if checklist_config.get('api_host_name') and checklist_config.get('project_id') and \
                    checklist_config.get('merge_request_id'):
                ChecklistItemDirective.query_results = query_checklist(checklist_config, attr_values)


def define_attribute(attr, app):
    """ Defines a new attribute. """
    attrobject = TraceableAttribute(attr, app.config.traceability_attributes[attr])
    if attr in app.config.traceability_attribute_to_string:
        attrobject.set_name(app.config.traceability_attribute_to_string[attr])
    else:
        report_warning('Traceability: attribute {attr} cannot be translated to string'.format(attr=attr))
    TraceableItem.define_attribute(attrobject)


def query_checklist(settings, attr_values):
    """ Queries specified API host name for the description of the specified merge request.

    Reports a warning if the API host name is invalid or the response does not contain a description.

    Args:
        settings (dict): Dictionary with the environment variables specified for the checklist feature.
        attr_values (list): List of the two possible attribute values (str).

    Returns:
        (dict) The query results with zero or more key-value pairs in the form of {item ID: ItemInfo}.
    """
    query_results = {}
    headers = {}
    if not settings.get('private_token'):
        settings['private_token'] = ''
    if 'github' in settings['api_host_name']:
        # explicitly request the v3 version of the REST API
        headers['Accept'] = 'application/vnd.github.v3+json'
        if settings['private_token']:
            headers['Authorization'] = 'token {}'.format(settings['private_token'])
        base_url = "{}/repos/{}/pulls/".format(settings['api_host_name'].rstrip('/'),
                                               settings['project_id'],)
        key = 'body'
    elif 'gitlab' in settings['api_host_name']:
        headers['PRIVATE-TOKEN'] = settings['private_token']
        base_url = "{}/projects/{}/merge_requests/".format(settings['api_host_name'].rstrip('/'),
                                                           settings['project_id'],)
        key = 'description'
    else:
        return {}

    for merge_request_id in str(settings['merge_request_id']).split(','):
        url = base_url + merge_request_id.strip()
        with Session() as session:
            with session.get(url, headers=headers) as response:
                response = response.json()

        description = response.get(key)
        if description:
            query_results = {**query_results, **_parse_description(description, attr_values, merge_request_id,
                                                                   settings['checklist_item_regex'])}
        else:
            report_warning("The query did not return a description. URL = {}. Response = {}.".format(url, response))
    return query_results


def _parse_description(description, attr_values, merge_request_id, regex):
    """ Returns the relevant checklist information.

    The item IDs are expected to follow checkboxes directly and the attribute value depends on the status of the
    checkbox.

    Args:
        description (str): Description of the merge/pull request.
        attr_values (list): List of the two possible attribute values (str).
        merge_request_id (int): Merge/Pull request ID.
        regex (str): Regular expression for matching the item ID.

    Returns:
        (dict) Dictionary with key-value pairs with item IDs (str) as keys and ItemInfo (attr_val, mr_id) (namedtuple)
            as values.
    """
    query_results = {}
    for line in description.split('\n'):
        # catch the content of checkbox and the item ID after the checkbox
        cli_match = match(r"\s*[\*\-]\s+\[(?P<checkbox>[\sx])\]\s+(?P<target_id>{})".format(regex), line)
        if cli_match:
            if cli_match.group('checkbox') == 'x':
                item_info = ItemInfo(attr_values[0], merge_request_id)
            else:
                item_info = ItemInfo(attr_values[1], merge_request_id)
            query_results[cli_match.group('target_id')] = item_info
    return query_results


# -----------------------------------------------------------------------------
# Extension setup
def setup(app):
    '''Extension setup'''

    # Javascript and stylesheet for the tree-view
    # app.add_javascript('jquery.js') #note: can only be included once
    app.add_javascript('https://cdn.rawgit.com/aexmachina/jquery-bonsai/master/jquery.bonsai.js')
    app.add_stylesheet('https://cdn.rawgit.com/aexmachina/jquery-bonsai/master/jquery.bonsai.css')
    app.add_javascript('traceability.js')

    # Configuration for exporting collection to json
    app.add_config_value('traceability_json_export_path', None, 'env')

    # Configuration for adapting items through a callback
    app.add_config_value('traceability_callback_per_item', None, 'env')

    # Create default attributes dictionary. Can be customized in conf.py
    app.add_config_value(
        'traceability_attributes',
        {
            'value': '^.*$',
            'asil': '^(QM|[ABCD])$',
            'aspice': '^[123]$',
            'status': '^.*$',
            'result': '(?i)^(pass|fail|error)$',
        },
        'env',
    )

    # Configuration for translating the attribute keywords to rendered text
    app.add_config_value(
        'traceability_attribute_to_string',
        {
            'value': 'Value',
            'asil': 'ASIL',
            'aspice': 'ASPICE',
            'status': 'Status',
            'result': 'Result',
        },
        'env',
    )

    # Create default relationships dictionary. Can be customized in conf.py
    app.add_config_value(
        'traceability_relationships',
        {
            'fulfills': 'fulfilled_by',
            'depends_on': 'impacts_on',
            'implements': 'implemented_by',
            'realizes': 'realized_by',
            'validates': 'validated_by',
            'trace': 'backtrace',
            'ext_toolname': '',
        },
        'env',
    )

    # Configuration for translating the relationship keywords to rendered text
    app.add_config_value(
        'traceability_relationship_to_string',
        {
            'fulfills': 'Fulfills',
            'fulfilled_by': 'Fulfilled by',
            'depends_on': 'Depends on',
            'impacts_on': 'Impacts on',
            'implements': 'Implements',
            'implemented_by': 'Implemented by',
            'realizes': 'Realizes',
            'realized_by': 'Realized by',
            'validates': 'Validates',
            'validated_by': 'Validated by',
            'trace': 'Traces',
            'backtrace': 'Back traces',
            'ext_toolname': 'Reference to toolname',
        },
        'env',
    )

    # Configuration for translating external relationship to url
    app.add_config_value(
        'traceability_external_relationship_to_url',
        {'ext_toolname': 'http://toolname.company.com/field1/workitem?field2'},
        'env',
    )

    # Configuration for enabling the rendering of the attributes on every item
    app.add_config_value('traceability_render_attributes_per_item', True, 'env')

    # Configuration for enabling the rendering of the relations on every item
    app.add_config_value('traceability_render_relationship_per_item', False, 'env')

    # Configuration for disabling the rendering of the captions for item
    app.add_config_value('traceability_item_no_captions', False, 'env')

    # Configuration for enabling the ability to collapse the list of attributes and relations for item
    app.add_config_value('traceability_collapse_links', False, 'env')

    # Configuration for disabling the rendering of the captions for item-list
    app.add_config_value('traceability_list_no_captions', False, 'env')

    # Configuration for disabling the rendering of the captions for item-matrix
    app.add_config_value('traceability_matrix_no_captions', False, 'env')

    # Configuration for disabling the rendering of the captions for item-attributes-matrix
    app.add_config_value('traceability_attributes_matrix_no_captions', False, 'env')

    # Configuration for disabling the rendering of the captions for item-tree
    app.add_config_value('traceability_tree_no_captions', False, 'env')

    # Configuration for customizing the color of hyperlinked items
    app.add_config_value('traceability_hyperlink_colors', OrderedDict([]), 'env')
    # Dictionary used by plugin to pass class names via application object
    app.add_config_value('traceability_class_names', {}, 'env')

    # Configuration for checklist feature
    app.add_config_value('traceability_checklist', {}, 'env')

    # Configuration for notification item about missing items
    app.add_config_value('traceability_notifications', {}, 'env')

    app.add_node(ItemTree)
    app.add_node(ItemMatrix)
    app.add_node(ItemPieChart)
    app.add_node(ItemAttributesMatrix)
    app.add_node(Item2DMatrix)
    app.add_node(ItemList)
    app.add_node(ItemAttribute)
    app.add_node(Item)
    app.add_node(AttributeSort)

    app.add_directive('item', ItemDirective)
    app.add_directive('checklist-item', ChecklistItemDirective)
    app.add_directive('checkbox-result', CheckboxResultDirective)
    app.add_directive('item-attribute', ItemAttributeDirective)
    app.add_directive('item-list', ItemListDirective)
    app.add_directive('item-matrix', ItemMatrixDirective)
    app.add_directive('item-piechart', ItemPieChartDirective)
    app.add_directive('item-attributes-matrix', ItemAttributesMatrixDirective)
    app.add_directive('item-2d-matrix', Item2DMatrixDirective)
    app.add_directive('item-tree', ItemTreeDirective)
    app.add_directive('item-link', ItemLinkDirective)
    app.add_directive('attribute-sort', AttributeSortDirective)

    app.connect('doctree-resolved', process_item_nodes)
    app.connect('env-check-consistency', perform_consistency_check)
    app.connect('builder-inited', initialize_environment)

    app.add_role('item', XRefRole(nodeclass=PendingItemXref,
                                  innernodeclass=nodes.emphasis,
                                  warn_dangling=True))
