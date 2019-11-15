from docutils import nodes
from docutils.parsers.rst import directives

from mlx.traceability_exception import report_warning, TraceabilityException
from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode, REGEXP_EXTERNAL_RELATIONSHIP
from mlx.traceable_item import TraceableItem


class Item(TraceableBaseNode):
    '''Documentation item'''
    _item = None

    def perform_replacement(self, app, collection):
        """
        Perform the node replacement
        Args:
            app: Sphinx's application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        self._item = collection.get_item(self['id'])
        item_id = self._item.get_id()
        top_node = self.create_top_node(item_id, app=app)
        dl_node = nodes.definition_list()
        if app.config.traceability_render_attributes_per_item:
            self._process_attributes(dl_node, app)
        if app.config.traceability_render_relationship_per_item:
            self._process_relationships(collection, dl_node, app)
        if dl_node.children:
            top_node.append(dl_node)
        # Note: content should be displayed during read of RST file, as it contains other RST objects
        self.replace_self(top_node)

    def _process_attributes(self, dl_node, app):
        """ Processes all attributes for the given item and adds the list of attributes to the given definition list.

        Args:
            dl_node (nodes.definition_list): Definition list of the item.
            app: Sphinx's application object to use.
        """
        if self._item.iter_attributes():
            li_node = nodes.definition_list_item()
            dt_node = nodes.term()
            txt = nodes.Text('Attributes')
            dt_node.append(txt)
            li_node.append(dt_node)
            for attr in self._item.iter_attributes():
                dd_node = nodes.definition()
                p_node = nodes.paragraph()
                link = self.make_attribute_ref(app, attr, self._item.get_attribute(attr))
                p_node.append(link)
                dd_node.append(p_node)
                li_node.append(dd_node)
            dl_node.append(li_node)

    def _process_relationships(self, collection, *args):
        """ Processes all relationships of the item. All targets get listed per relationship.

        Args:
            collection (TraceableCollection): Collection of all TraceableItems.
        """
        for rel in collection.iter_relations():
            targets = self._item.iter_targets(rel)
            if targets:
                self._list_targets_for_relation(rel, targets, *args)

    def _list_targets_for_relation(self, relation, targets, dl_node, app):
        """ Add a list with all targets for a specific relation to the given definition list.

        Args:
            relation (str): Name of the relation.
            targets (list): Naturally sorted list of targets to other traceable item(s).
            dl_node (nodes.definition_list): Definition list of the item.
            app: Sphinx's application object to use.
        """
        env = app.builder.env
        li_node = nodes.definition_list_item()
        dt_node = nodes.term()
        if relation in app.config.traceability_relationship_to_string:
            relstr = app.config.traceability_relationship_to_string[relation]
        else:
            report_warning('Traceability: relation {rel} cannot be translated to string'
                           .format(rel=relation),
                           env.docname, self.line)
            relstr = relation
        dt_node.append(nodes.Text(relstr))
        li_node.append(dt_node)
        for target in targets:
            dd_node = nodes.definition()
            p_node = nodes.paragraph()
            if REGEXP_EXTERNAL_RELATIONSHIP.search(relation):
                link = self.make_external_item_ref(app, target, relation)
            else:
                showcaptions = not self['nocaptions']
                link = self.make_internal_item_ref(app, target, showcaptions)
            p_node.append(link)
            dd_node.append(p_node)
            li_node.append(dd_node)
        dl_node.append(li_node)


class ItemDirective(TraceableBaseDirective):
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
    # Options: the typical ones plus every relationship (and reverse)
    # defined in env.config.traceability_relationships
    option_spec = {
        'class': directives.class_option,
        'nocaptions': directives.flag,
    }
    # Content allowed
    has_content = True

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        target_id = self.arguments[0]

        item_node = Item('')
        item_node['document'] = env.docname
        item_node['line'] = self.lineno
        item_node['id'] = target_id
        item_node['classes'].append('collapsible_links')  # traceability.js adds the arrowhead button
        if app.config.traceability_collapse_links:
            item_node['classes'].append('collapse')

        target_node = self._store_item_info(target_id, env)

        # Custom callback for modifying items
        if app.config.traceability_callback_per_item:
            app.config.traceability_callback_per_item(target_id, env.traceability_collection)

        # Output content of item to document
        template = []
        for line in self.content:
            template.append('    ' + line)
        self.state_machine.insert_input(template, self.state_machine.document.attributes['source'])

        self.check_no_captions_flag(item_node, app.config.traceability_item_no_captions)

        return [target_node, item_node]

    def _store_item_info(self, target_id, env):
        """ Stores item info and adds TraceableItem to the collection.

        Args:
            target_id (str): Item identifier.
            env (sphinx.environment.BuildEnvironment): Sphinx's build environment.

        Returns:
            (nodes.target) Node object which is bound to the traceable item.
        """
        target_node = nodes.target('', '', ids=[target_id])
        item = TraceableItem(target_id)
        item.set_document(env.docname, self.lineno)
        item.bind_node(target_node)
        item.set_caption(self.get_caption())
        item.set_content('\n'.join(self.content))
        try:
            env.traceability_collection.add_item(item)
        except TraceabilityException as err:
            report_warning(err, env.docname, self.lineno)

        self._add_attributes(item, env.docname)

        # Add found relationships to item. All relationship data is a string of
        # item ids separated by space. It is split in a list of item ids.
        for rel in env.traceability_collection.iter_relations():
            if rel in self.options:
                self._warn_if_comma_separated(rel, env.docname)
                related_ids = self.options[rel].split()
                self._add_relation_to_ids(rel, target_id, related_ids, env)

        return target_node

    def _add_relation_to_ids(self, relation, source_id, related_ids, env):
        """ Adds the given relation between the source id and all related ids.

        Both the forward and the automatic reverse relation are added.

        Args:
            relation (str): Name of the given relation.
            source_id (str): ID of the source item.
            related_ids (list): List of target item IDs.
            env (sphinx.environment.BuildEnvironment): Sphinx's build environment.
        """
        for related_id in related_ids:
            try:
                env.traceability_collection.add_relation(source_id, relation, related_id)
            except TraceabilityException as err:
                report_warning(err, env.docname, self.lineno)

    def _add_attributes(self, item, docname):
        """ Adds all specified attributes to the item. Attribute data is a single string.

        A warning is reported when an attribute's value doesn't match the attribute's regex.

        Args:
            item (TraceableItem): Item to add the attributes to.
            docname (str): Document name.
        """
        for attribute in TraceableItem.defined_attributes:
            if attribute in self.options:
                try:
                    item.add_attribute(attribute, self.options[attribute])
                except TraceabilityException as err:
                    report_warning(err, docname, self.lineno)
