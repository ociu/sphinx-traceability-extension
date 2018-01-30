'''
Exception classes for traceability
'''


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
