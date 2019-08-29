from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode


class ItemAttributesMatrix(TraceableBaseNode):
    '''Matrix for referencing documentation items with their attributes'''

    def perform_replacement(self, app, collection):
        """ Creates table with items, printing their attribute values.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        showcaptions = not self['nocaptions']
        item_ids = collection.get_items(self['filter'],
                                        attributes=self['filter-attributes'],
                                        sortattributes=self['sort'],
                                        reverse=self['reverse'])
        top_node = self.create_top_node(self['title'])
        table = nodes.table()
        if self.get('classes'):
            table.get('classes').extend(self.get('classes'))
        tgroup = nodes.tgroup()
        tbody = nodes.tbody()
        colspecs = [nodes.colspec(colwidth=5)]
        hrow = nodes.row('', nodes.entry('', nodes.paragraph('', '')))

        for item_id in item_ids:
            p_node = self.make_internal_item_ref(app, item_id, showcaptions)  # 1st col
            if self['transpose']:
                colspecs.append(nodes.colspec(colwidth=5))
                hrow.append(nodes.entry('', p_node))
            else:
                row = nodes.row()
                row.append(nodes.entry('', p_node))
                item = collection.get_item(item_id)
                self.fill_item_row(row, item)
                tbody += row

        for attr in self['attributes']:
            p_node = self.make_attribute_ref(app, attr)
            if self['transpose']:
                row = nodes.row()
                row.append(nodes.entry('', p_node))
                self.fill_attribute_row(row, attr, item_ids, collection)
                tbody += row
            else:
                colspecs.append(nodes.colspec(colwidth=5))
                hrow.append(nodes.entry('', p_node))

        tgroup += colspecs
        tgroup += nodes.thead('', hrow)
        tgroup += tbody
        table += tgroup
        top_node += table
        self.replace_self(top_node)

    def fill_item_row(self, row, item):
        """ Fills the row for one item with the specified attributes.

        Args:
            row (nodes.row): Row node to fill.
            item (TraceableItem): TraceableItem object to get attributes from.
        """
        for attr in self['attributes']:
            cell = nodes.entry()
            p_node = nodes.paragraph()
            txt = item.get_attribute(attr)
            p_node += nodes.Text(txt)
            cell += p_node
            row += cell

    @staticmethod
    def fill_attribute_row(row, attr, item_ids, collection):
        """ Fills the row for a particular attribute with attribute values from item IDs.

        Args:
            row (nodes.row): Row node to fill.
            attr (str): Attribute name.
            item_ids (list): List of item IDs.
            collection (TraceableCollection): Storage object for a collection of TraceableItems.
        """
        for item_id in item_ids:
            item = collection.get_item(item_id)
            cell = nodes.entry()
            p_node = nodes.paragraph()
            txt = item.get_attribute(attr)
            p_node += nodes.Text(txt)
            cell += p_node
            row += cell


class ItemAttributesMatrixDirective(TraceableBaseDirective):
    """
    Directive to generate a matrix of items with their attribute values.

    Syntax::

      .. item-attributes-matrix:: title
         :filter: regexp
         :<<attribute>>: regexp
         :attributes: <<attribute>> ...
         :sort: <attribute>> ...
         :reverse:
         :nocaptions:
    """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'class': directives.class_option,
        'filter': directives.unchanged,
        'attributes': directives.unchanged,
        'sort': directives.unchanged,
        'reverse': directives.flag,
        'nocaptions': directives.flag,
        'transpose': directives.flag,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        node = ItemAttributesMatrix('')
        node['document'] = env.docname
        node['line'] = self.lineno

        if self.options.get('class'):
            node.get('classes').extend(self.options.get('class'))

        # Process title (optional argument)
        if self.arguments:
            node['title'] = self.arguments[0]
        else:
            node['title'] = 'Matrix of items and attributes'

        # Process ``filter`` options
        self.process_options(node, {'filter': ''})

        self.add_found_attributes(node)

        # Process ``attributes`` option, given as a string with attributes
        # separated by space. It is converted to a list.
        if 'attributes' in self.options and self.options['attributes']:
            self._warn_if_comma_separated('attributes', env.docname)
            node['attributes'] = self.options['attributes'].split()
        else:
            node['attributes'] = list(app.config.traceability_attributes)
        self.remove_unknown_attributes(node['attributes'], 'attribute', env.docname)

        # Process ``sort`` option, given as a string with attributes
        # separated by space. It is converted to a list.
        if 'sort' in self.options and self.options['sort']:
            self._warn_if_comma_separated('sort', env.docname)
            node['sort'] = self.options['sort'].split()
            self.remove_unknown_attributes(node['sort'], 'sorting attribute', env.docname)
        else:
            node['sort'] = []

        self.check_option_presence(node, 'reverse')
        self.check_option_presence(node, 'transpose')

        self.check_no_captions_flag(node, app.config.traceability_attributes_matrix_no_captions)

        return [node]
