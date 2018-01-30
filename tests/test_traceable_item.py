from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableItem(TestCase):
    docname = 'folder/doc.rst'
    identification = 'some-random$name\'with<\"weird@symbols'
    fwd_relation = 'some-random-forward-relation'
    rev_relation = 'some-random-reverse-relation'
    identification_tgt = 'another-item-to-target'

    def test_init(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        item.self_test()
        self.assertEqual(self.identification, item.get_id())
        self.assertFalse(item.is_placeholder())
        self.assertIsNotNone(item.get_document())
        self.assertEqual(0, item.get_line_number())
        self.assertIsNone(item.get_node())
        self.assertIsNone(item.get_caption())
        self.assertIsNone(item.get_content())

    def test_init_placeholder(self):
        item = dut.TraceableItem(self.identification, placeholder=True)
        item.set_document(self.docname)
        with self.assertRaises(dut.TraceabilityException) as err:
            item.self_test()
        self.assertEqual(err.exception.get_document(), self.docname)
        self.assertEqual(self.identification, item.get_id())
        self.assertTrue(item.is_placeholder())

    def test_set_document(self):
        item = dut.TraceableItem(self.identification)
        with self.assertRaises(dut.TraceabilityException):
            item.self_test()
        item.set_document('some-file.rst', 888)
        self.assertEqual('some-file.rst', item.get_document())
        self.assertEqual(888, item.get_line_number())
        item.self_test()

    def test_bind_node(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        node = object()
        item.bind_node(node)
        self.assertEqual(node, item.get_node())
        item.self_test()

    def test_set_caption(self):
        txt = 'some short description'
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        item.set_caption(txt)
        self.assertEqual(txt, item.get_caption())
        item.self_test()

    def test_set_content(self):
        txt = 'some description, with\n newlines and other stuff'
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        item.set_content(txt)
        self.assertEqual(txt, item.get_content())
        item.self_test()

    def test_add_target_explicit_self(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        with self.assertRaises(dut.TraceabilityException):
            item.add_target(self.fwd_relation, self.identification, implicit=False)

    def test_add_target_implicit_self(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        with self.assertRaises(dut.TraceabilityException):
            item.add_target(self.fwd_relation, self.identification, implicit=True)

    def test_add_get_target_explicit(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
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
        with self.assertRaises(dut.TraceabilityException):
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
        with self.assertRaises(dut.TraceabilityException):
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
        item.self_test()

    def test_add_get_target_implicit(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
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
        item.self_test()

    def test_remove_target_explicit(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
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
        item.self_test()

    def test_remove_target_implicit(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
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
        item.self_test()

    def test_stringify(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        item.add_target(self.fwd_relation, self.identification_tgt, implicit=False)
        item.add_target(self.rev_relation, 'one more item', implicit=True)
        itemstr = str(item)
        self.assertIn(self.identification, itemstr)
        self.assertIn(self.fwd_relation, itemstr)
        self.assertIn(self.identification_tgt, itemstr)
        self.assertIn(self.rev_relation, itemstr)
        self.assertIn('one more item', itemstr)

    def test_match(self):
        item = dut.TraceableItem(self.identification)
        self.assertEqual(self.identification, item.get_id())
        self.assertFalse(item.is_match('some-name-that(will-definitely)not-match'))
        self.assertTrue(item.is_match('some'))
        self.assertTrue(item.is_match('some-random'))
        self.assertTrue(item.is_match('\w+'))
        self.assertTrue(item.is_match('[\w-]+andom'))

    def test_related(self):
        item = dut.TraceableItem(self.identification)
        self.assertEqual(self.identification, item.get_id())
        self.assertFalse(item.is_related([self.fwd_relation], self.identification_tgt))
        item.add_target(self.fwd_relation, self.identification_tgt)
        self.assertTrue(item.is_related([self.fwd_relation], self.identification_tgt))
        self.assertFalse(item.is_related(['some-other-relation'], self.identification_tgt))

    def test_self_test(self):
        item = dut.TraceableItem(self.identification)
        item.set_document(self.docname)
        # Add a target
        item.add_target(self.fwd_relation, self.identification_tgt)
        # Self test should pass
        item.self_test()
        # Add same target (fails as it is not allowed)
        with self.assertRaises(dut.TraceabilityException):
            item.add_target(self.fwd_relation, self.identification_tgt)
        # Hack into class and add same relation anyway
        item.explicit_relations[self.fwd_relation].append(self.identification_tgt)
        # Self test should fail
        with self.assertRaises(dut.TraceabilityException):
            item.self_test()
