__author__ = 'daniel'
import paho.mqtt.client as mqtt
import networkx as nx
import logging
import json

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, name):
        self.name = name
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.last_msg = None
        self.last_command = None
        self.pos = (0, 0)
        self.graph = nx.Graph()
        self.closed_list = []
        self.open_list = []

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("botgrid/" + self.name + "/state")
        logger.debug("Connected to mqtt broker, subscribed to {}".format("botgrid/init"))

    def connect(self, server_ip):
        self.client.connect(server_ip)
        self.client.publish("botgrid/init", self.name)
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        logger.debug("Received [{topic}]: {msg}".format(topic=msg.topic, msg=msg.payload))
        current_msg = json.loads(bytes.decode(msg.payload))
        if not self.last_msg:
            # Initialize
            self.init_search()
        elif self.last_msg["step"] == current_msg["step"]:
            # no news
            self.last_msg = current_msg
        else:
            # We have tried to move
            assert (self.last_msg["step"] == current_msg["step"] - 1)
            current_x = current_msg["position"]["x"]
            current_y = current_msg["position"]["y"]

            last_x = self.last_msg["position"]["x"]
            last_y = self.last_msg["position"]["y"]

            if current_x != last_x \
                    or current_y != last_y:
                # we moved!
                self.graph.add_edge((last_x, last_y),
                                    (current_x, current_y))

                self.open_list.remove((current_x, current_y))
                neighbor_list = [pos for pos in
                                 self.get_neighbor_list((current_x, current_y))
                                 if pos not in self.closed_list]

                neighbor_list.remove((last_x, last_y))
                self.open_list.append(neighbor_list)
            else:
                # we didn't move
                blocked = None
                if self.last_command == "n":
                    blocked = (current_x + 1, current_y)
                elif self.last_command == "e":
                    blocked = (current_x, current_y + 1)
                elif self.last_command == "s":
                    blocked = (current_x - 1, current_y)
                elif self.last_command == "w":
                    blocked = (current_x, current_y - 1)
                logger.debug("Pos. {} is blocked".format(blocked))
                self.closed_list.append(blocked)
                self.open_list.remove(blocked)



    @staticmethod
    def get_neighbor_list(pos):
        return [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]


    def init_search(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s:: %(message)s')
    bot = Bot('the_bot')
    bot.connect("localhost")
    bot.play_game()
