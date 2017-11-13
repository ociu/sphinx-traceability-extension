
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
                print('Error duplicating {itemid}'.format(itemid=itemid))
                return
            # ... otherwise, update the item with new content
            else:
                olditem.update(item)
        # If item doesn't exist, add it
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

    def remove_item(self, tgtid):
        '''
        Remove item from container

        Note: any implicit relations to the removed item are also removed.

        Args:
            tgtid (str): Identification of item to remove
        '''
        for itemid in self.iter_items():
            self.items[itemid].remove_targets(tgtid, explicit=False, implicit=True)
        del self.items[tgtid]

    def has_item(self, itemid):
        '''
        Verify if a item with given id is in the collection

        Args:
            itemid (str): Identification of item to look for
        Returns:
            bool: True if the given itemid is in the collection, false otherwise
        '''
        return itemid in self.iter_items()

    def purge(self, docname):
        '''
        Purge any item from the list which matches the given docname

        Note: any implicit relations to the removed items are also removed.

        Args:
            docname (str): Name of the document to purge for
        '''
        for itemid in self.iter_items():
            if self.items[itemid].docname == docname:
                self.remove_item(itemid)

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
            raise ValueError('Item {name} not known'.format(name=sourceid))
        # Error if relation is unknown
        if relation not in self.relations:
            print('Relation {name} not known'.format(name=relation))
            return
        # Add forward relation
        self.items[sourceid].add_target(relation, targetid)
        # When reverse relation exists, continue to create/adapt target-item
        reverse_relation = self.get_reverse_relation(relation)
        if reverse_relation:
            # Add placeholder if target item is unknown
            if targetid not in self.items:
                tgt = TraceableItem(targetid, True)
                self.add_item(tgt)
            # Add reverse relation to target-item
            self.items[targetid].add_target(reverse_relation, sourceid, implicit=True)

    def self_test(self):
        '''
        Perform self test on collection content

        Returns:
            bool: True if self test passed, false otherwise
        '''
        # Having no valid relations, is invalid
        if not self.iter_relations():
            print('Error: no relations configured')
            return False
        # Validate each item
        for itemid in self.iter_items():
            # On item level
            item = self.get_item(itemid)
            if not item.self_test():
                print('Error: self test for {item} failed'.format(item=itemid))
                return False
            # targetted items shall exist, with automatic reverse relation
            for relation in self.iter_relations():
                # Exception: no reverse relation (external links)
                rev_relation = self.get_reverse_relation(relation)
                if rev_relation == self.NO_RELATION_STR:
                    continue
                for tgt in item.iter_targets(relation):
                    # Target item exists?
                    if tgt not in self.iter_items():
                        print('''Error: {source} {relation} {target},
                                 but {target} is not known'''.format(source=itemid,
                                                                     relation=relation,
                                                                     target=tgt))
                        return False
                    # Reverse relation exists?
                    target = self.get_item(tgt)
                    if itemid not in target.iter_targets(rev_relation):
                        print('''Error no automatic reverse relation:
                                 {source} {relation} {target}'''.format(source=tgt,
                                                                        relation=rev_relation,
                                                                        target=itemid))
                        return False
        return True

    def __str__(self):
        '''
        Convert object to string
        '''
        retval = ''
        for __, item in self.items.iteritems():
            retval += str(item)
        return retval

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

    def update(self, item):
        '''
        Update item with new object

        Store the sum of both objects
        '''
        if self.id != item.id:
            raise ValueError('Update error {old} vs {new}'.format(old=self.id, new=item.id))
        for relation in item.explicit_relations.keys():
            if relation not in self.explicit_relations:
                self.explicit_relations[relation] = []
            self.explicit_relations[relation].extend(item.explicit_relations[relation])
        for relation in item.implicit_relations.keys():
            if relation not in self.implicit_relations:
                self.implicit_relations[relation] = []
            self.implicit_relations[relation].extend(item.implicit_relations[relation])
        # Remainder of fields: update if they improve quality of the item
        if not item.placeholder:
            self.placeholder = False
        if item.docname is not None:
            self.docname = item.docname
        if item.lineno is not None:
            self.lineno = item.lineno
        if item.node is not None:
            self.node = item.node
        if item.caption is not None:
            self.caption = item.caption
        if item.content is not None:
            self.content = item.content

    def get_id(self):
        '''
        Getter for item identification

        Returns:
            str: item identification
        '''
        return self.id

    def set_document(self, docname, lineno):
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
        # When relation is already explicit, we shouldn't add. When relation-to-add is explicit, it is an error.
        if target in self.iter_targets(relation, explicit=True, implicit=False):
            if implicit == False:
                print('Error duplicating {src} {rel} {tgt}'.format(src=self.get_id(), rel=relation, tgt=target))
        # When relation is already implicit, we shouldn't add. When relation-to-add is explicit, it should move
        # from implicit to explicit.
        elif target in self.iter_targets(relation, explicit=False, implicit=True):
            if implicit == False:
                print('Warning duplicating {src} {rel} {tgt}, moving to explicit'.format(src=self.get_id(), rel=relation, tgt=target))
                self._remove_target(self.implicit_relations, relation, target)
                self._add_target(self.explicit_relations, relation, target)
        # Otherwise it is a new relation, and we add to the selected database
        else:
            if implicit == False:
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
        if explicit == True:
            for relation in self.explicit_relations.keys():
                if targetid in self.explicit_relations[relation]:
                    self.explicit_relations[relation].remove(targetid)
        if implicit == True:
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
        if explicit == True:
            if relation in self.explicit_relations.keys():
                relations.extend(self.explicit_relations[relation])
        if implicit == True:
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
        for relation, tgt_ids in self.explicit_relations.iteritems():
            retval += '\tExplicit {relation}\n'.format(relation=relation)
            for tgtid in tgt_ids:
                retval += '\t\t{target}\n'.format(target=tgtid)
        for relation, tgt_ids in self.implicit_relations.iteritems():
            retval += '\tImplicit {relation}\n'.format(relation=relation)
            for tgtid in tgt_ids:
                retval += '\t\t{target}\n'.format(target=tgtid)
        return retval

    def self_test(self):
        '''
        Perform self test on collection content

        Returns:
            bool: True if self test passed, false otherwise
        '''
        # Item should not be a placeholder
        if self.placeholder:
            print('Error: item {item} is not defined'.format(item=self.get_id()))
            return False
        # Targets should have no duplicates
        for relation in self.iter_relations():
            tgts = self.iter_targets(relation)
            if len(tgts) is not len(set(tgts)):
                print('Error: duplicate targets found for {item}'.format(item=self.get_id()))
                return False
        return True
