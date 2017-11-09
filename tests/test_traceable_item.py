from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableItem(TestCase):
    identification = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        item = dut.TraceableItem(self.identification)
        self.assertEqual(self.identification, item.get_id())

    def test_add_get_relation_explicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no relations (explicit+implicit)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(out))
        # Add an explicit relation
        item.add_relation(self.fwd_relation, self.identification_tgt)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        # Add the same explicit relation, should not change (no duplicates)
        # TODO: assert error to be logged
        item.add_relation(self.fwd_relation, self.identification_tgt)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        # Add the same implicit relation, should not change (is already explicit)
        # TODO: assert warning to be logged
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)

    def test_add_get_relation_implicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no relations (explicit+implicit)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(out))
        # Add an implicit relation
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(out))
        # Add the same implicit relation, should not change (no duplicates)
        item.add_relation(self.fwd_relation, self.identification_tgt, implicit=True)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(out))
        # Add the same explicit relation, should move the relation to be explicit
        item.add_relation(self.fwd_relation, self.identification_tgt)
        out = item.get_relations(self.fwd_relation)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)
        out = item.get_relations(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(out))
        out = item.get_relations(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(out))
        self.assertEqual(out[0], self.identification_tgt)



