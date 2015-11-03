from Layer import InputLayer, Layer, Readiness


class NeuralNetwork:
    def __init__(self, shape):
        self.layers = []
        self.shape = shape
        self.time = 0

        self.input_layer = InputLayer(shape[0])

        self.middle_layer = Layer(shape[1], self.input_layer.neurons)
        self.input_layer.listeners.append(self.middle_layer)

        self.output_layer = Layer(shape[2], self.middle_layer.neurons)
        self.middle_layer.listeners.append(self.output_layer)

        self.layers.append(self.input_layer)
        self.layers.append(self.middle_layer)
        self.layers.append(self.output_layer)

        self._reset_layers_states()

    def __len__(self):
        return len(self.shape)

    def __getitem__(self, i):
        return self.layers[i]

    def calculate(self, x):
        """
        calculate vector x, if random value is set, add to result vector value (random()*2-1)*random_value
        :param x: input vector
        :param random_value: random range added to result vector
        :return: result of network calculation
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

    def teach_by_sample(self, database, teach_value=0.5):
        err = 0
        for inp, out in database:
            net_out = self.calculate(inp)
            self.output_layer.teach_output_layer_by_sample(teach_value, out)

            # teach middle layers
            self.middle_layer.teach_middle_layer(teach_value)

            for layer in self:
                layer.commit_teach()

            err += sum([abs(no-o) for no, o in zip(net_out, out)])
        return err / len(database)
