from Layer import InputLayer, Layer, Readiness


class NeuralNetwork:
    def __init__(self, shape):
        self.layers = []
        self.shape = shape
        self.time = 0

        self.input_layer = InputLayer(shape[0])
        self.layers.append(self.input_layer)

        prev_layer = self.input_layer
        for i in range(1, len(shape)-1):
            cur_layer = Layer(shape[i], prev_layer.neurons)
            prev_layer.listeners.append(cur_layer)
            self.layers.append(cur_layer)
            prev_layer = cur_layer

        self.output_layer = Layer(shape[-1], prev_layer.neurons)
        prev_layer.listeners.append(self.output_layer)
        self.layers.append(self.output_layer)

        self._reset_layers_states()

    def __len__(self):
        return len(self.shape)

    def __getitem__(self, i):
        return self.layers[i]

    def calculate(self, x):
        """
        :param x: list of input values
        :return: list of values which is result of network calculation
        """
        self.input_layer.input_values = x
        done = False
        while not done:
            done = True
            for layer in self:
                if layer.ready_to_calculate == Readiness.READY:
                    layer.calculate()
                    done = False

        self._reset_layers_states()
        return self.output_layer.get_output_values()

    def _reset_layers_states(self):
        for layer in self:
            layer.reset_state()