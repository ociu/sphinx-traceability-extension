from unittest import TestCase
from unittest.mock import Mock, MagicMock

from sphinx.application import Sphinx
from sphinx.builders.latex import LaTeXBuilder
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment import BuildEnvironment

from mlx.directives.item_directive import Item as dut
from mlx.traceable_collection import TraceableCollection
from mlx.traceable_item import TraceableItem


class TestItemDirective(TestCase):

    def setUp(self):
        self.app = Mock(spec=Sphinx)
        self.node = dut('')
        self.node['document'] = 'some_doc'
        self.node['id'] = 'some_id'
        self.node['line'] = 1
        self.item = TraceableItem(self.node['id'])
        self.item.set_document(self.node['document'], self.node['line'])
        self.item.bind_node(self.node)
        self.app.config = Mock()
        self.app.config.traceability_hyperlink_colors = {}

    def test_make_internal_item_ref_no_caption(self):
        mock_builder = MagicMock(spec=StandaloneHTMLBuilder)
        mock_builder.env = BuildEnvironment()
        self.app.builder = mock_builder
        self.app.builder.env.traceability_collection = TraceableCollection()
        self.app.builder.env.traceability_collection.add_item(self.item)
        p_node = self.node.make_internal_item_ref(self.app, self.node['id'], True)

        self.assertEqual(len(p_node.children[0].children[0].children), 1)
        self.assertEqual(str(p_node.children[0].children[0]), '<emphasis>some_id</emphasis>')
        self.assertEqual(p_node.children[0].tagname, 'reference')
        self.assertEqual(p_node.children[0].children[0].rawsource, 'some_id')

    def test_make_internal_item_ref_show_caption(self):
        mock_builder = MagicMock(spec=StandaloneHTMLBuilder)
        mock_builder.env = BuildEnvironment()
        self.app.builder = mock_builder
        self.app.builder.env.traceability_collection = TraceableCollection()
        self.app.builder.env.traceability_collection.add_item(self.item)
        self.item.set_caption('caption text')
        p_node = self.node.make_internal_item_ref(self.app, self.node['id'], True)

        self.assertEqual(len(p_node.children[0].children[0].children), 1)
        self.assertEqual(str(p_node.children[0].children[0]), '<emphasis>some_id : caption text</emphasis>')
        self.assertEqual(p_node.children[0].tagname, 'reference')
        self.assertEqual(p_node.children[0].children[0].rawsource, 'some_id : caption text')

    def test_make_internal_item_ref_hide_caption(self):
        mock_builder = MagicMock(spec=StandaloneHTMLBuilder)
        mock_builder.env = BuildEnvironment()
        self.app.builder = mock_builder
        self.app.builder.env.traceability_collection = TraceableCollection()
        self.app.builder.env.traceability_collection.add_item(self.item)
        self.item.set_caption('caption text')
        p_node = self.node.make_internal_item_ref(self.app, self.node['id'], False)

        self.assertEqual(len(p_node.children[0].children[0].children), 2)
        self.assertEqual(str(p_node.children[0].children[0]),
                         '<emphasis classes="has_hidden_caption">some_id'
                         '<inline classes="popup_caption">caption text</inline>'
                         '</emphasis>')
        self.assertEqual(p_node.children[0].tagname, 'reference')
        self.assertEqual(p_node.children[0].children[0].rawsource, 'some_id')

    def test_make_internal_item_ref_hide_caption_latex(self):
        mock_builder = MagicMock(spec=LaTeXBuilder)
        mock_builder.env = BuildEnvironment()
        self.app.builder = mock_builder
        self.app.builder.env.traceability_collection = TraceableCollection()
        self.app.builder.env.traceability_collection.add_item(self.item)
        self.item.set_caption('caption text')
        p_node = self.node.make_internal_item_ref(self.app, self.node['id'], False)

        self.assertEqual(len(p_node.children[0].children[0].children), 1)
        self.assertEqual(str(p_node.children[0].children[0]), '<emphasis>some_id</emphasis>')
        self.assertEqual(p_node.children[0].tagname, 'reference')
        self.assertEqual(p_node.children[0].children[0].rawsource, 'some_id')
