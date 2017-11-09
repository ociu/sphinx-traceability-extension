from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableItem(TestCase):
    identification = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        item = dut.TraceableItem(self.identification)
        self.assertEqual(self.identification, item.get_id())
        self.assertFalse(item.placeholder)

    def test_init_placeholder(self):
        item = dut.TraceableItem(self.identification, placeholder=True)
        self.assertEqual(self.identification, item.get_id())
        self.assertTrue(item.placeholder)

    def test_add_get_relation_explicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no relations (explicit+implicit)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(relations))
        # Add an explicit relation
        item.add_relation(self.fwd_relation, self.identification_tgt)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        # Add the same explicit relation, should not change (no duplicates)
        # TODO: assert error to be logged
        item.add_relation(self.fwd_relation, self.identification_tgt)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        # Add the same implicit relation, should not change (is already explicit)
        # TODO: assert warning to be logged
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)

    def test_add_get_relation_implicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no relations (explicit+implicit)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(relations))
        # Add an implicit relation
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(relations))
        # Add the same implicit relation, should not change (no duplicates)
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(relations))
        # Add the same explicit relation, should move the relation to be explicit
        item.add_relation(self.fwd_relation, self.identification_tgt)
        relations = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)
        relations = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(relations))
        relations = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(relations))
        self.assertEqual(relations[0], self.identification_tgt)



