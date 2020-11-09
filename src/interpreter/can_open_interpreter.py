from interpreter.interpreter import Interpreter
from node_input_factory.node_input_factory import NodeInputFactory
from node_input_factory.node_input_enums import NodeType


class CanOpenInterpreter(Interpreter):
    def __init__(self):
        self.node_input_factory = NodeInputFactory()
        super().__init__()

    def inform_interpreter(self, sdo_value, sdo_object, node_purpose):
        ''' This method is requested by the CanOpenListener when it notices
            changes at a certain sdo value.

            sdo_value: any
                Value to change the state of the vehicle.

            sdo_object: canopen.sdo.Variable
                The SDO with the changed value.

            node_purpose: dictionary {name: string, type: integer}
                A dictionary that contains a name/description about the node
                and the type of the node.
        '''
        self._interpret_object(sdo_value, sdo_object.od.name,
                               node_purpose['name'], node_purpose['type'])

    def _interpret_object(self, value, name, node_name, node_type):
        input_node = NodeType(node_type)
        if(NodeType.DistanceNode == input_node):
            self.node_input_factory.create_distance_node_input(value, name,
                                                               node_name)
        elif(NodeType.SteeringNode == input_node):
            self.node_input_factory.create_steering_node_input(value, name,
                                                               node_name)
        elif(NodeType.CoordinationNode == input_node):
            self.node_input_factory.create_coordination_node_input(value,
                                                                   name,
                                                                   node_name)
        elif(NodeType.EngineNode == input_node):
            self.node_input_factory.create_engine_node_input(value, name,
                                                             node_name)
        elif(NodeType.TemperatureNode == input_node):
            self.node_input_factory.create_temperature_node_input(value, name,
                                                                  node_name)
