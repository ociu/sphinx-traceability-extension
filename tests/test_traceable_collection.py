from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableCollection(TestCase):
    identification_src = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    rev_relation = 'some-random-reverse-relation'
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
        self.assertIsNone(coll.get_reverse_relation(self.fwd_relation))
        # Add a uni-directional relation pair
        coll.add_relation_pair(self.fwd_relation)
        # Reverse for fwd should be rev, and vice-versa
        self.assertEqual(coll.NO_REVERSE_RELATION_STR, coll.get_reverse_relation(self.fwd_relation))
        self.assertIsNone(coll.get_reverse_relation(self.rev_relation))

    def test_add_item(self):
        coll = dut.TraceableCollection()
        # Initially no items
        self.assertIsNone(coll.get_item(self.identification_src))
        # Add an item
        item = dut.TraceableItem(self.identification_src)
        coll.add_item(item)
        self.assertEqual(item, coll.get_item(self.identification_src))
        # Add same item: should give warning
        # TODO: assert error to be logged
        coll.add_item(item)
        self.assertEqual(1, len(coll.items))
        self.assertEqual(item, coll.get_item(self.identification_src))
