from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from mlx.traceability import report_warning
from mlx.traceability_item_element import ItemElement
from mlx.traceable_item import TraceableItem

class ItemAttributesMatrix(ItemElement):
    '''Matrix for referencing documentation items with their attributes'''

    def perform_traceability_replacement(self, app, collection):
        """ Creates table with items, printing their attribute values.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        showcaptions = not self['nocaptions']
        item_ids = collection.get_items(self['filter'], self['filter-attributes'],
                                                         sortattributes=self['sort'],
                                                         reverse=self['reverse'])
        top_node = self.create_top_node(self['title'])
        table = nodes.table()
        if self.get('classes'):
            table.get('classes').extend(self.get('classes'))
        tgroup = nodes.tgroup()
        colspecs = [nodes.colspec(colwidth=5)]
        hrow = nodes.row('', nodes.entry('', nodes.paragraph('', '')))
        for attr in self['attributes']:
            colspecs.append(nodes.colspec(colwidth=5))
            p_node = nodes.paragraph()
            p_node += self.make_attribute_ref(app, attr)
            hrow.append(nodes.entry('', p_node))
        tgroup += colspecs
        tgroup += nodes.thead('', hrow)
        tbody = nodes.tbody()
        for item_id in item_ids:
            item = collection.get_item(item_id)
            row = nodes.row()
            cell = nodes.entry()
            cell += self.make_internal_item_ref(app, item_id, showcaptions)
            row += cell
            for attr in self['attributes']:
                cell = nodes.entry()
                p_node = nodes.paragraph()
                txt = item.get_attribute(attr)
                p_node += nodes.Text(txt)
                cell += p_node
                row += cell
            tbody += row
        tgroup += tbody
        table += tgroup
        top_node += table
        self.replace_self(top_node)


class ItemAttributesMatrixDirective(Directive):
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
    final_argument_whitespace = True
    # Options
    option_spec = {'class': directives.class_option,
                   'filter': directives.unchanged,
                   'attributes': directives.unchanged,
                   'sort': directives.unchanged,
                   'reverse': directives.flag,
                   'nocaptions': directives.flag}
    # Content disallowed
    has_content = False

    def run(self):
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
        if 'filter' in self.options:
            node['filter'] = self.options['filter']
        else:
            node['filter'] = ''

        # Add found attributes to item. Attribute data is a single string.
        node['filter-attributes'] = {}
        for attr in TraceableItem.defined_attributes.keys():
            if attr in self.options:
                node['filter-attributes'][attr] = self.options[attr]

        # Process ``attributes`` option, given as a string with attributes
        # separated by space. It is converted to a list.
        if 'attributes' in self.options and self.options['attributes']:
            node['attributes'] = self.options['attributes'].split()
        else:
            node['attributes'] = list(app.config.traceability_attributes.keys())

        # Check if given attributes are in configuration
        for attr in node['attributes']:
            if attr not in TraceableItem.defined_attributes.keys():
                report_warning(env, 'Traceability: unknown attribute for item-attributes-matrix: %s' % attr,
                               env.docname, self.lineno)
                node['attributes'].remove(attr)

        # Process ``sort`` option, given as a string with attributes
        # separated by space. It is converted to a list.
        if 'sort' in self.options and self.options['sort']:
            node['sort'] = self.options['sort'].split()
            # Check if given sort-attributes are in configuration
            for attr in node['sort']:
                if attr not in TraceableItem.defined_attributes.keys():
                    report_warning(env, 'Traceability: unknown sorting attribute for item-attributes-matrix: %s' % attr,
                                   env.docname, self.lineno)
                    node['sort'].remove(attr)
        else:
            node['sort'] = None

        # Check reverse flag
        if 'reverse' in self.options:
            node['reverse'] = True
        else:
            node['reverse'] = False

        # Check nocaptions flag
        if 'nocaptions' in self.options:
            node['nocaptions'] = True
        elif app.config.traceability_attributes_matrix_no_captions:
            node['nocaptions'] = True
        else:
            node['nocaptions'] = False

        return [node]
