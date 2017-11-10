
class TraceableCollection(object):
    '''
    Storage for a collection of TraceableItems
    '''

    NO_REVERSE_RELATION_STR = ''

    def __init__(self):
        '''Initializer for container of traceable items'''
        self.relations = {}
        self.items = {}

    def add_relation_pair(self, forward, reverse=NO_REVERSE_RELATION_STR):
        '''
        Add a relation pair to the collection

        Args:
            forward (str): Keyword for the forward relation
            reverse (str): Keyword for the reverse relation, or NO_REVERSE_RELATION_STR for external relations
        '''
        # Link forward to reverse relation
        self.relations[forward] = reverse
        # Link reverse to forward relation
        if reverse != self.NO_REVERSE_RELATION_STR:
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

    def add_item(self, item):
        '''
        Add a TraceableItem to the list

        Args:
            item (TraceableItem): Traceable item to add
        '''
        itemid = item.get_id()
        # If the item already exists, and it's not a placeholder, log an error
        if itemid in self.items:
            if not self.items[itemid].placeholder:
                print('Error duplicating {itemid}'.format(itemid=itemid))
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
            self.items[itemid].remove_relations(tgtid, explicit=False, implicit=True)
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
        self.items[sourceid].add_relation(relation, targetid)
        # When reverse relation exists, continue to create/adapt target-item
        reverse_relation = self.get_reverse_relation(relation)
        if reverse_relation:
            # Add placeholder if target item is unknown
            if targetid not in self.items:
                tgt = TraceableItem(targetid, True)
                self.add_item(tgt)
            # Add reverse relation to target-item
            self.items[targetid].add_relation(reverse_relation, sourceid, implicit=True)

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

    def bind_node(self, node):
        '''
        Bind to node

        Args:
            node (node): Docutils node object
        '''
        self.node = node

    def set_caption(self, caption):
        '''
        Set short description of the item

        Args:
            caption (str): Short description of the item
        '''
        self.caption = caption

    def set_content(self, content):
        '''
        Set content of the item

        Args:
            content (str): Content of the item
        '''
        self.content = content

    def _add_relation(self, database, relation, target):
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

    def _remove_relation(self, database, relation, target):
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

    def add_relation(self, relation, target, implicit=False):
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
        if self.get_relations(relation, explicit=True, implicit=False):
            if implicit == False:
                print('Error duplicating {src} {rel} {tgt}'.format(src=self.get_id(), rel=relation, tgt=target))
        # When relation is already implicit, we shouldn't add. When relation-to-add is explicit, it should move
        # from implicit to explicit.
        elif self.get_relations(relation, explicit=False, implicit=True):
            if implicit == False:
                print('Warning duplicating {src} {rel} {tgt}, moving to explicit'.format(src=self.get_id(), rel=relation, tgt=target))
                self._remove_relation(self.implicit_relations, relation, target)
                self._add_relation(self.explicit_relations, relation, target)
        # Otherwise it is a new relation, and we add to the selected database
        else:
            if implicit == False:
                database = self.explicit_relations
            else:
                database = self.implicit_relations
            self._add_relation(database, relation, target)

    def remove_relations(self, targetid, explicit=False, implicit=True):
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

    def get_relations(self, relation, explicit=True, implicit=True):
        '''
        Get a sorted list of relations to other traceable item(s)

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

    def __str__(self):
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
