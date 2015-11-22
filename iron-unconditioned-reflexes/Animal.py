from __future__ import division
import math
from random import random, randint
#from threading import Lock

from NeuralNetwork.NeuralNetwork import NeuralNetwork
from NeuralNetwork.Neuron import Neuron
import World

TWO_PI = math.pi * 2


class Food(object):
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self._size = size
        self._smell_size = self._size * World.World.SMELL_SIZE_RATIO
        #self.lock = Lock()

    def beating(self, value):
        #self.lock.acquire()
        real_value = min(self.size, value)
        self.size -= real_value
        #self.lock.release()
        return value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = max(0, value)
        self._smell_size = self._size * World.World.SMELL_SIZE_RATIO

    @property
    def smell_size(self):
        return self._smell_size


class Animal(object):
    MAX_ENERGY = 30
    ENERGY_FOR_EXIST = 0.007
    MOVE_ENERGY_RATIO = 0.01

    # neural_network shape
    SENSOR_COUNT = 7
    MIDDLE_LAYER_NEURONS = 2
    OUTPUT_SIZE = 2

    # DNA
    DNA_BASE = 4 # must be less or equals than 10
    DNA_VALUE_LEN = 5
    DNA_MAX_VALUE = DNA_BASE ** DNA_VALUE_LEN
    DNA_HALF_MAX_VALUE = int(DNA_MAX_VALUE / 2)
    DNA_LEN = (MIDDLE_LAYER_NEURONS*(SENSOR_COUNT + 1) + OUTPUT_SIZE*(MIDDLE_LAYER_NEURONS + 1)) * DNA_VALUE_LEN

    # sensor_count_in_head / sensor_count
    SENSOR_COUNT_IN_HEAD_RATIO = 0.5
    # head angle
    HEAD_ANGLE = math.pi / 4.0
    HALF_HEAD_ANGLE = HEAD_ANGLE / 2.0

    READINESS_TO_BUD_THREADSHOULD = 30
    READINESS_TO_BUD_INCREASEMENT = 0.2
    ENERGY_FULLNES_TO_BUD = 0.7
    ENERGY_FOR_BUD = 5
    MIN_CHILD_COUNT = 1
    MAX_CHILD_COUNT = 3

    MUTATE_CHANCE = 0.1

    SIZE = 7

    def __init__(self, world, dna=""):
        self.world = world
        self._dna = dna
        self._x = randint(0, self.world.width)
        self._y = randint(0, self.world.height)
        self.size = Animal.SIZE
        self.angle = 0

        self._sensor_count_in_head = int(self.SENSOR_COUNT * Animal.SENSOR_COUNT_IN_HEAD_RATIO)
        self._sensor_count_not_in_head = self.SENSOR_COUNT - self._sensor_count_in_head
        self.sensor_values = []
        self._sensors_positions = []
        self._sensors_positions_calculated = False

        self.energy = self.ENERGY_FOR_BUD
        self.readiness_to_bud = 0

        if not self._dna:
            self._dna = "".join([ str(randint(0,Animal.DNA_BASE-1)) for _ in range(Animal.DNA_LEN) ])
            print(self._dna)

        self.brain = Animal.create_brain(self._dna)
        
    @property
    def sensors_positions(self):
        # on 45 degrees (pi/4) of main angle located 75% of all sensors
        if not self._sensors_positions_calculated:
            self._sensors_positions = []

            # calc sensor positions in head


            delta_angle = Animal.HEAD_ANGLE / (self._sensor_count_in_head-1)
            angle = -Animal.HALF_HEAD_ANGLE + self.angle
            for _ in range(self._sensor_count_in_head):
                self._sensors_positions.append(
                    (math.cos(angle) * self.size + self._x, math.sin(angle) * self.size + self._y))
                angle += delta_angle

            # calc sensor positions in body
            delta_angle = (TWO_PI - Animal.HEAD_ANGLE) / (self._sensor_count_not_in_head+1)
            angle = Animal.HALF_HEAD_ANGLE + self.angle
            for _ in range(self._sensor_count_not_in_head):
                angle += delta_angle
                self._sensors_positions.append(
                    (math.cos(angle) * self.size + self._x, math.sin(angle) * self.size + self._y))

            self._sensors_positions_calculated = True
        return self._sensors_positions

    def update(self):
        answer = self.brain.calculate(self.sensor_values)
        self.answer = answer

        self.energy -= Animal.ENERGY_FOR_EXIST

        if self.energy / Animal.MAX_ENERGY > Animal.ENERGY_FULLNES_TO_BUD:
            self.readiness_to_bud += Animal.READINESS_TO_BUD_INCREASEMENT
        if self.readiness_to_bud >= Animal.READINESS_TO_BUD_THREADSHOULD:
            self.readiness_to_bud = 0
            self.bud()

        self.move(answer[0], answer[1])

    def bud(self):
        child_count = randint(Animal.MIN_CHILD_COUNT, Animal.MAX_CHILD_COUNT)
        # if it tries to bud more child than it can - bud so many as it can and die.
        if child_count*Animal.ENERGY_FOR_BUD > self.energy:
            child_count = int(self.energy / Animal.ENERGY_FOR_BUD)
            self.energy = 0

        print("{}\n{}".format("="*10, self._dna))
        for _ in range(child_count):
            self.energy -= Animal.ENERGY_FOR_BUD
            child = Animal(self.world, Animal.mutate_dna(self.dna))
            print(child.dna)
            child.x = self.x + randint(-30, 30)
            child.y = self.y + randint(-30, 30)
            self.world.add_animal(child)

    def eat(self, food):
        value = min(World.World.EATING_VALUE, max(0, Animal.MAX_ENERGY - self.energy))
        value = food.beating(value)
        self.energy += value

    def move(self, move, rotate):
        self.energy -= (abs(move) + abs(rotate))*Animal.MOVE_ENERGY_RATIO

        self._sensors_positions_calculated = False
        self.angle += rotate
        self._x += math.cos(self.angle) * move * 2.0
        self._y += math.sin(self.angle) * move * 2.0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._sensors_positions_calculated = False

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._sensors_positions_calculated = False

    @property
    def dna(self):
        return self._dna


    @staticmethod
    def create_brain(dna):
        def dna_iter(dna):
            for i in range(0, len(dna), Animal.DNA_VALUE_LEN):
                cur = dna[i:i+Animal.DNA_VALUE_LEN]
                yield (int(cur, Animal.DNA_BASE) - Animal.DNA_HALF_MAX_VALUE) / Animal.DNA_HALF_MAX_VALUE

        dna = dna_iter(dna)
        brain = NeuralNetwork([Animal.SENSOR_COUNT, Animal.MIDDLE_LAYER_NEURONS, Animal.OUTPUT_SIZE])
        for layer in brain:
            for neuron in layer:
                neuron.w = [dna.next() for _ in range(len(neuron.w))]
        return brain

    # for debug
    @staticmethod
    def brain_to_dna(brain):
        def val_to_dna(x):
            x = max(0, int((x*Animal.DNA_HALF_MAX_VALUE) + Animal.DNA_HALF_MAX_VALUE))
            res = []
            while x:
                res.insert(0, str(x % Animal.DNA_BASE))
                x /= Animal.DNA_BASE
            return "".join(res)

        dna = []
        for layer in brain:
            for neuron in layer:
                for w in neuron.w:                
                    dna.append(val_to_dna(w))
        return "".join(dna)

    @staticmethod
    def mutate_dna(dna):
        dna_ba = bytearray(dna)    
        for i in range(len(dna_ba)):
            if random() < Animal.MUTATE_CHANCE:
                dna_ba[i] = ord(str(randint(0, Animal.DNA_BASE-1)))
        return str(dna_ba)