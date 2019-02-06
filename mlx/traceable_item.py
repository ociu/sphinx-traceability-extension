'''
Storage classes for traceable item
'''

import re
from natsort import natsorted
from mlx.traceable_base_class import TraceableBaseClass
from mlx.traceability_exception import TraceabilityException


class TraceableItem(TraceableBaseClass):
    '''
    Storage for a traceable documentation item
    '''

    STRING_TEMPLATE = 'Item {identification}\n'

    defined_attributes = {}

    def __init__(self, itemid, placeholder=False):
        '''
        Initialize a new traceable item

        Args:
            itemid (str): Item identification
            placeholder (bool): Internal use only
        '''
        super(TraceableItem, self).__init__(itemid)
        self.explicit_relations = {}
        self.implicit_relations = {}
        self.attributes = {}
        self.placeholder = placeholder

    def update(self, other):
        '''
        Update item with new object

        Store the sum of both objects
        '''
        super(TraceableItem, self).update(other)
        for relation in other.explicit_relations.keys():
            if relation not in self.explicit_relations:
                self.explicit_relations[relation] = []
            self.explicit_relations[relation].extend(other.explicit_relations[relation])
        for relation in other.implicit_relations.keys():
            if relation not in self.implicit_relations:
                self.implicit_relations[relation] = []
            self.implicit_relations[relation].extend(other.implicit_relations[relation])
        # Remainder of fields: update if they improve quality of the item
        for attr in other.attributes.keys():
            self.add_attribute(attr, other.attributes[attr], False)
        if not other.placeholder:
            self.placeholder = False

    def is_placeholder(self):
        '''
        Getter for item being a placeholder or not

        Returns:
            bool: True if the item is a placeholder, false otherwise.
        '''
        return self.placeholder

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
        Get a naturally sorted list of targets to other traceable item(s)

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
        return natsorted(relations)

    def iter_relations(self):
        '''
        Iterate over available relations: naturally sorted

        Returns:
            Sorted iterator over available relations in the item
        '''
        return natsorted(list(self.explicit_relations) + list(self.implicit_relations.keys()))

    @staticmethod
    def define_attribute(attr):
        '''
        Define a attribute that can be assigned to TraceableItems

        Args:
            attr (TraceableAttribute): Attribute
        '''
        TraceableItem.defined_attributes[attr.get_id()] = attr

    def add_attribute(self, attr, value, overwrite=True):
        '''
        Add an attribute key-value pair to the traceable item

        Note:
            The given attribute value is compared against defined attribute possibilities. When the attribute
            value doesn't match the defined regex, an exception is thrown.

        Args:
            attr (str): Name of the attribute
            value (str): Value of the attribute
            overwrite(boolean): Overwrite existing attribute value, if any
        '''
        if not attr or not value or attr not in TraceableItem.defined_attributes:
            raise TraceabilityException('item {item} has invalid attribute ({attr}={value})'.format(item=self.get_id(),
                                                                                                    attr=attr,
                                                                                                    value=value),
                                        self.get_document())
        if not TraceableItem.defined_attributes[attr].can_accept(value):
            raise TraceabilityException('item {item} attribute does not match defined attributes ({attr}={value})'
                                        .format(item=self.get_id(), attr=attr, value=value),
                                        self.get_document())
        if overwrite or attr not in self.attributes:
            self.attributes[attr] = value

    def remove_attribute(self, attr):
        '''
        Removes an attribute key-value pair from the traceable item

        Args:
            attr (str): Name of the attribute
        '''
        if not attr:
            raise TraceabilityException('item {item} cannot remove invalid attribute {attr}'.format(item=self.get_id(),
                                                                                                    attr=attr),
                                        self.get_document())
        del self.attributes[attr]

    def get_attribute(self, attr):
        '''
        Get the value of an attribute from the traceable item

        Args:
            attr (str): Name of the attribute
        Returns:
            Value matching the given attribute key, or '' if attribute does not exist
        '''
        value = ''
        if attr in self.attributes:
            value = self.attributes[attr]
        return value

    def get_attributes(self, attrs):
        '''
        Get the values of a list of attributes from the traceable item

        Args:
            attr (list): List of names of the attribute
        Returns:
            List of values matching the given attributes, or [] if attributes do not exist
        '''
        value = []
        if attrs:
            for attr in attrs:
                value.append(self.get_attribute(attr))
        return value

    def iter_attributes(self):
        '''
        Iterate over available attributes: naturally sorted

        Returns:
            Sorted iterator over available attributes in the item
        '''
        return natsorted(list(self.attributes))

    def __str__(self, explicit=True, implicit=True):
        '''
        Convert object to string
        '''
        retval = TraceableItem.STRING_TEMPLATE.format(identification=self.get_id())
        retval += '\tPlaceholder: {placeholder}\n'.format(placeholder=self.is_placeholder())
        for attribute in self.attributes:
            retval += '\tAttribute {attribute} = {value}\n'.format(attribute=attribute,
                                                                   value=self.attributes[attribute])
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

    def attributes_match(self, attributes):
        '''
        Check if item matches a given set of attributes

        Args:
            - attributes (dict): Dictionary with attribute-regex pairs to match the given item against
        Returns:
            (boolean) True if the given attributes match the item attributes
        '''
        for attr in attributes.keys():
            if not re.match(attributes[attr], self.get_attribute(attr)):
                return False
        return True

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

    def to_dict(self):
        '''
        Export to dictionary

        Returns:
            (dict) Dictionary representation of the object
        '''
        data = {}
        if not self.is_placeholder():
            data = super(TraceableItem, self).to_dict()
            data['id'] = self.get_id()
            caption = self.get_caption()
            if caption:
                data['caption'] = caption
            data['document'] = self.docname
            data['line'] = self.lineno
            data['attributes'] = self.attributes
            data['targets'] = {}
            for relation in self.iter_relations():
                tgts = self.iter_targets(relation)
                if tgts:
                    data['targets'][relation] = tgts
        return data

    def self_test(self):
        '''
        Perform self test on collection content
        '''
        super(TraceableItem, self).self_test()
        # Item should not be a placeholder
        if self.is_placeholder():
            raise TraceabilityException('item {item} is not defined'.format(item=self.get_id()), self.get_document())
        # Item's attributes should be valid
        for attribute in self.iter_attributes():
            if not self.attributes[attribute]:
                raise TraceabilityException('item {item} has invalid attribute value for {attribute}'
                                            .format(item=self.get_id(), attribute=attribute))
        # Targets should have no duplicates
        for relation in self.iter_relations():
            tgts = self.iter_targets(relation)
            cnt_duplicate = len(tgts) - len(set(tgts))
            if cnt_duplicate != 0:
                raise TraceabilityException('{cnt} duplicate target(s) found for {item} {relation})'
                                            .format(cnt=cnt_duplicate, item=self.get_id(), relation=relation),
                                            self.get_document())
