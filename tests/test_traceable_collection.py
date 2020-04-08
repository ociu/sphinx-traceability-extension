from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError:
    from mock import MagicMock, patch, mock_open

import mlx.traceable_item as item
import mlx.traceable_attribute as attribute
import mlx.traceability_exception as exception
import mlx.traceable_collection as dut


class TestTraceableCollection(TestCase):
    docname = 'folder/doc.rst'
    identification_src = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    rev_relation = 'some-random-reverse-relation'
    unidir_relation = 'some-random-unidirectional-relation'
    identification_tgt = 'another-item-to-target'
    attribute_key = 'some-random-attribute-key'
    attribute_regex = 'some-random-attribute value[12]'
    attribute_value_src = 'some-random-attribute value1'
    attribute_value_tgt = 'some-random-attribute value2'
    mock_export_file = '/tmp/my/mocked_export_file.json'

    def setUp(self):
        attr = attribute.TraceableAttribute(self.attribute_key, self.attribute_regex)
        dut.TraceableItem.define_attribute(attr)

    def test_init(self):
        coll = dut.TraceableCollection()
        # Self test should fail as no relations configured
        with self.assertRaises(exception.TraceabilityException):
            coll.self_test(None)

    def test_add_relation_pair_bidir(self):
        coll = dut.TraceableCollection()
        # Initially no relations, so no reverse
        self.assertIsNone(coll.get_reverse_relation(self.fwd_relation))
        relations_iterator = coll.iter_relations()
        self.assertNotIn(self.fwd_relation, relations_iterator)
        self.assertNotIn(self.rev_relation, relations_iterator)
        # Add a bi-directional relation pair
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        # Reverse for fwd should be rev, and vice-versa
        self.assertEqual(self.rev_relation, coll.get_reverse_relation(self.fwd_relation))
        self.assertEqual(self.fwd_relation, coll.get_reverse_relation(self.rev_relation))
        # Verify relations iterator
        relations_iterator = coll.iter_relations()
        self.assertIn(self.fwd_relation, relations_iterator)
        self.assertIn(self.rev_relation, relations_iterator)
        # Self test should pass
        coll.self_test(None)

    def test_add_relation_pair_unidir(self):
        coll = dut.TraceableCollection()
        # Initially no relations, so no reverse
        self.assertIsNone(coll.get_reverse_relation(self.unidir_relation))
        # Add a uni-directional relation pair
        coll.add_relation_pair(self.unidir_relation)
        # Reverse for fwd should be nothing
        self.assertEqual(coll.NO_RELATION_STR, coll.get_reverse_relation(self.unidir_relation))
        # Self test should pass
        coll.self_test(None)

    def test_add_item(self):
        coll = dut.TraceableCollection()
        # Initially no items
        self.assertFalse(coll.has_item(self.identification_src))
        self.assertIsNone(coll.get_item(self.identification_src))
        item_iterator = coll.iter_items()
        self.assertNotIn(self.identification_src, item_iterator)
        self.assertNotIn(self.identification_tgt, item_iterator)
        # Add an item
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add same item: should give warning
        with self.assertRaises(exception.TraceabilityException):
            coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(1, len(coll.items))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add a second item, make sure first one is still there
        self.assertFalse(coll.has_item(self.identification_tgt))
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        self.assertTrue(coll.has_item(self.identification_tgt))
        self.assertEqual(item2, coll.get_item(self.identification_tgt))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Verify iterator
        item_iterator = coll.iter_items()
        self.assertIn(self.identification_src, item_iterator)
        self.assertIn(self.identification_tgt, item_iterator)
        # Self test should pass
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.self_test(None)

    def test_add_item_overwrite(self):
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Add target item: should update existing one (keeping relations)
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        # Assert old relations are still there
        item1_out = coll.get_item(self.identification_src)
        item2_out = coll.get_item(self.identification_tgt)
        relations = item1_out.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item2_out.iter_targets(self.rev_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        # Assert item are not placeholders
        self.assertFalse(item1_out.is_placeholder())
        self.assertFalse(item2_out.is_placeholder())

    def test_add_relation_unknown_source(self):
        # with unknown source item, the generation of a placeholder is expected
        coll = dut.TraceableCollection()
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert placeholder item is created
        item1 = coll.get_item(self.identification_src)
        self.assertIsNotNone(item1)
        self.assertEqual(self.identification_src, item1.get_id())
        self.assertTrue(item1.is_placeholder())
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=False, implicit=True)
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))
        # Self test should fail, as we have a placeholder item
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test(None)

    def test_add_relation_unknown_relation(self):
        # with unknown relation, warning is expected
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item1)
        coll.add_item(item2)
        with self.assertRaises(exception.TraceabilityException):
            coll.add_relation(self.identification_src,
                              self.fwd_relation,
                              self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        # Self test should pass
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.self_test(None)

    def test_add_relation_unknown_target(self):
        # With unknown target item, the generation of a placeholder is expected
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert placeholder item is created
        item2 = coll.get_item(self.identification_tgt)
        self.assertIsNotNone(item2)
        self.assertEqual(self.identification_tgt, item2.get_id())
        self.assertTrue(item2.is_placeholder())
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))
        # Self test should fail, as we have a placeholder item
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test(None)

    def test_add_relation_happy(self):
        # Normal addition of relation, everything is there
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item1)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not a placeholder item
        item2_read = coll.get_item(self.identification_tgt)
        self.assertFalse(item2.is_placeholder())
        self.assertEqual(item2, item2_read)
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))
        # Self test should pass
        coll.self_test(None)

    def test_add_relation_unidirectional(self):
        # Normal addition of uni-directional relation
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation_pair(self.unidir_relation)
        coll.add_relation(self.identification_src,
                          self.unidir_relation,
                          self.identification_tgt)
        # Assert explicit forward relation is created
        relations = item1.iter_targets(self.unidir_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.iter_targets(self.unidir_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not existent
        self.assertIsNone(coll.get_item(self.identification_tgt))
        # Self test should pass
        coll.self_test(None)

    def test_stringify(self):
        coll = dut.TraceableCollection()
        # Assert relation pairs are printed
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        collstr = str(coll)
        self.assertIn(self.fwd_relation, collstr)
        self.assertIn(self.rev_relation, collstr)
        # Add some items and relations, assert they are in the string
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        coll.add_item(item1)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        collstr = str(coll)
        self.assertIn(self.identification_src, collstr)
        self.assertIn(self.identification_tgt, collstr)

    def test_get_items(self):
        coll = dut.TraceableCollection()
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        self.assertEqual(0, len(coll.get_items(r'\w*')))
        item1 = item.TraceableItem(self.identification_src)
        coll.add_item(item1)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # placeholder should be excluded
        self.assertEqual(1, len(coll.get_items(r'\w*')))
        item2 = item.TraceableItem(self.identification_tgt)
        # placeholder is replaced by actual item
        coll.add_item(item2)
        self.assertEqual(2, len(coll.get_items(r'\w*')))
        # Empty filter should match all items
        self.assertEqual(2, len(coll.get_items('')))

    def test_get_items_attribute(self):
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        coll.add_item(item1)
        item2 = item.TraceableItem(self.identification_tgt)
        coll.add_item(item2)
        self.assertEqual(2, len(coll.get_items('')))
        self.assertEqual(0, len(coll.get_items('', {self.attribute_key: self.attribute_value_src})))
        self.assertEqual(0, len(coll.get_items('', {self.attribute_key: self.attribute_value_tgt})))
        item1.add_attribute(self.attribute_key, self.attribute_value_src)
        self.assertEqual(1, len(coll.get_items('', {self.attribute_key: self.attribute_value_src})))
        self.assertEqual(0, len(coll.get_items('', {self.attribute_key: self.attribute_value_tgt})))
        item2.add_attribute(self.attribute_key, self.attribute_value_tgt)
        self.assertEqual(1, len(coll.get_items('', {self.attribute_key: self.attribute_value_src})))
        self.assertEqual(1, len(coll.get_items('', {self.attribute_key: self.attribute_value_tgt})))

    def test_get_items_sortattributes(self):
        name1 = 'z11'
        name2 = 'z2'
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(name1)
        coll.add_item(item1)
        item2 = item.TraceableItem(name2)
        coll.add_item(item2)
        attribute_regex = '0x[0-9A-Z]+'
        attr = attribute.TraceableAttribute(self.attribute_key, attribute_regex)
        dut.TraceableItem.define_attribute(attr)
        item1.add_attribute(self.attribute_key, '0x0029')
        item2.add_attribute(self.attribute_key, '0x003A')
        # Alphabetical sorting: 0x0029 before 0x003A
        self.assertEqual(item1.get_id(), coll.get_items('', sortattributes=[self.attribute_key])[0])
        self.assertEqual(item2.get_id(), coll.get_items('', sortattributes=[self.attribute_key])[1])
        # Natural sorting: z2 before z11
        self.assertEqual(item2.get_id(), coll.get_items('')[0])
        self.assertEqual(item1.get_id(), coll.get_items('')[1])

    def test_related(self):
        coll = dut.TraceableCollection()
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        self.assertFalse(coll.are_related(self.identification_src, [], self.identification_tgt))
        item1 = item.TraceableItem(self.identification_src)
        coll.add_item(item1)
        self.assertFalse(coll.are_related(self.identification_src, [], self.identification_tgt))
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # placeholder should be excluded
        self.assertFalse(coll.are_related(self.identification_src, [], self.identification_tgt))
        item2 = item.TraceableItem(self.identification_tgt)
        # placeholder is replaced by actual item
        coll.add_item(item2)
        self.assertTrue(coll.are_related(self.identification_src, [], self.identification_tgt))
        self.assertTrue(coll.are_related(self.identification_src, [self.fwd_relation],
                                         self.identification_tgt))
        self.assertTrue(coll.are_related(self.identification_src, [self.fwd_relation, 'another-relation'],
                                         self.identification_tgt))

    def test_selftest(self):
        coll = dut.TraceableCollection()
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        # Self test should pass
        coll.self_test(None)
        # Create first item
        item1 = item.TraceableItem(self.identification_src)
        item1.set_document(self.docname)
        # Improper use: add target on item level (no sanity check and no automatic reverse link)
        item1.add_target(self.fwd_relation, self.identification_tgt)
        # Improper use is not detected at level of item-level
        item1.self_test()
        # Add item to collection
        coll.add_item(item1)
        # Self test should fail as target item is not in collection
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test(None)
        # Self test one limited scope (no matching document), should pass
        coll.self_test(None, docname='document-does-not-exist.rst')
        # Creating and adding second item, self test should still fail as no automatic reverse relation
        item2 = item.TraceableItem(self.identification_tgt)
        item2.set_document(self.docname)
        coll.add_item(item2)
        with self.assertRaises(dut.MultipleTraceabilityExceptions):
            coll.self_test(None)
        # Mimicing the automatic reverse relation, self test should pass
        item2.add_target(self.rev_relation, self.identification_src)
        coll.self_test(None)

    def test_export_no_items(self):
        open_mock = mock_open()
        coll = dut.TraceableCollection()
        with patch('mlx.traceable_collection.open', open_mock, create=True):
            coll.export(self.mock_export_file)
        open_mock.assert_called_once_with(self.mock_export_file, 'w')

    @patch('mlx.traceable_collection.json', autospec=True)
    def test_export_single_item(self, json_mock):
        json_mock_object = MagicMock(spec=dut.json)
        json_mock.return_value = json_mock_object
        open_mock = mock_open()
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem(self.identification_src)
        coll.add_item(item1)
        with patch('mlx.traceable_collection.open', open_mock, create=True):
            coll.export(self.mock_export_file)
        open_mock.assert_called_once_with(self.mock_export_file, 'w')

    def test_add_attribute_sorting_rule(self):
        coll = dut.TraceableCollection()
        item1 = item.TraceableItem('ABC')
        coll.add_item(item1)
        item2 = item.TraceableItem('DEF')
        coll.add_item(item2)
        attribute_regex = r'\w+'

        for attr_key in ('small', 'large', 'number'):
            attr = attribute.TraceableAttribute(attr_key, attribute_regex)
            dut.TraceableItem.define_attribute(attr)
            item1.add_attribute(attr_key, 'small')

        for attr_key in ('small', 'large', 'number', 'attr2'):
            attr = attribute.TraceableAttribute(attr_key, attribute_regex)
            dut.TraceableItem.define_attribute(attr)
            item2.add_attribute(attr_key, 'small')

        ignored1 = coll.add_attribute_sorting_rule('AB', ['number', 'small', 'large', 'attr2'])
        ignored2 = coll.add_attribute_sorting_rule('[A-Z]+', ['small', 'large'])  # item ABC must get ignored

        attributes_item1 = item1.iter_attributes()
        attributes_item2 = item2.iter_attributes()

        self.assertEqual(item1.attribute_order, ['number', 'small', 'large', 'attr2'])
        self.assertEqual(item2.attribute_order, ['small', 'large'])
        self.assertEqual(attributes_item1, ['number', 'small', 'large'])
        self.assertEqual(attributes_item2, ['small', 'large', 'attr2', 'number'])
        self.assertEqual(ignored1, [])
        self.assertEqual(ignored2, [item1])
