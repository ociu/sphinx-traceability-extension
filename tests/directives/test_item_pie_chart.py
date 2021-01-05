from unittest import TestCase

from mlx.directives.item_pie_chart_directive import ItemPieChart


class TestItemPieChart(TestCase):
    def setUp(self):
        self.dut = ItemPieChart()
        self.all_labels = ['uncovered', 'covered']

    def test_build_pie_chart_all_labels(self):
        explode = self.dut._get_explode_values(self.all_labels, self.all_labels)
        self.assertEqual(explode, [0.05, 0])

    def test_build_pie_chart_all_covered(self):
        explode = self.dut._get_explode_values(self.all_labels[1:], self.all_labels)
        self.assertEqual(explode, [0])

    def test_build_pie_chart_all_uncovered(self):
        explode = self.dut._get_explode_values(self.all_labels[:1], self.all_labels)
        self.assertEqual(explode, [0.05])
