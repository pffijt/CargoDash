import canopen
import logging
import yaml
import random
from time import sleep

'''
    We are not going to use this for the project but can be
    used for testing purposes.
'''

INTERFACE = 'canopen_vcan'
# INTERFACE = 'canopen_slcan'


class ServoSlaveNode:
    def __init__(self):
        with open('../config.yaml', 'r') as ymlfile:
            self.config = yaml.safe_load(ymlfile)
        # local node
        self.connectToNetwork(canopen.Network())
        self.network.create_node(5, '../eds_files/steering_node.eds')
        while True:
            sleep(1)
            self.network.sync.transmit()

    def connectToNetwork(self, network):
        self.network = network
        try:
            bustype = self.config[INTERFACE]['bustype']
            channel = self.config[INTERFACE]['channel']
            bitrate = self.config[INTERFACE]['bitrate']
            network.connect(bustype=bustype, channel=channel, bitrate=bitrate)
        except OSError:
            logging.error('CanOpenListener is unable to listen to network,'
                          ' please check if configuration is set properly!'
                          f'(bustype = {bustype}, channel = {channel},'
                          f' bitrate = {bitrate})')


ServoSlaveNode()