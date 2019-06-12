'''
Storage class for traceable item attribute
'''

import re
from mlx.traceable_base_class import TraceableBaseClass


class TraceableAttribute(TraceableBaseClass):
    '''
    Storage for an attribute to a traceable documentation item
    '''

    def __init__(self, attrid, value):
        '''
        Initialize a new attribute

        Args:
            attrid (str): Attribute identification
            value (str): Regex to which the attribute values should match
        '''
        super(TraceableAttribute, self).__init__(attrid)
        self.value = value

    @staticmethod
    def to_id(id):
        '''
        Convert a given identification to a storable id

        Args:
            id (str): input identification
        Returns:
            str - Converted storable identification
        '''
        return id.lower()

    def update(self, other):
        '''
        Update with new object

        Store the sum of both objects
        '''
        super(TraceableAttribute, self).update(other)
        if other.value is not None:
            self.value = other.value

    def can_accept(self, value):
        '''
        Check whether a certain value can be accepted for attribute value

        Args:
            value (str): Value to be checked against validness
        '''
        return re.match(self.value, value)
