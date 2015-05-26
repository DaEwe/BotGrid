__author__ = 'daniel'

from numpy import zeros
from numpy.random import random_integers as rand
from random import randint, random


class Grid:
    """Class to represent the playing field"""

    def __init__(self, grid_size, complexity=0.75, density=0.75):
        self.grid_size = grid_size
        # Only odd shapes
        shape = ((grid_size // 2) * 2 + 1, (grid_size // 2) * 2 + 1)
        # Adjust complexity and density relative to maze size
        complexity = int(complexity * (5 * (shape[0] + shape[1])))
        density = int(density * (shape[0] // 2 * shape[1] // 2))
        # Build actual maze
        self.grid = zeros(shape, dtype=bool)
        # Fill borders
        self.grid[0, :] = self.grid[-1, :] = 1
        self.grid[:, 0] = self.grid[:, -1] = 1
        # Make aisles
        for i in range(density):
            x, y = rand(0, shape[1] // 2) * 2, rand(0, shape[0] // 2) * 2
            self.grid[y, x] = 1
            for j in range(complexity):
                neighbours = []
                if x > 1:             neighbours.append((y, x - 2))
                if x < shape[1] - 2:  neighbours.append((y, x + 2))
                if y > 1:             neighbours.append((y - 2, x))
                if y < shape[0] - 2:  neighbours.append((y + 2, x))
                if len(neighbours):
                    y_, x_ = neighbours[rand(0, len(neighbours) - 1)]
                    if self.grid[y_, x_] == 0:
                        self.grid[y_, x_] = 1
                        self.grid[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                        x, y = x_, y_
        self.start_pos = self.get_random_free_field()
        self.goal_pos = self.get_random_free_field(self.start_pos, self.grid_size//2)




    def is_free_field(self, x, y):
        if x > self.grid_size or y > self.grid_size or x < 0 or y < 0:
            raise IndexError('Grid size is {gs}x{gs}'.format(gs=self.grid_size))
        return self.grid[x, y] == 0

    def get_random_free_field(self, other_pos=None, dist=0):

        if not other_pos:
            x = randint(0, self.grid_size)
            y = randint(0, self.grid_size)
            while not self.is_free_field(x, y):
                x = randint(0, self.grid_size)
                y = randint(0, self.grid_size)
        else:
            sign_x = self.get_random_sign()
            sign_y = self.get_random_sign()
            range_x = [other_pos[0] + dist*sign_x, other_pos[0] + (dist-dist//10)*sign_x]
            range_y = [other_pos[1] + dist*sign_y, other_pos[1] + (dist-dist//10)*sign_y]
            range_x.sort()
            range_y.sort()
            x = randint(range_x[0], range_x[1]) % self.grid_size
            y = randint(range_y[0], range_y[1]) % self.grid_size
            while not self.is_free_field(x, y):
                x = randint(range_x[0], range_x[1]) % self.grid_size
                y = randint(range_y[0], range_y[1]) % self.grid_size
        return x, y

    def get_random_sign(self):
        if random() < 0.5:
            return -1
        else:
            return 1

    def __str__(self):
        grid_string = ""
        for i in range((self.grid_size // 2) * 2 + 1):
            for j in range((self.grid_size // 2) * 2 + 1):
                if self.grid[i, j] == 1:
                    grid_string += "#"
                elif (i, j) == self.start_pos:
                    grid_string += "S"
                elif (i, j) == self.goal_pos:
                    grid_string += "G"
                else:
                    grid_string += " "
            grid_string += "\n"
        return grid_string