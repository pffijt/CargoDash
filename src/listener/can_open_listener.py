import canopen
import logging
import asyncio
import time
import can

from listener.listener import Listener
from numpy import array, append
from canopen.sdo.exceptions import SdoCommunicationError


class CanOpenListener(Listener):
    ''' This class is being used to listen on a network and mainly
        tries to push the changes around other nodes to it's interpreter.
    '''
    def __init__(self, config, config_type='canopen_vcan', interpreter=None):
        ''' config : yaml_file_stream
                The configured yaml file that contains details for the
                connection type.

            config_type: string
                The selected configuration that is going to be used.
                The configurations are defined in 'config.yaml'.

            interpreter : CanOpenInterpreter
                The wanted interpreter that is going to be used.
        '''

        super().__init__(config)
        self.observers = array([])
        self.nodes = array([])
        self.config_type = config_type
        self.network = self.connect_to_network()
        self._add_nodes(self.config[self.config_type]['nodes'])
        self.interpreter = interpreter

    def connect_to_network(self):
        ''' Connects to a can network.
            This method is depending on config.yaml, please
            configure the yaml file correctly before using this method.

            Returns canopen.Network.
        '''

        network = canopen.Network()
        try:
            bustype = self.config[self.config_type]['bustype']
            channel = self.config[self.config_type]['channel']
            bitrate = self.config[self.config_type]['bitrate']
            network.connect(bustype=bustype, channel=channel, bitrate=bitrate)
        except OSError:
            logging.error('CanOpenListener is unable to listen to network,'
                          ' please check if configuration is set properly!'
                          f'(bustype = {bustype}, channel = {channel},'
                          f' bitrate = {bitrate})')
        return network

    def listen_to_network(self, nodes):
        ''' Listens to connected network and tries to find any value changes
            within any connected node.
            The network sends out SDOs to be able to notice the value changes.

            Returns void.
        '''

        # Listens to every node
        for node_id in nodes:
            # Within a node find the variables saved
            for sdo_object in self.network[node_id].sdo.values():
                # And then get each variable's index and read it
                sdo_index = sdo_object.od.index
                try:
                    # Check for indices between 0x2000 and 0x5FFF
                    # Because we except communication between those
                    if (sdo_index >= 0x2000 and sdo_index <= 0x5FFF):
                        if (type(sdo_object) == canopen.sdo.base.Array
                           or type(sdo_object) == canopen.sdo.base.Record):
                            self._read_complex_variable(
                                self.network[node_id].sdo, sdo_index, node_id)
                        elif (type(sdo_object) == canopen.sdo.base.Variable):
                            self._read_simple_variable(
                                self.network[node_id].sdo, sdo_index, node_id)
                except SdoCommunicationError:
                    logging.error(f'The requested sdo ({hex(sdo_index)})'
                                  ' is not received!')

    async def async_network_loop(self):
        ''' Function to loop the through all nodes asynchronously.
            Loops forever.
        '''
        try:
            self.network.scanner.search()
            time.sleep(0.05)
            if(len(self.network.scanner.nodes) > 0):
                while True:
                    self.listen_to_network(self.network.scanner.nodes)
                    # Sleeps 0.1 seconds
                    await asyncio.sleep(0.1)
            else:
                logging.error('No nodes to listen to!')
        except can.CanError as exc:
            if ('[Errno 100] Network is down' in repr(exc)):
                logging.error('CAN network is down!')
            else:
                raise exc
        except KeyboardInterrupt:
            pass

    def _read_complex_variable(self, sdo_client, sdo_index, node_id):
        for subindex in range(len(sdo_client[sdo_index]) + 1):
            # Skips subindex 0 because there are no value changes around this
            if(subindex != 0):
                index_and_subindex = f'{sdo_index}sub{subindex}'
                sdo_value = sdo_client.upload(sdo_index, subindex)
                sdo_data_type = hex(
                    sdo_client[sdo_index][subindex].od.data_type)
                # Checks for every subindex if value changed
                if(self._sdo_value_changed(index_and_subindex, node_id,
                                           sdo_value)):
                    self.inform_interpreter(
                        sdo_value, sdo_client[sdo_index][subindex].od.name,
                        sdo_data_type, node_id, hex(sdo_index), hex(subindex))

    def _read_simple_variable(self, sdo_client, sdo_index, node_id):
        sdo_value = sdo_client.upload(sdo_index, 0)
        sdo_data_type = hex(sdo_client[sdo_index].od.data_type)
        if(self._sdo_value_changed(sdo_index, node_id, sdo_value)):
            self.inform_interpreter(sdo_value, sdo_client[sdo_index].od.name,
                                    sdo_data_type, node_id, hex(sdo_index),
                                    hex(0))

    def _add_nodes(self, nodes):
        for i in range(len(nodes)):
            self.nodes = append(
                self.nodes, nodes[i]['node_properties'])
            # Either adds local or remote node bases on config for each node
            if(nodes[i]['local']):
                # Create a local node
                self.network.create_node(nodes[i]['node_properties']['id'],
                                         nodes[i]['eds_location'])
            else:
                # Add a remote node
                self.network.add_node(nodes[i]['node_properties']['id'],
                                      nodes[i]['eds_location'])

    def inform_interpreter(self, sdo_value, sdo_name, sdo_data_type, node_id,
                           index, sub_index):
        ''' Informs the interpreter with a changed SDO.

            sdo_value : any
                Sends out the changed value.

            sdo_name : canopen.sdo.Variable
                Sends out the changed SDO name.

            sdo_data_type : str
                Sends the data_type as string representing a
                hexadecimal value.

            node_id : integer
                Used to read node purpose.

            index : string
                Index of the variable.

            sub_index : string
                Sub-index of the variable.

            Returns void.
        '''
        # Iterates through self.nodes to find correct node with id.
        node = [x for x in self.nodes if x['id'] == node_id][0]
        self.interpreter.inform_interpreter(sdo_value, sdo_name,
                                            sdo_data_type, node, index,
                                            sub_index)

    def set_interpreter(self, interpreter):
        ''' Set the interpreter where CanOpenListener can send messages to.

            interpreter : CanOpenInterpreter
                The wanted interpreter that is going to be used.

            Returns void.
        '''

        self.interpreter = interpreter

    def _sdo_value_changed(self, sdo_index, node_id, sdo_value):
        # Couldn't find a possibility to subscribe to a value with the CANopen
        # library, so needed to make an implementation by myself.

        found = False
        changed = False
        for observer in self.observers:
            if(observer['index'] == sdo_index and
               observer['node_id'] == node_id):
                found = True
                if(observer['value'] != sdo_value):
                    observer['value'] = sdo_value
                    changed = True
        if(not found):
            self.observers = append(
                self.observers, {'index': sdo_index, 'node_id': node_id,
                                 'value': sdo_value})
            changed = True
        return changed
