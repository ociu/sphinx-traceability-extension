from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableCollection(TestCase):
    identification_src = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    rev_relation = 'some-random-reverse-relation'
    unidir_relation = 'some-random-unidirectional-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        coll = dut.TraceableCollection()

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

    def test_add_relation_pair_unidir(self):
        coll = dut.TraceableCollection()
        # Initially no relations, so no reverse
        self.assertIsNone(coll.get_reverse_relation(self.unidir_relation))
        # Add a uni-directional relation pair
        coll.add_relation_pair(self.unidir_relation)
        # Reverse for fwd should be nothing
        self.assertEqual(coll.NO_REVERSE_RELATION_STR, coll.get_reverse_relation(self.unidir_relation))

    def test_add_item(self):
        coll = dut.TraceableCollection()
        # Initially no items
        self.assertFalse(coll.has_item(self.identification_src))
        self.assertIsNone(coll.get_item(self.identification_src))
        item_iterator = coll.iter_items()
        self.assertNotIn(self.identification_src, item_iterator)
        self.assertNotIn(self.identification_tgt, item_iterator)
        # Add an item
        item1 = dut.TraceableItem(self.identification_src)
        coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add same item: should give warning
        # TODO: assert error to be logged
        coll.add_item(item1)
        self.assertTrue(coll.has_item(self.identification_src))
        self.assertEqual(1, len(coll.items))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add a second item, make sure first one is still there
        self.assertFalse(coll.has_item(self.identification_tgt))
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item2)
        self.assertTrue(coll.has_item(self.identification_tgt))
        self.assertEqual(item2, coll.get_item(self.identification_tgt))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Verify iterator
        item_iterator = coll.iter_items()
        self.assertIn(self.identification_src, item_iterator)
        self.assertIn(self.identification_tgt, item_iterator)

    def test_add_relation_unknown_source(self):
        # with unknown source item, exception is expected
        coll = dut.TraceableCollection()
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        with self.assertRaises(ValueError):
            coll.add_relation(self.identification_src,
                              self.fwd_relation,
                              self.identification_tgt)

    def test_add_relation_unknown_relation(self):
        # with unknown relation, warning is expected
        # TODO: expect error to be logged
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item1)
        coll.add_item(item2)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))

    def test_add_relation_unknown_target(self):
        # With unknown target item, the generation of a placeholder is expected
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
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
        self.assertTrue(item2.placeholder)
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))

    def test_add_relation_happy(self):
        # Normal addition of relation, everything is there
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item2 = dut.TraceableItem(self.identification_tgt)
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
        self.assertFalse(item2.placeholder)
        self.assertEqual(item2, item2_read)
        # Assert implicit reverse relation is created
        relations = item2.iter_targets(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.iter_targets(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(0, len(relations))

    def test_add_relation_unidirectional(self):
        # Normal addition of uni-directional relation
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
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

    def test_remove_item_with_implicit_relations(self):
        # Normal addition of relation, everything is there
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item1)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert forward relation is created
        relations = item1.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        # Assert reverse relation is created
        relations = item2.iter_targets(self.rev_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        # Remove
        coll.remove_item(self.identification_src)
        # Assert item is gone
        self.assertIsNone(coll.get_item(self.identification_src))
        # Assert implicit relations to this item are removed
        relations = item2.iter_targets(self.rev_relation)
        self.assertEqual(0, len(relations))

    def test_remove_item_with_explicit_relations(self):
        # Normal addition of relation, everything is there
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item1)
        coll.add_item(item2)
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        # Assert forward relation is created
        relations = item1.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        # Assert reverse relation is created
        relations = item2.iter_targets(self.rev_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        # Remove
        coll.remove_item(self.identification_tgt)
        # Assert item is gone
        self.assertIsNone(coll.get_item(self.identification_tgt))
        # Assert explicit relations to this item are not removed
        relations = item1.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)

    def test_purge(self):
        coll = dut.TraceableCollection()
        # Add item in first document
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document('a.rst', 111)
        coll.add_item(item1)
        self.assertEqual('a.rst', coll.get_item(self.identification_src).docname)
        # Add item in second document
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document('b.rst', 222)
        coll.add_item(item2)
        self.assertEqual('b.rst', coll.get_item(self.identification_tgt).docname)
        # Purge first document
        coll.purge('a.rst')
        # Assert first item is gone, second one is still there
        self.assertIsNone(coll.get_item(self.identification_src))
        self.assertEqual(self.identification_tgt, coll.get_item(self.identification_tgt).get_id())
        # Purge second document
        coll.purge('b.rst')
        # Assert second item is gone
        self.assertIsNone(coll.get_item(self.identification_tgt))

    def test_purge_with_relations(self):
        coll = dut.TraceableCollection()
        # Add item in first document
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document('a.rst', 111)
        coll.add_item(item1)
        # Add item in second document
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document('b.rst', 222)
        coll.add_item(item2)
        # Add relation in between them
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        coll.add_relation(self.identification_src,
                          self.fwd_relation,
                          self.identification_tgt)
        relations = item1.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item2.iter_targets(self.rev_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        # Purge first document
        coll.purge('a.rst')
        # Assert first item is gone, second one is still there
        self.assertIsNone(coll.get_item(self.identification_src))
        self.assertEqual(self.identification_tgt, coll.get_item(self.identification_tgt).get_id())
        # Assert implicit relation to first item is removed
        relations = item2.iter_targets(self.rev_relation)
        self.assertEqual(0, len(relations))
