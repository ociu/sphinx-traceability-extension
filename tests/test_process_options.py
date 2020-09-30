from unittest import TestCase
from unittest.mock import Mock
from sphinx.application import Sphinx

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceable_base_node import TraceableBaseNode
from docutils.parsers.rst import directives


class FakeNode(TraceableBaseNode):

    def perform_replacement():
        pass


class FakeDirectiveClass(TraceableBaseDirective):
    """ Fake class with a fake optionspec """
    # Optional argument: title (whitespace allowed)
    optional_arguments = 1
    # Options
    option_spec = {
        'commalist_arg': directives.class_option,
        'string_arg': directives.unchanged,
        'spacelist_arg': directives.unchanged,
    }
    # Content disallowed
    has_content = False

    def run():
        pass


class TestTraceableBaseClass(TestCase):

    def setUp(self):
        self.app = Mock(spec=Sphinx)
        self.app.config = Mock()
        self.app.config.traceability_hyperlink_colors = {}

    def test_with_empty_options(self):
        fake_node = FakeNode('')
        fake_node['document'] = 'fake_doc'
        fake_node['line'] = 0
        self.node = FakeDirectiveClass(name="testdirective",
                                       arguments=None,
                                       options=[],
                                       content='',
                                       lineno=0,
                                       content_offset=0,
                                       block_text='',
                                       state=None,
                                       state_machine=None)

        self.assertNotIn('commalist_arg', fake_node)
        self.assertNotIn('string_arg', fake_node)
        self.assertNotIn('spacelist_arg', fake_node)
        self.node.process_options(fake_node,
                                  {'commalist_arg':   {'default': ['element1', 'element2'], 'delimiter': ','},
                                   'string_arg':  {'default': 'element3'},
                                   'spacelist_arg':    {'default': ['element4', 'element5']}})
        self.assertEqual(fake_node['commalist_arg'], ['element1', 'element2'])
        self.assertEqual(fake_node['string_arg'], 'element3')
        self.assertEqual(fake_node['spacelist_arg'], ['element4', 'element5'])

    def test_with_existing_options(self):
        fake_node = FakeNode('')
        fake_node['document'] = 'fake_doc'
        fake_node['line'] = 0
        self.node = FakeDirectiveClass(name="testdirective",
                                       arguments=None,
                                       options={'commalist_arg': 'new_element1,     new_element2',
                                                'string_arg': 'some_other_string',
                                                'spacelist_arg': "   new_element4     new_element5",
                                                },
                                       content='',
                                       lineno=0,
                                       content_offset=0,
                                       block_text='',
                                       state=None,
                                       state_machine=None)

        self.assertNotIn('commalist_arg', fake_node)
        self.assertNotIn('string_arg', fake_node)
        self.assertNotIn('spacelist_arg', fake_node)
        self.node.process_options(fake_node,
                                  {'commalist_arg':   {'default': ['element1', 'element2'], 'delimiter': ','},
                                   'string_arg':  {'default': 'element3'},
                                   'spacelist_arg':    {'default': ['element4', 'element5']}})
        self.assertEqual(fake_node['commalist_arg'], ['new_element1', 'new_element2'])
        self.assertEqual(fake_node['string_arg'], 'some_other_string')
        self.assertEqual(fake_node['spacelist_arg'], ['new_element4', 'new_element5'])

    def test_with_just_one_existing_option(self):
        fake_node = FakeNode('')
        fake_node['document'] = 'fake_doc'
        fake_node['line'] = 0
        self.node = FakeDirectiveClass(name="testdirective",
                                       arguments=None,
                                       options={'string_arg': 'some_other_string'},
                                       content='',
                                       lineno=0,
                                       content_offset=0,
                                       block_text='',
                                       state=None,
                                       state_machine=None)

        self.assertNotIn('commalist_arg', fake_node)
        self.assertNotIn('string_arg', fake_node)
        self.assertNotIn('spacelist_arg', fake_node)
        self.node.process_options(fake_node,
                                  {'commalist_arg':   {'default': ['element1', 'element2'], 'delimiter': ','},
                                   'string_arg':  {'default': 'element3'},
                                   'spacelist_arg':    {'default': ['element4', 'element5']}})
        self.assertEqual(fake_node['commalist_arg'], ['element1', 'element2'])
        self.assertEqual(fake_node['string_arg'], 'some_other_string')
        self.assertEqual(fake_node['spacelist_arg'], ['element4', 'element5'])
