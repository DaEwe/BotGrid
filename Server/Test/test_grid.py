from unittest import TestCase
from Server.Grid import Grid
__author__ = 'daniel'


class TestGrid(TestCase):

    def test_get_random_free_field(self):
        grid = Grid(20)
        for i in range(20):
            start = grid.get_random_free_field()
            goal = grid.get_random_free_field(start, 10)
            self.assertGreaterEqual(abs(start[0]-goal[0]), 8)
            self.assertGreaterEqual(abs(start[0]-goal[0]), 8)
            print(start, goal)
