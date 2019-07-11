from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from mlx.traceability_exception import report_warning, TraceabilityException
from mlx.traceability_item_element import ItemElement, REGEXP_EXTERNAL_RELATIONSHIP
from mlx.traceable_item import TraceableItem

class Item(ItemElement):
    '''Documentation item'''

    def perform_traceability_replacement(self, app, collection):
        """
        Perform the node replacement
        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        env = app.builder.env
        currentitem = collection.get_item(self['id'])
        showcaptions = not self['nocaptions']
        header = currentitem.get_id()
        if currentitem.caption:
            header += ' : ' + currentitem.caption
        top_node = self.create_top_node(header)
        par_node = nodes.paragraph()
        dl_node = nodes.definition_list()
        if app.config.traceability_render_attributes_per_item:
            if currentitem.iter_attributes():
                li_node = nodes.definition_list_item()
                dt_node = nodes.term()
                txt = nodes.Text('Attributes')
                dt_node.append(txt)
                li_node.append(dt_node)
                for attr in currentitem.iter_attributes():
                    dd_node = nodes.definition()
                    p_node = nodes.paragraph()
                    link = self.make_attribute_ref(app, attr, currentitem.get_attribute(attr))
                    p_node.append(link)
                    dd_node.append(p_node)
                    li_node.append(dd_node)
                dl_node.append(li_node)
        if app.config.traceability_render_relationship_per_item:
            for rel in collection.iter_relations():
                tgts = currentitem.iter_targets(rel)
                if tgts:
                    li_node = nodes.definition_list_item()
                    dt_node = nodes.term()
                    if rel in app.config.traceability_relationship_to_string:
                        relstr = app.config.traceability_relationship_to_string[rel]
                    else:
                        report_warning(env,
                                       'Traceability: relation {rel} cannot be translated to string'
                                       .format(rel=rel),
                                       self.docname, self.line)
                        relstr = rel
                    txt = nodes.Text(relstr)
                    dt_node.append(txt)
                    li_node.append(dt_node)
                    for tgt in tgts:
                        dd_node = nodes.definition()
                        p_node = nodes.paragraph()
                        if REGEXP_EXTERNAL_RELATIONSHIP.search(rel):
                            link = self.make_external_item_ref(app, tgt, rel)
                        else:
                            link = self.make_internal_item_ref(app, tgt, showcaptions)
                        p_node.append(link)
                        dd_node.append(p_node)
                        li_node.append(dd_node)
                    dl_node.append(li_node)
        par_node.append(dl_node)
        top_node.append(par_node)
        # Note: content should be displayed during read of RST file, as it contains other RST objects
        self.replace_self(top_node)


class ItemDirective(Directive):
    """
    Directive to declare items and their traceability relationships.

    Syntax::

      .. item:: item_id [item_caption]
         :<<relationship>>:  other_item_id ...
         :<<attribute>>: attribute_value
         ...
         :nocaptions:

         [item_content]

    When run, for each item, two nodes will be returned:

    * A target node
    * A custom node with id + caption, to be replaced with relationship links
    * A node containing the content of the item

    Also ``traceability_collection`` storage is filled with item information

    """
    # Required argument: id
    required_arguments = 1
    # Optional argument: caption (whitespace allowed)
    optional_arguments = 1
    final_argument_whitespace = True
    # Options: the typical ones plus every relationship (and reverse)
    # defined in env.config.traceability_relationships
    option_spec = {'class': directives.class_option,
                   'nocaptions': directives.flag}
    # Content allowed
    has_content = True

    def run(self):
        env = self.state.document.settings.env
        app = env.app
        caption = ''

        target_id = self.arguments[0]
        target_node = nodes.target('', '', ids=[target_id])

        item_node = Item('')
        item_node['document'] = env.docname
        item_node['line'] = self.lineno
        item_node['id'] = target_id

        # Item caption is the text following the mandatory id argument.
        # Caption should be considered a line of text. Remove line breaks.
        if len(self.arguments) > 1:
            caption = self.arguments[1].replace('\n', ' ')

        # Store item info
        item = TraceableItem(target_id)
        item.set_document(env.docname, self.lineno)
        item.bind_node(target_node)
        item.set_caption(caption)
        item.set_content('\n'.join(self.content))
        try:
            env.traceability_collection.add_item(item)
        except TraceabilityException as err:
            report_warning(env, err, env.docname, self.lineno)

        # Add found attributes to item. Attribute data is a single string.
        for attribute in TraceableItem.defined_attributes.keys():
            if attribute in self.options:
                try:
                    item.add_attribute(attribute, self.options[attribute])
                except TraceabilityException as err:
                    report_warning(env, err, env.docname, self.lineno)

        # Add found relationships to item. All relationship data is a string of
        # item ids separated by space. It is splitted in a list of item ids
        for rel in env.traceability_collection.iter_relations():
            if rel in self.options:
                related_ids = self.options[rel].split()
                for related_id in related_ids:
                    try:
                        env.traceability_collection.add_relation(target_id, rel, related_id)
                    except TraceabilityException as err:
                        report_warning(env, err, env.docname, self.lineno)

        # Custom callback for modifying items
        if app.config.traceability_callback_per_item:
            app.config.traceability_callback_per_item(target_id, env.traceability_collection)

        # Output content of item to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template, self.state_machine.document.attributes['source'])

        # Check nocaptions flag
        if 'nocaptions' in self.options:
            item_node['nocaptions'] = True
        elif app.config.traceability_item_no_captions:
            item_node['nocaptions'] = True
        else:
            item_node['nocaptions'] = False

        return [target_node, item_node]
