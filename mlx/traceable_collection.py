'''
Storage classes for collection of traceable items
'''

import json
from natsort import natsorted
from mlx.traceable_item import TraceableItem
from mlx.traceability_exception import TraceabilityException, MultipleTraceabilityExceptions


class TraceableCollection:
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
        Iterate over available relations: naturally sorted

        Returns:
            Naturally sorted list over available relations in the collection
        '''
        return natsorted(self.relations)

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
            if not olditem.is_placeholder():
                raise TraceabilityException('duplicating {itemid}'.format(itemid=itemid), item.get_document())
            # ... otherwise, update the item with new content
            else:
                item.update(olditem)
        # add it
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
        Iterate over items: naturally sorted identification

        Returns:
            Sorted iterator over identification of the items in the collection
        '''
        return natsorted(self.items)

    def has_item(self, itemid):
        '''
        Verify if a item with given id is in the collection

        Args:
            itemid (str): Identification of item to look for
        Returns:
            bool: True if the given itemid is in the collection, false otherwise
        '''
        return itemid in self.items

    def add_relation(self, source_id, relation, target_id):
        '''
        Add relation between two items

        The function adds the forward and the automatic reverse relation.

        Args:
            source_id (str): ID of the source item
            relation (str): Relation between source and target item
            target_id (str): ID of the target item
        '''
        # Add placeholder if source item is unknown
        if source_id not in self.items:
            src = TraceableItem(source_id, True)
            self.add_item(src)
        source = self.items[source_id]
        # Error if relation is unknown
        if relation not in self.relations:
            raise TraceabilityException('Relation {name} not known'.format(name=relation), source.get_document())
        # Add forward relation
        source.add_target(relation, target_id)
        # When reverse relation exists, continue to create/adapt target-item
        reverse_relation = self.get_reverse_relation(relation)
        if reverse_relation:
            # Add placeholder if target item is unknown
            if target_id not in self.items:
                tgt = TraceableItem(target_id, True)
                self.add_item(tgt)
            # Add reverse relation to target-item
            self.items[target_id].add_target(reverse_relation, source_id, implicit=True)

    def export(self, fname):
        '''
        Export collection content

        Args:
            fname (str): Path to the json file to export
        '''
        with open(fname, 'w') as outfile:
            data = []
            for itemid in self.iter_items():
                item = self.get_item(itemid)
                data.append(item.to_dict())
            json.dump(data, outfile, indent=4, sort_keys=True)

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
                        errors.append(TraceabilityException("{source} {relation} {target}, but {target} is not known"
                                                            .format(source=itemid,
                                                                    relation=relation,
                                                                    target=tgt),
                                                            item.get_document()))
                        continue
                    # Reverse relation exists?
                    target = self.get_item(tgt)
                    if itemid not in target.iter_targets(rev_relation):
                        errors.append(TraceabilityException("No automatic reverse relation: {source} {relation} "
                                                            "{target}".format(source=tgt,
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

    def are_related(self, source_id, relations, target_id):
        '''
        Check if 2 items are related using a list of relationships

        Placeholders are excluded

        Args:
            source_id (str): id of the source item
            relations (list): list of relations, empty list for wildcard
            target_id (str): id of the target item
        Returns:
            (boolean) True if both items are related through the given relationships, false otherwise
        '''
        if source_id not in self.items:
            return False
        source = self.items[source_id]
        if not source or source.is_placeholder():
            return False
        if target_id not in self.items:
            return False
        target = self.items[target_id]
        if not target or target.is_placeholder():
            return False
        if not relations:
            relations = self.iter_relations()
        return self.items[source_id].is_related(relations, target_id)

    def get_items(self, regex, attributes=None, sortattributes=None, reverse=False):
        '''
        Get all items that match a given regular expression

        Placeholders are excluded

        Args:
            regex (str): Regex to match the items in this collection against
            attributes (dict): Dictionary with attribute-regex pairs to match the items in this collection against
            sortattributes (list): List of attributes on which to alphabetically sort the items
            reverse (bool): True for reverse sorting
        Returns:
            A sorted list of item-id's matching the given regex. Sorting is done naturally when sortattributes is
            unused.
        '''
        matches = []
        for itemid in self.items:
            if self.items[itemid].is_placeholder():
                continue
            if self.items[itemid].is_match(regex) and \
                    (not attributes or self.items[itemid].attributes_match(attributes)):
                matches.append(itemid)
        if sortattributes:
            matches = sorted(matches, key=lambda itemid: self.get_item(itemid).get_attributes(sortattributes),
                             reverse=reverse)
        else:
            matches = natsorted(matches, reverse=reverse)
        return matches
