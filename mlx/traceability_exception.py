'''
Exception classes for traceability
'''
from sphinx import __version__ as sphinx_version
if sphinx_version >= '1.6.0':
    from sphinx.util.logging import getLogger


def report_warning(env, msg, docname=None, lineno=None):
    '''Convenience function for logging a warning

    Args:
        env (sphinx.environment.BuildEnvironment): Sphinx' build environment.
        msg (any __str__): Message of the warning, gets converted to str.
        docname (str): Relative path to the document on which the error occured, without extension.
        lineno (int): Line number in the document on which the error occured.
    '''
    msg = str(msg)
    if sphinx_version >= '1.6.0':
        logger = getLogger(__name__)
        if lineno is not None:
            logger.warning(msg, location=(docname, str(lineno)))
        else:
            logger.warning(msg, location=docname)
    else:
        env.warn(docname, msg, lineno=lineno)


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
