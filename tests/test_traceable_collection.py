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
        # Add a bi-directional relation pair
        coll.add_relation_pair(self.fwd_relation, self.rev_relation)
        # Reverse for fwd should be rev, and vice-versa
        self.assertEqual(self.rev_relation, coll.get_reverse_relation(self.fwd_relation))
        self.assertEqual(self.fwd_relation, coll.get_reverse_relation(self.rev_relation))

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
        self.assertIsNone(coll.get_item(self.identification_src))
        # Add an item
        item1 = dut.TraceableItem(self.identification_src)
        coll.add_item(item1)
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add same item: should give warning
        # TODO: assert error to be logged
        coll.add_item(item1)
        self.assertEqual(1, len(coll.items))
        self.assertEqual(item1, coll.get_item(self.identification_src))
        # Add a second item, make sure first one is still there
        item2 = dut.TraceableItem(self.identification_tgt)
        coll.add_item(item2)
        self.assertEqual(item2, coll.get_item(self.identification_tgt))
        self.assertEqual(item1, coll.get_item(self.identification_src))

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

    def test_purge(self):
        coll = dut.TraceableCollection()
        item1 = dut.TraceableItem(self.identification_src)
        item1.set_document('a.rst', 111)
        coll.add_item(item1)
        self.assertEqual('a.rst', coll.get_item(self.identification_src).docname)
        item2 = dut.TraceableItem(self.identification_tgt)
        item2.set_document('b.rst', 222)
        coll.add_item(item2)
        self.assertEqual('b.rst', coll.get_item(self.identification_tgt).docname)
        coll.purge('a.rst')
        self.assertIsNone(coll.get_item(self.identification_src))
        self.assertEqual(self.identification_tgt, coll.get_item(self.identification_tgt).get_id())

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
        relations = item1.get_relations(self.fwd_relation, explicit=True, implicit=True)
        self.assertEqual(0, len(relations))
        relations = item2.get_relations(self.fwd_relation, explicit=True, implicit=True)
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
        relations = item1.get_relations(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.get_relations(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert placeholder item is created
        item2 = coll.get_item(self.identification_tgt)
        self.assertIsNotNone(item2)
        self.assertEqual(self.identification_tgt, item2.get_id())
        self.assertTrue(item2.placeholder)
        # Assert implicit reverse relation is created
        relations = item2.get_relations(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.get_relations(self.fwd_relation, explicit=True, implicit=False)
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
        relations = item1.get_relations(self.fwd_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.get_relations(self.fwd_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not a placeholder item
        item2_read = coll.get_item(self.identification_tgt)
        self.assertFalse(item2.placeholder)
        self.assertEqual(item2, item2_read)
        # Assert implicit reverse relation is created
        relations = item2.get_relations(self.rev_relation, explicit=False, implicit=True)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_src)
        relations = item2.get_relations(self.fwd_relation, explicit=True, implicit=False)
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
        relations = item1.get_relations(self.unidir_relation, explicit=True, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item1.get_relations(self.unidir_relation, explicit=False, implicit=True)
        self.assertEqual(0, len(relations))
        # Assert item2 is not existent
        self.assertIsNone(coll.get_item(self.identification_tgt))
