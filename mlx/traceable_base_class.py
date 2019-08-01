'''
Base class for traceable stuff
'''

from mlx.traceability_exception import TraceabilityException


class TraceableBaseClass(object):
    '''
    Storage for a traceable base class
    '''

    def __init__(self, name):
        '''
        Initialize a new base class

        Args:
            name (str): Base class object identification
        '''
        self.id = self.to_id(name)
        self.name = name
        self.caption = None
        self.docname = None
        self.lineno = None
        self.node = None
        self.content = None

    @staticmethod
    def to_id(id):
        '''
        Convert a given identification to a storable id

        Args:
            id (str): input identification
        Returns:
            str - Converted storable identification
        '''
        return id

    def update(self, other):
        '''
        Update with new object

        Store the sum of both objects
        '''
        if self.id != other.id:
            raise ValueError('Update error {old} vs {new}'.format(old=self.id, new=other.id))
        if other.name is not None:
            self.name = other.name
        if other.docname is not None:
            self.docname = other.docname
        if other.lineno is not None:
            self.lineno = other.lineno
        if other.node is not None:
            self.node = other.node
        if other.caption is not None:
            self.caption = other.caption
        if other.content is not None:
            self.content = other.content

    def get_id(self):
        '''
        Getter for identification

        Returns:
            str: identification
        '''
        return self.id

    def set_name(self, name):
        '''
        Set readable name

        Args:
            name (str): Short name
        '''
        self.name = name

    def get_name(self):
        '''
        Get readable name

        Returns:
            str: Short name
        '''
        return self.name

    def set_caption(self, caption):
        '''
        Set caption

        Args:
            caption (str): Short caption
        '''
        self.caption = caption

    def get_caption(self):
        '''
        Get caption

        Returns:
            str: Short caption
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

    def to_dict(self):
        '''
        Export to dictionary

        Returns:
            (dict) Dictionary representation of the object
        '''
        data = {}
        data['id'] = self.get_id()
        data['name'] = self.get_name()
        caption = self.get_caption()
        if caption:
            data['caption'] = caption
        data['document'] = self.docname
        data['line'] = self.lineno
        return data

    def self_test(self):
        '''
        Perform self test on content
        '''
        # should hold a reference to a document
        if self.get_document() is None:
            raise TraceabilityException("Item '{identification}' has no reference to source document."
                                        .format(identification=self.get_id()))
