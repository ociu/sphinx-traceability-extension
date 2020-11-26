from collections import namedtuple
from unittest import TestCase

from docutils import nodes
from mlx.directives.item_matrix_directive import ItemMatrix as dut

from parameterized import parameterized


class TestItemMatrix(TestCase):
    Rows = namedtuple('Rows', "sorted covered uncovered")

    @parameterized.expand([
       (True, False, [1, 1, 0]),
       (False, False, [1, 0, 1]),
       (True, True, [1, 1, 0]),
       (False, True, [0, 0, 1]),
    ])
    def test_store_row(self, covered, onlycovered, expected_lengths):
        rows = self.Rows([], [], [])
        left = nodes.entry('left')
        rights = [nodes.entry('right1'), nodes.entry('right2')]
        dut._store_row(rows, left, rights, covered, onlycovered)

        self.assertEqual([len(attr) for attr in rows], expected_lengths)
        my_row = nodes.row()
        my_row += left
        my_row += rights
        for idx, rows_per_type in enumerate(rows):  # verify that rows contain the three entries
            self.assertEqual(str(rows_per_type), str([my_row] * expected_lengths[idx]))
