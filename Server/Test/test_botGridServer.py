import random
from unittest import TestCase
from Server.BotGridServer import BotGridServer
from Server.BotGridServer import BotCommand

__author__ = 'daniel'


class TestBotGridServer(TestCase):

    def setUp(self):
        self.bot_grid_server = BotGridServer(100)

    def test_reset(self):
        for i in range(random.randint(5, 50)):
            self.bot_grid_server.set_command(random.choice(list(BotCommand.__members__.values())))
            print(self.bot_grid_server.bot_pos)
        self.bot_grid_server.reset()
        self.assertEqual(self.bot_grid_server.bot_pos, self.bot_grid_server.start_pos)

    def test_set_command(self):
        new_pos = self.bot_grid_server.set_command(BotCommand.North)
        print(new_pos)
        self.assertIsNotNone(new_pos)