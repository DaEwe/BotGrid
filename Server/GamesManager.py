__author__ = 'daniel'

# noinspection PyUnresolvedReferences
from multiprocessing import Process

from Server.BotGridServer import BotGridServer
from Server.BotGridServer import BotCommand
import paho.mqtt.client as mqtt
import time
import json
import logging
import datetime

logger = logging.getLogger(__name__)


def play_game(client_name):
    game = Game(client_name)
    game.run()


class Game:
    def __init__(self, client_name):
        logger.debug("Creating new Game for %s", client_name)
        self.game_logger = logging.getLogger(client_name)
        self.game_logger.setLevel(logging.INFO)
        self.fh = logging.FileHandler("botgrid_game_" + client_name + str(datetime.datetime.now()) + ".log")
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.game_logger.addHandler(self.fh)
        self.client_name = client_name
        self.bgs = BotGridServer(30)
        self.start_time = time.time()
        self.game_logger.info("Game started.")
        self.game_logger.info("Grid:\n" + str(self.bgs.grid))


    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("botgrid/" + self.client_name + "/command")
        logger.debug("Connected. Subscribed to topic {}".format("botgrid/" + self.client_name + "/command"))

    def on_message(self, client, userdate, msg):
        logger.debug("Received message '{msg}' on topic '{topic}'".format(msg=msg.payload, topic=msg.topic))
        command = bytes.decode(msg.payload)
        self.game_logger.info("Game started.")
        if command == 'n':
            self.bgs.set_command(BotCommand.North)
        elif command == 'e':
            self.bgs.set_command(BotCommand.East)
        elif command == 's':
            self.bgs.set_command(BotCommand.South)
        elif command == 'w':
            self.bgs.set_command(BotCommand.West)
        elif command == 'r':
            self.bgs.reset()
        else:
            logger.debug("Received illegal command '{}' on topic '{}'".format(command, msg.topic))
        self.game_logger.info(
            "Command '{command}' results in {status}".format(command=command, status=self.bgs.get_state()))

    def run(self):
        logger.debug("Game for {client} starts".format(client=self.client_name))
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("localhost")
        logger.debug("Game connected to mqtt broker.")
        client.loop_start()
        while (time.time() - self.start_time) < 120:
            json_msg = json.dumps(self.bgs.get_state());
            client.publish("botgrid/" + self.client_name + "/state", json_msg)
            logger.debug("Published message '{msg}' on topic '{topic}'"
                         .format(msg=json_msg, topic="botgrid/" + self.client_name + "/state"))
            time.sleep(0.1)
        client.loop_stop()
        client.disconnect()
        self.game_logger.info(self.bgs.get_report())
        self.fh.close()


class GamesManager:
    MAX_GAMES = 20

    def __init__(self):
        self.games = {}

    def run(self):
        logger.debug("GamesManager started up")
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("localhost")
        client.loop_start()
        while True:
            time.sleep(0.1)
            # check and remove all dead processes from game dict
            self.games = {k: v for k, v in self.games.items() if v.is_alive()}
        client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("botgrid/init")
        logger.debug("Connected to mqtt broker, subscribed to {}".format("botgrid/init"))

    def on_message(self, client, userdata, msg):
        logger.debug(
            "Received message '{msg}' on topic '{topic}' of type '{type}'".format(msg=msg.payload, topic=msg.topic,
                                                                                  type=type(msg.payload)))
        client_name = bytes.decode(msg.payload)
        if len(self.games) < GamesManager.MAX_GAMES:
            if msg.payload not in self.games:
                p = Process(target=play_game, args=(client_name,))
                p.start()
                self.games[msg.payload] = p
                logger.debug("Started new Game Process for {}".format(client_name))
            else:
                logger.debug("client name {client} already playing. Ignoring request.".format(client=client_name))
        else:
            logger.debug("Too many parallel games. Ignoring request from {client}".format(client=client_name))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s:: %(message)s')
    gm = GamesManager()
    logger.debug("Starting GamesManager.")
    gm.run()