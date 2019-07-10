from docutils import nodes
from docutils.parsers.rst import Directive

from mlx.traceability import report_warning
from mlx.traceability_item_element import ItemElement
from mlx.traceable_attribute import TraceableAttribute
from mlx.traceable_item import TraceableItem


class ItemAttribute(ItemElement):
    '''Attribute to documentation item'''

    def perform_traceability_replacement(self, app, collection):
        """
        Perform the node replacement
        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        if self['id'] in TraceableItem.defined_attributes.keys():
            attr = TraceableItem.defined_attributes[self['id']]
            header = attr.get_name()
            if attr.get_caption():
                header += ' : ' + attr.get_caption()
        else:
            header = self['id']
        top_node = self.create_top_node(header)
        par_node = nodes.paragraph()
        dl_node = nodes.definition_list()
        par_node.append(dl_node)
        top_node.append(par_node)
        self.replace_self(top_node)


class ItemAttributeDirective(Directive):
    """
    Directive to declare attribute for items

    Syntax::

      .. item-attribute:: attribute_id [attribute_caption]

         [attribute_content]

    """
    # Required argument: id
    required_arguments = 1
    # Optional argument: caption (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Content allowed
    has_content = True

    def run(self):
        env = self.state.document.settings.env

        # Convert to lower-case as sphinx only allows lowercase arguments (attribute to item directive)
        attribute_id = self.arguments[0]
        target_node = nodes.target('', '', ids=[attribute_id])
        attribute_node = ItemAttribute('')
        attribute_node['document'] = env.docname
        attribute_node['line'] = self.lineno

        # Item caption is the text following the mandatory id argument.
        # Caption should be considered a line of text. Remove line breaks.
        caption = ''
        if len(self.arguments) > 1:
            caption = self.arguments[1].replace('\n', ' ')

        stored_id = TraceableAttribute.to_id(attribute_id)
        if stored_id not in TraceableItem.defined_attributes.keys():
            report_warning(env,
                           'Found attribute description which is not defined in configuration ({})'
                           .format(attribute_id),
                           env.docname,
                           self.lineno)
            attribute_node['id'] = stored_id
        else:
            attr = TraceableItem.defined_attributes[stored_id]
            attr.set_caption(caption)
            attr.set_document(env.docname, self.lineno)
            attribute_node['id'] = attr.get_id()

        # Output content of attribute to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template, self.state_machine.document.attributes['source'])


        return [target_node, attribute_node]
