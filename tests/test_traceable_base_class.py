from unittest import TestCase

import mlx.traceability_exception as exception
import mlx.traceable_base_class as dut


class TestTraceableBaseClass(TestCase):
    name = 'silly-Name'
    docname = 'folder/doc.rst'
    identification = 'some-random$name\'with<\"weird@symbols'

    def test_init(self):
        item = dut.TraceableBaseClass(self.identification)
        item.set_document(self.docname)
        item.self_test()
        self.assertEqual(self.identification, item.get_id())
        self.assertIsNotNone(item.get_document())
        self.assertEqual(0, item.get_line_number())
        self.assertEqual(self.identification, item.get_name())
        self.assertIsNone(item.get_node())
        self.assertIsNone(item.get_caption())
        self.assertIsNone(item.get_content())

    def test_set_name(self):
        item = dut.TraceableBaseClass(self.identification)
        item.set_name(self.name)
        self.assertEqual(self.name, item.get_name())

    def test_set_document(self):
        item = dut.TraceableBaseClass(self.identification)
        with self.assertRaises(exception.TraceabilityException):
            item.self_test()
        item.set_document('some-file.rst', 888)
        self.assertEqual('some-file.rst', item.get_document())
        self.assertEqual(888, item.get_line_number())
        item.self_test()

    def test_bind_node(self):
        item = dut.TraceableBaseClass(self.identification)
        item.set_document(self.docname)
        node = object()
        item.bind_node(node)
        self.assertEqual(node, item.get_node())
        item.self_test()

    def test_set_caption(self):
        txt = 'some short description'
        item = dut.TraceableBaseClass(self.identification)
        item.set_document(self.docname)
        item.set_caption(txt)
        self.assertEqual(txt, item.get_caption())
        # Verify dict
        data = item.to_dict()
        self.assertEqual(self.identification, data['id'])
        self.assertEqual(txt, data['caption'])
        self.assertEqual(self.docname, data['document'])
        self.assertEqual(0, data['line'])
        self.assertEqual("0", data['content-hash'])
        item.self_test()

    def test_set_content(self):
        txt = 'some description, with\n newlines and other stuff'
        item = dut.TraceableBaseClass(self.identification)
        item.set_document(self.docname)
        item.set_content(txt)
        self.assertEqual(txt, item.get_content())
        data = item.to_dict()
        self.assertEqual("b787a17fc91c9cf37b5bf0665f13c8b1", data['content-hash'])
        item.self_test()
