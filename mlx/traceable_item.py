
class TraceableItemCollection(dict):
    '''
    Storage for a collection of TraceableItems
    '''

    def add_relation_pair(self, forward, reverse):
        '''
        Add a relation pair to the collection

        Args:
            forward (str): Keyword for the forward relation
            reverse (str): Keyword for the reverse relation
        '''
        if not self.relations:
            self.relations = {}
        self.relations[forward] = reverse
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


class TraceableItem(object):
    '''
    Storage for a traceable documentation item
    '''

    def __init__(self, itemid, itemlib=None, placeholder=False):
        '''
        Initialize a new traceable item

        Args:
            itemid (str): Item identification
            itemlib (dict): Library of items in which this traceable item is contained
            placeholder (bool): Internal use only
        '''
        self.id = itemid
        self.itemlib = itemlib
        if self.itemlib is not None:
            self.itemlib[itemid] = self
        self.relations = {}

    def get_id(self):
        '''
        Getter for item identification

        Returns:
            str: item identification
        '''
        return self.id

    def set_details(self, docname, lineno):
        self.docname = docname
        self.lineno = lineno

    def add_relation(self, relation, target):
        '''
        Add a relation to another traceable item

        Args:
            relation (str): Name of the relation
            target (str): Item identification of the targetted traceable item
        '''
        if relation not in self.relations:
            self.relations[relation] = []
        # Add forward relation
        if target not in self.relations[relation]:
            self.relations[relation].append(target)
        # Add reverse relation
        if self.itemlib:
            if target in self.itemlib:
                reverse = self.itemlib.get_reverse_relation(relation)
            #self.itemlib[target].add_relation(reverse,

