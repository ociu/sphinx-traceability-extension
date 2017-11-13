from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableItem(TestCase):
    identification = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        item = dut.TraceableItem(self.identification)
        self.assertTrue(item.self_test())
        self.assertEqual(self.identification, item.get_id())
        self.assertFalse(item.placeholder)
        self.assertIsNone(item.get_document())
        self.assertIsNone(item.get_line_number())
        self.assertIsNone(item.get_node())
        self.assertIsNone(item.get_caption())
        self.assertIsNone(item.get_content())

    def test_init_placeholder(self):
        item = dut.TraceableItem(self.identification, placeholder=True)
        self.assertFalse(item.self_test())
        self.assertEqual(self.identification, item.get_id())
        self.assertTrue(item.placeholder)

    def test_set_document(self):
        item = dut.TraceableItem(self.identification)
        item.set_document('some-file.rst', 888)
        self.assertEqual('some-file.rst', item.get_document())
        self.assertEqual(888, item.get_line_number())

    def test_bind_node(self):
        item = dut.TraceableItem(self.identification)
        node = object()
        item.bind_node(node)
        self.assertEqual(node, item.get_node())

    def test_set_caption(self):
        txt = 'some short description'
        item = dut.TraceableItem(self.identification)
        item.set_caption(txt)
        self.assertEqual(txt, item.get_caption())

    def test_set_content(self):
        txt = 'some description, with\n newlines and other stuff'
        item = dut.TraceableItem(self.identification)
        item.set_content(txt)
        self.assertEqual(txt, item.get_content())

    def test_add_get_target_explicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no targets (explicit+implicit)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(targets))
        relations = item.iter_relations()
        self.assertNotIn(self.fwd_relation, relations)
        # Add an explicit target
        item.add_target(self.fwd_relation, self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Add the same explicit target, should not change (no duplicates)
        # TODO: assert error to be logged
        item.add_target(self.fwd_relation, self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Add the same implicit target, should not change (is already explicit)
        # TODO: assert warning to be logged
        item.add_target(self.fwd_relation, self.identification_tgt, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Verify relations iterator
        relations = item.iter_relations()
        self.assertIn(self.fwd_relation, relations)
        # Self test should pass
        self.assertTrue(item.self_test())

    def test_add_get_target_implicit(self):
        item = dut.TraceableItem(self.identification)
        # Initially no targets (explicit+implicit)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(targets))
        relations = item.iter_relations()
        self.assertNotIn(self.fwd_relation, relations)
        # Add an implicit target
        item.add_target(self.fwd_relation, self.identification_tgt, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(targets))
        # Add the same implicit target, should not change (no duplicates)
        item.add_target(self.fwd_relation, self.identification_tgt, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(0, len(targets))
        # Add the same explicit target, should move the target to be explicit
        item.add_target(self.fwd_relation, self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation, explicit=False)
        self.assertEqual(0, len(targets))
        targets = item.iter_targets(self.fwd_relation, implicit=False)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Verify relations iterator
        relations = item.iter_relations()
        self.assertIn(self.fwd_relation, relations)
        # Self test should pass
        self.assertTrue(item.self_test())

    def test_remove_target_explicit(self):
        item = dut.TraceableItem(self.identification)
        # Add an explicit target
        item.add_target(self.fwd_relation, self.identification_tgt)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Remove target to self and implicit targets, no effect
        item.remove_targets(self.identification)
        item.remove_targets(self.identification_tgt, explicit=False, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Remove explicit target to tgt, should be removed
        item.remove_targets(self.identification_tgt, explicit=True, implicit=False)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(0, len(targets))
        # Self test should pass
        self.assertTrue(item.self_test())

    def test_remove_target_implicit(self):
        item = dut.TraceableItem(self.identification)
        # Add an implicit target
        item.add_target(self.fwd_relation, self.identification_tgt, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Remove target to self and explicit targets, no effect
        item.remove_targets(self.identification)
        item.remove_targets(self.identification_tgt, explicit=True, implicit=False)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(1, len(targets))
        self.assertEqual(targets[0], self.identification_tgt)
        # Remove implicit target to tgt, should be removed
        item.remove_targets(self.identification_tgt, explicit=False, implicit=True)
        targets = item.iter_targets(self.fwd_relation)
        self.assertEqual(0, len(targets))
        # Self test should pass
        self.assertTrue(item.self_test())
