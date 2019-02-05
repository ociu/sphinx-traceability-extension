'''
Storage class for traceable item attribute
'''

import re


class TraceableAttribute(object):
    '''
    Storage for an attribute to a traceable documentation item
    '''

    def __init__(self, attrid, value):
        '''
        Initialize a new attribute

        Args:
            attrid (str): Attribute identification, converted to lowercase as sphinx only allows lower case arguments
            value (str): Regex to which the attribute values should match
        '''
        self.id = attrid.lower()
        self.value = value
        self.name = attrid
        self.caption = None
        self.docname = None

    def get_id(self):
        '''
        Getter for attribute identification

        Returns:
            str: attribute identification
        '''
        return self.id

    def can_accept(self, value):
        '''
        Check whether a certain value can be accepted for attribute value

        Args:
            value (str): Value to be checked against validness
        '''
        return re.match(self.value, value)

    def set_name(self, name):
        '''
        Set readable name of attribute

        Args:
            name (str): Short name of the attribute
        '''
        self.name = name

    def get_name(self):
        '''
        Get readable name of attribute

        Returns:
            str: Short name of the attribute
        '''
        return self.name

    def set_caption(self, caption):
        '''
        Set caption of attribute

        Args:
            caption (str): Short caption of the attribute
        '''
        self.caption = caption

    def get_caption(self):
        '''
        Get caption of attribute

        Returns:
            str: Short caption of the attribute
        '''
        return self.caption

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


