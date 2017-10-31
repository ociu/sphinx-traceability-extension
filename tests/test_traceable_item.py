from unittest import TestCase

import mlx.traceable_item as dut


class TestTraceableItem(TestCase):
    name = 'some-random$name\'with<\"weird@symbols'

    def test_init(self):
        item = dut.TraceableItem(self.name)
        self.assertEqual(self.name, item.get_id())

    def test_init_lib(self):
        lib = dut.TraceableItemCollection()
        item = dut.TraceableItem(self.name, lib)
        self.assertEqual(self.name, item.get_id())
        print(lib)
        self.assertEqual(self.name, lib[self.name].get_id())

