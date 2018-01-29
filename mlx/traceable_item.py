'''
Storage classes for traceability plugin
'''

import re


class MultipleTraceabilityExceptions(Exception):
    '''
    Multiple exceptions for traceability plugin
    '''
    def __init__(self, errors):
        '''
        Constructor for multiple traceability exceptions
        '''
        self.errors = errors

    def iter(self):
        '''Iterator for multiple exceptions'''
        return self.errors


class TraceabilityException(Exception):
    '''
    Exception for traceability plugin
    '''
    def __init__(self, message, docname=''):
        '''
        Constructor for traceability exception

        Args:
            message (str): Message for the exception
            docname (str): Name of the document triggering the exception
        '''
        super(TraceabilityException, self).__init__(message)
        self.docname = docname

    def get_document(self):
        '''
        Get document in which error occured

        Returns:
            str: The name of the document in which the error occured
        '''
        return self.docname


class TraceableCollection(object):
    '''
    Storage for a collection of TraceableItems
    '''

    NO_RELATION_STR = ''

    def __init__(self):
        '''Initializer for container of traceable items'''
        self.relations = {}
        self.items = {}

    def add_relation_pair(self, forward, reverse=NO_RELATION_STR):
        '''
        Add a relation pair to the collection

        Args:
            forward (str): Keyword for the forward relation
            reverse (str): Keyword for the reverse relation, or NO_RELATION_STR for external relations
        '''
        # Link forward to reverse relation
        self.relations[forward] = reverse
        # Link reverse to forward relation
        if reverse != self.NO_RELATION_STR:
            self.relations[reverse] = forward

    def get_reverse_relation(self, forward):
        '''
        Get the matching reverse relation

        Args:
            forward (str): Keyword for the forward relation
        Returns:
            str: Keyword for the matching reverse relation, or None
        '''
        if forward in self.relations:
            return self.relations[forward]
        return None

    def iter_relations(self):
        '''
        Iterate over available relations: sorted

        Returns:
            Sorted iterator over available relations in the collection
        '''
        return sorted(self.relations.keys())

    def add_item(self, item):
        '''
        Add a TraceableItem to the list

        Args:
            item (TraceableItem): Traceable item to add
        '''
        itemid = item.get_id()
        # If the item already exists ...
        if itemid in self.items:
            olditem = self.items[itemid]
            # ... and it's not a placeholder, log an error
            if not olditem.placeholder:
                raise TraceabilityException('duplicating {itemid}'.format(itemid=itemid), item.get_document())
            # ... otherwise, update the item with new content
            else:
                olditem.update(item)
        # Otherwise (item doesn't exist), add it
        else:
            self.items[item.get_id()] = item

    def get_item(self, itemid):
        '''
        Get a TraceableItem from the list

        Args:
            itemid (str): Identification of traceable item to get
        Returns:
            TraceableItem: Object for traceable item
        '''
        if self.has_item(itemid):
            return self.items[itemid]
        return None

    def iter_items(self):
        '''
        Iterate over items: sorted identification

        Returns:
            Sorted iterator over identification of the items in the collection
        '''
        return sorted(self.items.keys())

    def has_item(self, itemid):
        '''
        Verify if a item with given id is in the collection

        Args:
            itemid (str): Identification of item to look for
        Returns:
            bool: True if the given itemid is in the collection, false otherwise
        '''
        return itemid in self.items

    def add_relation(self, sourceid, relation, targetid):
        '''
        Add relation between two items

        The function adds the forward and the automatic reverse relation.

        Args:
            sourceid (str): ID of the source item
            relation (str): Relation between source and target item
            targetid (str): ID of the target item
        '''
        # Fail if source item is unknown
        if sourceid not in self.items:
            raise ValueError('Source item {name} not known'.format(name=sourceid))
        source = self.items[sourceid]
        # Error if relation is unknown
        if relation not in self.relations:
            raise TraceabilityException('Relation {name} not known'.format(name=relation), source.get_document())
        # Add forward relation
        source.add_target(relation, targetid)
        # When reverse relation exists, continue to create/adapt target-item
        reverse_relation = self.get_reverse_relation(relation)
        if reverse_relation:
            # Add placeholder if target item is unknown
            if targetid not in self.items:
                tgt = TraceableItem(targetid, True)
                self.add_item(tgt)
            # Add reverse relation to target-item
            self.items[targetid].add_target(reverse_relation, sourceid, implicit=True)

    def self_test(self, docname=None):
        '''
        Perform self test on collection content

        Args:
            docname (str): Document on which to run the self test, None for all.
        '''
        errors = []
        # Having no valid relations, is invalid
        if not self.relations:
            raise TraceabilityException('No relations configured', 'configuration')
        # Validate each item
        for itemid in self.items:
            item = self.get_item(itemid)
            # Only for relevant items, filtered on document name
            if docname is not None and item.get_document() != docname and item.get_document() is not None:
                continue
            # On item level
            try:
                item.self_test()
            except TraceabilityException as e:
                errors.append(e)
            # targetted items shall exist, with automatic reverse relation
            for relation in self.relations:
                # Exception: no reverse relation (external links)
                rev_relation = self.get_reverse_relation(relation)
                if rev_relation == self.NO_RELATION_STR:
                    continue
                for tgt in item.iter_targets(relation):
                    # Target item exists?
                    if tgt not in self.items:
                        errors.append(TraceabilityException('''{source} {relation} {target},
                                      but {target} is not known'''.format(source=itemid,
                                                                          relation=relation,
                                                                          target=tgt),
                                      item.get_document()))
                        continue
                    # Reverse relation exists?
                    target = self.get_item(tgt)
                    if itemid not in target.iter_targets(rev_relation):
                        errors.append(TraceabilityException('''No automatic reverse relation:
                                      {source} {relation} {target}'''.format(source=tgt,
                                                                             relation=rev_relation,
                                                                             target=itemid),
                                      item.get_document()))
        if errors:
            raise MultipleTraceabilityExceptions(errors)

    def __str__(self):
        '''
        Convert object to string
        '''
        retval = 'Available relations:'
        for relation in self.relations:
            reverse = self.get_reverse_relation(relation)
            retval += '\t{forward}: {reverse}\n'.format(forward=relation, reverse=reverse)
        for itemid in self.items:
            retval += str(self.items[itemid])
        return retval

    def are_related(self, sourceid, relations, targetid):
        '''
        Check if 2 items are related using a list of relationships

        Placeholders are excluded

        Args:
            - sourceid (str): id of the source item
            - relations (list): list of relations, empty list for wildcard
            - targetid (str): id of the target item
        Returns:
            (boolean) True if both items are related through the given relationships, false otherwise
        '''
        if sourceid not in self.items:
            return False
        source = self.items[sourceid]
        if not source or source.is_placeholder():
            return False
        if targetid not in self.items:
            return False
        target = self.items[targetid]
        if not target or target.is_placeholder():
            return False
        if not relations:
            relations = self.iter_relations()
        return self.items[sourceid].is_related(relations, targetid)

    def get_matches(self, regex):
        '''
        Get all items that match a given regular expression

        Placeholders are excluded

        Args:
            - regex (str): Regex to match the items in this collection against
        Returns:
            A sorted list of item-id's matching the given regex
        '''
        matches = []
        for itemid in self.items:
            if self.items[itemid].is_placeholder():
                continue
            if self.items[itemid].is_match(regex):
                matches.append(itemid)
        matches.sort()
        return matches


class TraceableItem(object):
    '''
    Storage for a traceable documentation item
    '''

    STRING_TEMPLATE = 'Item {identification}\n'

    def __init__(self, itemid, placeholder=False):
        '''
        Initialize a new traceable item

        Args:
            itemid (str): Item identification
            placeholder (bool): Internal use only
        '''
        self.id = itemid
        self.explicit_relations = {}
        self.implicit_relations = {}
        self.placeholder = placeholder
        self.docname = None
        self.lineno = None
        self.node = None
        self.caption = None
        self.content = None

    def update(self, other):
        '''
        Update item with new object

        Store the sum of both objects
        '''
        if self.id != other.id:
            raise ValueError('Update error {old} vs {new}'.format(old=self.id, new=other.id))
        for relation in other.explicit_relations.keys():
            if relation not in self.explicit_relations:
                self.explicit_relations[relation] = []
            self.explicit_relations[relation].extend(other.explicit_relations[relation])
        for relation in other.implicit_relations.keys():
            if relation not in self.implicit_relations:
                self.implicit_relations[relation] = []
            self.implicit_relations[relation].extend(other.implicit_relations[relation])
        # Remainder of fields: update if they improve quality of the item
        if not other.placeholder:
            self.placeholder = False
        if other.docname is not None:
            self.docname = other.docname
        if other.lineno is not None:
            self.lineno = other.lineno
        if other.node is not None:
            self.node = other.node
        if other.caption is not None:
            self.caption = other.caption
        if other.content is not None:
            self.content = other.content

    def get_id(self):
        '''
        Getter for item identification

        Returns:
            str: item identification
        '''
        return self.id

    def is_placeholder(self):
        '''
        Getter for item being a placeholder or not

        Returns:
            bool: True if the item is a placeholder, false otherwise.
        '''
        return self.placeholder

    def set_document(self, docname, lineno=0):
        '''
        Set location in document

        Args:
            docname (str): Path to docname
            lineno (int): Line number in given document
        '''
        self.docname = docname
        self.lineno = lineno

    def get_document(self):
        '''
        Get location in document

        Returns:
            str: Path to docname
        '''
        return self.docname

    def get_line_number(self):
        '''
        Get line number in document

        Returns:
            int: Line number in given document
        '''
        return self.lineno

    def bind_node(self, node):
        '''
        Bind to node

        Args:
            node (node): Docutils node object
        '''
        self.node = node

    def get_node(self):
        '''
        Get the node to which the object is bound

        Returns:
            node: Docutils node object
        '''
        return self.node

    def set_caption(self, caption):
        '''
        Set short description of the item

        Args:
            caption (str): Short description of the item
        '''
        self.caption = caption

    def get_caption(self):
        '''
        Get short description of the item

        Returns:
            str: Short description of the item
        '''
        return self.caption

    def set_content(self, content):
        '''
        Set content of the item

        Args:
            content (str): Content of the item
        '''
        self.content = content

    def get_content(self):
        '''
        Get content of the item

        Returns:
            str: Content of the item
        '''
        return self.content

    def _add_target(self, database, relation, target):
        '''
        Add a relation to another traceable item

        Args:
            relation (str): Name of the relation
            target (str): Item identification of the targetted traceable item
            database (dict): Dictionary to add the relation to
        '''
        if relation not in database:
            database[relation] = []
        if target not in database[relation]:
            database[relation].append(target)

    def _remove_target(self, database, relation, target):
        '''
        Delete a relation to another traceable item

        Args:
            relation (str): Name of the relation
            target (str): Item identification of the targetted traceable item
            database (dict): Dictionary to remove the relation from
        '''
        if relation in database:
            if target in database[relation]:
                database[relation].remove(target)

    def add_target(self, relation, target, implicit=False):
        '''
        Add a relation to another traceable item

        Note: using this API, the automatic reverse relation is not created. Adding the relation
        through the TraceableItemCollection class performs the adding of automatic reverse
        relations.

        Args:
            relation (str): Name of the relation
            target (str): Item identification of the targetted traceable item
            implicit (bool): If true, an explicitely expressed relation is added here. If false, an implicite
                             (e.g. automatic reverse) relation is added here.
        '''
        # When target is the item itself, it is an error: no circular relationships
        if self.get_id() == target:
            raise TraceabilityException('Error: circular relationship {src} {rel} {tgt}'.format(src=self.get_id(),
                                                                                                rel=relation,
                                                                                                tgt=target),
                                        self.get_document())
        # When relation is already explicit, we shouldn't add. It is an error.
        if relation in self.explicit_relations and target in self.explicit_relations[relation]:
            raise TraceabilityException('Error: duplicating {src} {rel} {tgt}'.format(src=self.get_id(),
                                                                                      rel=relation,
                                                                                      tgt=target),
                                        self.get_document())
        # When relation is already implicit, we shouldn't add. When relation-to-add is explicit, it should move
        # from implicit to explicit.
        elif relation in self.implicit_relations and target in self.implicit_relations[relation]:
            if implicit is False:
                self._remove_target(self.implicit_relations, relation, target)
                self._add_target(self.explicit_relations, relation, target)
        # Otherwise it is a new relation, and we add to the selected database
        else:
            if implicit is False:
                database = self.explicit_relations
            else:
                database = self.implicit_relations
            self._add_target(database, relation, target)

    def remove_targets(self, targetid, explicit=False, implicit=True):
        '''
        Remove any relation to given target item

        Args:
            targetid (str): Identification of the target items to remove
            explicit (bool): If true, explicitely expressed relations to given target are removed.
            implicit (bool): If true, implicitely expressed relations to given target are removed.
        '''
        if explicit is True:
            for relation in self.explicit_relations.keys():
                if targetid in self.explicit_relations[relation]:
                    self.explicit_relations[relation].remove(targetid)
        if implicit is True:
            for relation in self.implicit_relations.keys():
                if targetid in self.implicit_relations[relation]:
                    self.implicit_relations[relation].remove(targetid)

    def iter_targets(self, relation, explicit=True, implicit=True):
        '''
        Get a sorted list of targets to other traceable item(s)

        Args:
            relation (str): Name of the relation
            explicit (bool): If true, explicitely expressed relations are included in the returned list.
            implicit (bool): If true, implicitely expressed relations are included in the returned list.
        '''
        relations = []
        if explicit is True:
            if relation in self.explicit_relations.keys():
                relations.extend(self.explicit_relations[relation])
        if implicit is True:
            if relation in self.implicit_relations.keys():
                relations.extend(self.implicit_relations[relation])
        relations.sort()
        return relations

    def iter_relations(self):
        '''
        Iterate over available relations: sorted

        Returns:
            Sorted iterator over available relations in the item
        '''
        return sorted(list(self.explicit_relations) + list(self.implicit_relations.keys()))

    def __str__(self, explicit=True, implicit=True):
        '''
        Convert object to string
        '''
        retval = self.STRING_TEMPLATE.format(identification=self.get_id())
        retval += '\tPlaceholder: {placeholder}\n'.format(placeholder=self.is_placeholder())
        for relation in self.explicit_relations:
            retval += '\tExplicit {relation}\n'.format(relation=relation)
            for tgtid in self.explicit_relations[relation]:
                retval += '\t\t{target}\n'.format(target=tgtid)
        for relation in self.implicit_relations:
            retval += '\tImplicit {relation}\n'.format(relation=relation)
            for tgtid in self.implicit_relations[relation]:
                retval += '\t\t{target}\n'.format(target=tgtid)
        return retval

    def is_match(self, regex):
        '''
        Check if item matches a given regular expression

        Args:
            - regex (str): Regex to match the given item against
        Returns:
            (boolean) True if the given regex matches the item identification
        '''
        return re.match(regex, self.get_id())

    def is_related(self, relations, targetid):
        '''
        Check if a given item is related using a list of relationships

        Args:
            - relations (list): list of relations
            - targetid (str): id of the target item
        Returns:
            (boolean) True if given item is related through the given relationships, false otherwise
        '''
        related = False
        for relation in relations:
            if targetid in self.iter_targets(relation, explicit=True, implicit=True):
                related = True
        return related

    def self_test(self):
        '''
        Perform self test on collection content
        '''
        # Item should not be a placeholder
        if self.is_placeholder():
            raise TraceabilityException('item {item} is not defined'.format(item=self.get_id()), self.get_document())
        # Item should hold a reference to a document
        if self.get_document() is None:
            raise TraceabilityException('item {item} has no reference to source document'.format(item=self.get_id()))
        # Targets should have no duplicates
        for relation in self.iter_relations():
            tgts = self.iter_targets(relation)
            cnt_duplicate = len(tgts) - len(set(tgts))
            if cnt_duplicate != 0:
                raise TraceabilityException('{cnt} duplicate target(s) found for {item} {relation})'
                                            .format(cnt=cnt_duplicate, item=self.get_id(), relation=relation),
                                            self.get_document())
