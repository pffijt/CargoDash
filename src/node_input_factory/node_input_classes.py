from abc import ABC


class NodeInput(ABC):
    def __init__(self, value, node_var_name, node_name,
                 **additional_attributes):
        ''' NodeInput Object used to change to state of the vehicle.

            value : any
                Node value to change the state of the vehicle.

            name : string
                Name belonging to a variable within the node.

            node_name : string
                Description what the node is functioning for.

            additional_attributes
                Able to add multiple extra attibutes

        '''
        self.node_var_name = node_var_name
        self.value = value
        self.node_name = node_name
        # Sets any additional attribute to the NodeInput
        for key, value in additional_attributes.items():
            setattr(self, key, value)
        super().__init__()

    def read_node_input(self):
        ''' Returns the value of the node input object.
        '''
        return self.value

    def write_node_input(self, new_value):
        ''' Changes the value of the node input object.

            new_value : void
                The new value for the node input object.

            Returns void.
        '''
        self.value = new_value


class DistanceNodeInput(NodeInput):
    # Enum 0
    # Distance as object distance
    def __init__(self, distance: float, node_var_name: str, node_name: str,
                 **additional_attributes):
        super().__init__(distance, node_var_name, node_name,
                         **additional_attributes)


class SteeringNodeInput(NodeInput):
    # Enum 1
    def __init__(self, steering_angle: float, node_var_name: str,
                 node_name: str, **additional_attributes):
        super().__init__(steering_angle, node_var_name, node_name,
                         **additional_attributes)


class LocalizationNodeInput(NodeInput):
    # Enum 2
    def __init__(self, location: str, node_var_name: str, node_name: str,
                 **additional_attributes):
        super().__init__(location, node_var_name, node_name,
                         **additional_attributes)


class EngineNodeInput(NodeInput):
    # Enum 3
    def __init__(self, set_engine: bool, node_var_name: str, node_name: str,
                 **additional_attributes):
        super().__init__(set_engine, node_var_name, node_name,
                         **additional_attributes)


class TemperatureNodeInput(NodeInput):
    # Enum 4
    def __init__(self, temperature: float, node_var_name: str, node_name: str,
                 **additional_attributes):
        super().__init__(temperature, node_var_name, node_name,
                         **additional_attributes)
