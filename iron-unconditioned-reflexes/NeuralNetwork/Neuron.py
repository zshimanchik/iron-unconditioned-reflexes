from random import random
import math


def sigmoid(x):
    return 1/(1 + math.exp(-x))

def th(x):
    return (math.exp(x) - math.exp(-x)) / (math.exp(x) + math.exp(-x))


class _AbstractNeuron():
    def __init__(self):
        self.out = 0
        self.w = []
        self.dw = []

    def calculate(self, x):
        return self.out

    def commit_teach(self):
        pass


class Neuron(_AbstractNeuron):
    def __init__(self, synapse_count):
        _AbstractNeuron.__init__(self)
        self.w = [random() * 0.3 - 0.15 for _ in range(synapse_count)]
        self.dw = [0] * synapse_count

    def add_synapse(self, count):
        self.w = self.w + [random() * 0.3 - 0.15 for _ in range(count)]
        self.dw = self.dw + [0]*count
        
    def calculate(self, inp):
        net = sum((x * w for x, w in zip(inp, self.w)))
        self.out = th(net)
        return self.out

    def commit_teach(self):
        for i in range(len(self.w)):
            self.w[i] += self.dw[i]
        

class InputNeuron(_AbstractNeuron):
    def __init__(self):
        _AbstractNeuron.__init__(self)

    def calculate(self, x):
        self.out = x
        return self.out


class RandomNeuron(_AbstractNeuron):
    def __init__(self, random_value):
        _AbstractNeuron.__init__(self)
        self.random_value = random_value

    def calculate(self, x):
        self.out = x + (random() - (1 - self.out) / 2) * self.random_value
        return self.out


class BiasNeuron(_AbstractNeuron):
    def __init__(self):
        _AbstractNeuron.__init__(self)
        self.out = 1
