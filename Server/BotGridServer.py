import logging
from enum import Enum
from Server.Grid import Grid


__author__ = 'Daniel Ewert'

logger = logging.getLogger(__name__)


class BotCommand(Enum):
    North = 1
    East = 2
    South = 3
    West = 4
    Nothing = 5


class BotGridServer:
    """Frontend for the Server, interface to game clients"""

    def __init__(self, grid_size):
        self.grid = Grid(grid_size)
        logger.debug("Created grid of size{}".format(grid_size))
        self.start_pos = self.grid.start_pos
        self.goal_pos = self.grid.goal_pos
        logger.debug("grid has startpos {start} and goalpos {goal}".format(start=self.start_pos, goal=self.goal_pos))
        self.bot_pos = self.start_pos
        self.steps = 0
        self.num_runs = 0
        self.report = ""

    def reset(self):
        self.report += "Run: {run}, steps_taken {steps}," \
                       " goal reached {goal_reached}\n".format(run=self.num_runs, steps=self.steps,
                                                               goal_reached=self.goal_pos == self.bot_pos)
        self.bot_pos = self.start_pos
        self.steps = 0
        self.num_runs += 1

    def set_command(self, command):
        self.steps += 1
        delta = (0, 0)
        if command == BotCommand.North:
            delta = (1, 0)
        elif command == BotCommand.East:
            delta = (0, 1)
        elif command == BotCommand.South:
            delta = (-1, 0)
        elif command == BotCommand.West:
            delta = (0, -1)
        new_pos = tuple(map(lambda x, y: x + y, self.bot_pos, delta))  # probably inefficient
        if self.grid.is_free_field(new_pos[0], new_pos[1]):
            self.bot_pos = new_pos

    def get_state(self):
        odom_pos = tuple(map(lambda x, y: x - y, self.bot_pos, self.start_pos))  # probably inefficient
        return {"step": self.steps, "position": {"x": odom_pos[0], "y": odom_pos[1]},
                "is_goal": self.bot_pos == self.goal_pos}

    def get_report(self):
        return self.report





