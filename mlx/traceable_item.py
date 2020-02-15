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

    def __init__(self, item_id, placeholder=False):
        ''' Initializes a new traceable item

        Args:
            item_id (str): Item identifier.
            placeholder (bool): Internal use only.
        '''
        super(TraceableItem, self).__init__(item_id)
        self.explicit_relations = {}
        self.implicit_relations = {}
        self.attributes = {}
        self.attribute_order = []
        self._placeholder = placeholder

    def update(self, other):
        ''' Updates item with other object. Stores the sum of both objects.

        Args:
            other (TraceableItem): Other TraceableItem which is the source for the update.
        '''
        super(TraceableItem, self).update(other)
        self._add_relations(self.explicit_relations, other.explicit_relations)
        self._add_relations(self.implicit_relations, other.implicit_relations)
        # Remainder of fields: update if they improve the quality of the item
        for attr in other.attributes:
            self.add_attribute(attr, other.attributes[attr], False)
        if not other.is_placeholder():
            self._placeholder = False

    @staticmethod
    def _add_relations(relations_of_self, relations_of_other):
        ''' Adds all relations from other item to own relations.

        Args:
            relations_of_self (dict): Dictionary used to add relations to.
            relations_of_other (dict): Dictionary used to fetch relations from.
        '''
        for relation in relations_of_other:
            if relation not in relations_of_self:
                relations_of_self[relation] = []
            relations_of_self[relation].extend(relations_of_other[relation])

    def is_placeholder(self):
        ''' Gets whether the item is a placeholder or not.

        Returns:
            bool: True if the item is a placeholder, False otherwise.
        '''
        return self._placeholder

    def add_target(self, relation, target, implicit=False):
        ''' Adds a relation to another traceable item.

        Note: using this API, the automatic reverse relation is not created. Adding the relation
        through the TraceableItemCollection class performs the adding of automatic reverse
        relations.

        Args:
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
            implicit (bool): If True, an explicitly expressed relation is added here. If false, an implicite
                             (e.g. automatic reverse) relation is added here.
        '''
        # When target is the item itself, it is an error: no circular relationships
        if self.get_id() == target:
            raise TraceabilityException('circular relationship {src} {rel} {tgt}'.format(src=self.get_id(),
                                                                                         rel=relation,
                                                                                         tgt=target),
                                        self.get_document())
        # When relation is already explicit, we shouldn't add. It is an error.
        if relation in self.explicit_relations and target in self.explicit_relations[relation]:
            raise TraceabilityException('duplicating {src} {rel} {tgt}'.format(src=self.get_id(),
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
            database = self.implicit_relations if implicit else self.explicit_relations
            self._add_target(database, relation, target)

    @staticmethod
    def _add_target(database, relation, target):
        ''' Adds a relation to another traceable item.

        Args:
            database (dict): Dictionary to add the relation to.
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
        '''
        if relation not in database:
            database[relation] = []
        if target not in database[relation]:
            database[relation].append(target)

    @staticmethod
    def _remove_target(database, relation, target):
        ''' Deletes a relation to another traceable item.

        Args:
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
            database (dict): Dictionary to remove the relation from.
        '''
        if relation in database:
            if target in database[relation]:
                database[relation].remove(target)

    def remove_targets(self, target_id, explicit=False, implicit=True):
        ''' Removes any relation to given target item.

        Args:
            target_id (str): Identification of the target items to remove.
            explicit (bool): If True, explicitly expressed relations to given target are removed.
            implicit (bool): If True, implicitly expressed relations to given target are removed.
        '''
        source_databases = []
        if explicit:
            source_databases.append(self.explicit_relations)
        if implicit:
            source_databases.append(self.implicit_relations)
        for database in source_databases:
            for relation in database:
                if target_id in database[relation]:
                    database[relation].remove(target_id)

    def iter_targets(self, relation, explicit=True, implicit=True):
        ''' Gets a naturally sorted list of targets to other traceable item(s).

        Args:
            relation (str): Name of the relation.
            explicit (bool): If True, explicitly expressed relations are included in the returned list.
            implicit (bool): If True, implicitly expressed relations are included in the returned list.

        Returns:
            (list) Naturally sorted list of targets to other traceable item(s).
        '''
        relations = []
        if explicit and relation in self.explicit_relations:
            relations.extend(self.explicit_relations[relation])
        if implicit and relation in self.implicit_relations:
            relations.extend(self.implicit_relations[relation])
        return natsorted(relations)

    def iter_relations(self):
        ''' Iterates over available relations: naturally sorted.

        Returns:
            (list) Naturally sorted list containing available relations in the item.
        '''
        return natsorted(list(self.explicit_relations) + list(self.implicit_relations))

    @staticmethod
    def define_attribute(attr):
        ''' Defines an attribute that can be assigned to traceable items.

        Args:
            attr (TraceableAttribute): Attribute to be assigned.
        '''
        TraceableItem.defined_attributes[attr.get_id()] = attr

    def add_attribute(self, attr, value, overwrite=True):
        ''' Adds an attribute key-value pair to the traceable item.

        Note:
            The given attribute value is compared against defined attribute possibilities. An exception is thrown when
            the attribute value doesn't match the defined regex.

        Args:
            attr (str): Name of the attribute.
            value (str): Value of the attribute.
            overwrite (bool): Overwrite existing attribute value, if any.
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
        ''' Removes an attribute key-value pair from the traceable item.

        Args:
            attr (str): Name of the attribute.
        '''
        if not attr:
            raise TraceabilityException('item {item}: cannot remove invalid attribute {attr}'.format(item=self.get_id(),
                                                                                                     attr=attr),
                                        self.get_document())
        del self.attributes[attr]

    def get_attribute(self, attr):
        ''' Gets the value of an attribute from the traceable item.

        Args:
            attr (str): Name of the attribute.
        Returns:
            (str) Value matching the given attribute key, or '' if attribute does not exist.
        '''
        value = ''
        if attr in self.attributes:
            value = self.attributes[attr]
        return value

    def get_attributes(self, attrs):
        ''' Gets the values of a list of attributes from the traceable item.

        Args:
            attr (list): List of names of the attribute
        Returns:
            (list) List of values matching the given attributes, or an empty list if no attributes exist
        '''
        values = []
        for attr in attrs:
            values.append(self.get_attribute(attr))
        return values

    def iter_attributes(self):
        ''' Iterates over available attributes.

        Sorted as configured by an attribute-sort directive, with the remaining attributes naturally sorted.

        Returns:
            (list) Sorted list containing available attributes in the item.
        '''
        sorted_attributes = [attr for attr in self.attribute_order if attr in self.attributes]
        sorted_attributes.extend(natsorted(set(self.attributes).difference(set(self.attribute_order))))
        return sorted_attributes

    def __str__(self, explicit=True, implicit=True):
        ''' Converts object to string.

        Args:
            explicit (bool)

        Returns:
            (str): String representation of the item.
        '''
        retval = TraceableItem.STRING_TEMPLATE.format(identification=self.get_id())
        retval += '\tPlaceholder: {placeholder}\n'.format(placeholder=self.is_placeholder())
        for attribute in self.attributes:
            retval += '\tAttribute {attribute} = {value}\n'.format(attribute=attribute,
                                                                   value=self.attributes[attribute])
        if explicit:
            retval += self._relations_to_str(self.explicit_relations, 'Explicit')
        if implicit:
            retval += self._relations_to_str(self.implicit_relations, 'Implicit')
        return retval

    @staticmethod
    def _relations_to_str(relations, description):
        ''' Returns the string represtentation of the given relations.

        Args:
            relations (dict): Dictionary of relations.
            description (str): Description of the kind of relations.
        '''
        retval = ''
        for relation in relations:
            retval += '\t{text} {relation}\n'.format(text=description, relation=relation)
            for tgtid in relations[relation]:
                retval += '\t\t{target}\n'.format(target=tgtid)
        return retval

    def is_match(self, regex):
        ''' Checks if the item matches a given regular expression.

        Args:
            regex (str): Regex to match the given item against.

        Returns:
            (bool) True if the given regex matches the item identification.
        '''
        return re.match(regex, self.get_id())

    def attributes_match(self, attributes):
        ''' Checks if item matches a given set of attributes.

        Args:
            attributes (dict): Dictionary with attribute-regex pairs to match the given item against.

        Returns:
            (bool) True if the given attributes match the item attributes.
        '''
        for attr in attributes:
            if not re.match(attributes[attr], self.get_attribute(attr)):
                return False
        return True

    def is_related(self, relations, target_id):
        ''' Checks if a given item is related using a list of relationships.

        Args:
            relations (list): List of relations.
            target_id (str): Identifier of the target item.

        Returns:
            (bool) True if given item is related through the given relationships, False otherwise.
        '''
        for relation in relations:
            if target_id in self.iter_targets(relation, explicit=True, implicit=True):
                return True
        return False

    def to_dict(self):
        ''' Exports item to a dictionary.

        Returns:
            (dict) Dictionary representation of the object.
        '''
        data = {}
        if not self.is_placeholder():
            data = super(TraceableItem, self).to_dict()
            data['attributes'] = self.attributes
            data['targets'] = {}
            for relation in self.iter_relations():
                tgts = self.iter_targets(relation)
                if tgts:
                    data['targets'][relation] = tgts
        return data

    def self_test(self):
        ''' Performs self-test on collection content.

        Raises:
            TraceabilityException: Item is not defined.
            TraceabilityException: Item has an invalid attribute value.
            TraceabilityException: Duplicate target found for item.
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
            if cnt_duplicate:
                raise TraceabilityException('{cnt} duplicate target(s) found for {item} {relation})'
                                            .format(cnt=cnt_duplicate, item=self.get_id(), relation=relation),
                                            self.get_document())
