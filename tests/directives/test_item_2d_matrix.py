from unittest import TestCase

from mlx.directives.item_2d_matrix_directive import Item2DMatrix as dut
from mlx.traceable_collection import TraceableCollection
from mlx.traceable_attribute import TraceableAttribute
from mlx.traceable_item import TraceableItem

from parameterized import parameterized


class TestItemMatrix(TestCase):
    def setUp(self):
        self.collection = TraceableCollection()
        for id_ in ('rAB', 'rCC', 'dBB', 'dC', 'z1'):
            self.collection.add_item(TraceableItem(id_))
        TraceableItem.define_attribute(TraceableAttribute('asil', '[ABCD]'))
        TraceableItem.define_attribute(TraceableAttribute('rating', '[ABCD]'))
        self.collection.get_item('rAB').add_attribute('asil', 'A')
        self.collection.get_item('rAB').add_attribute('rating', 'B')
        self.collection.get_item('rCC').add_attribute('asil', 'C')
        self.collection.get_item('rCC').add_attribute('rating', 'C')
        self.collection.get_item('dBB').add_attribute('asil', 'B')
        self.collection.get_item('dBB').add_attribute('rating', 'B')
        self.collection.get_item('dC').add_attribute('asil', 'C')

    @parameterized.expand([
        (r'r\w+', r'd\w+', {'asil': '[AB]'}, False, (['rAB'], ['dBB', 'dC'])),
        (r'r\w+', r'd\w+', {'asil': '[AB]'}, True, (['rAB', 'rCC'], ['dBB'])),
        ('', '', {'asil': '[AB]'}, False, (['dBB', 'rAB'], ['dBB', 'dC', 'rAB', 'rCC', 'z1'])),
        ('', '', {'asil': '[AB]'}, True, (['dBB', 'dC', 'rAB', 'rCC', 'z1'], ['dBB', 'rAB'])),
        ('', r'd\w+', {'asil': '[ABC]', 'rating': '[ACD]'}, False, (['rCC'], ['dBB', 'dC'])),
        ('', r'd\w+', {'asil': '[ABC]', 'rating': '[ACD]'}, True, (['dBB', 'dC', 'rAB', 'rCC', 'z1'], [])),
        ('', '', {'asil': '[ABC]', 'rating': '[ACD]'}, False, (['rCC'], ['dBB', 'dC', 'rAB', 'rCC', 'z1'])),
        ('', '', {'asil': '[ABC]', 'rating': '[ACD]'}, True, (['dBB', 'dC', 'rAB', 'rCC', 'z1'], ['rCC'])),
        ('', '', {}, False, (['dBB', 'dC', 'rAB', 'rCC', 'z1'], ['dBB', 'dC', 'rAB', 'rCC', 'z1'])),
        ('', '', {}, True, (['dBB', 'dC', 'rAB', 'rCC', 'z1'], ['dBB', 'dC', 'rAB', 'rCC', 'z1'])),
    ])
    def test_get_source_and_target_ids(self, source_regex, target_regex, filter_attributes, filter_target, expected):
        result = dut.get_source_and_target_ids(self.collection, source_regex, target_regex,
                                               filter_attributes, filter_target)
        self.assertEqual(result, expected)
