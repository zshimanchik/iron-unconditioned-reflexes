from __future__ import division
import math
from random import random, randint
from threading import Lock

from NeuralNetwork.NeuralNetwork import NeuralNetwork
import World

TWO_PI = math.pi * 2


class Food(object):
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self._size = size
        self._smell = (0, 1, 0,)
        self._smell_size = self._size * World.World.FOOD_SMELL_SIZE_RATIO
        # self.lock = Lock()

    def beating(self, value):
        # self.lock.acquire()
        real_value = min(self.size, value)
        self.size -= real_value
        # self.lock.release()
        return value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = max(0, value)
        self._smell_size = self._size * World.World.FOOD_SMELL_SIZE_RATIO

    @property
    def smell_size(self):
        return self._smell_size

    @property
    def smell(self):
        return self._smell


class Gender:
    FEMALE = 0
    MALE = 1


class Animal(object):
    MAX_ENERGY = 30
    ENERGY_FOR_EXIST = 0.007
    MOVE_ENERGY_RATIO = 0.01

    # neural_network shape
    SENSOR_COUNT = 7
    SENSOR_DIMENSION = 3  # how many values in one sensor
    INPUT_LAYER_SIZE = SENSOR_COUNT * SENSOR_DIMENSION
    MIDDLE_LAYER_SIZE = 2
    OUTPUT_LAYER_SIZE = 3

    # DNA
    DNA_BASE = 4  # must be less or equals than 10, but greater than 1
    DNA_BRAIN_VALUE_LEN = 5
    DNA_MAX_VALUE = DNA_BASE ** DNA_BRAIN_VALUE_LEN
    DNA_HALF_MAX_VALUE = int(DNA_MAX_VALUE / 2)
    DNA_FOR_BRAIN_LEN = (MIDDLE_LAYER_SIZE * (INPUT_LAYER_SIZE + 1) + OUTPUT_LAYER_SIZE * (MIDDLE_LAYER_SIZE + 1)) * DNA_BRAIN_VALUE_LEN
    DNA_LEN = 1 + DNA_FOR_BRAIN_LEN

    READINESS_TO_SEX_THRESHOLD = 30
    READINESS_TO_SEX_INCREMENT = 0.2
    ENERGY_FULLNESS_TO_INCREASE_READINESS_TO_SEX = 0.7
    ENERGY_FOR_BUD = 5
    MIN_CHILD_COUNT = 1
    MAX_CHILD_COUNT = 3

    MUTATE_CHANCE = 0.05

    SIZE = 10
    MAX_SMELL_SIZE = 50

    def __init__(self, world, dna=""):
        self.world = world
        self._dna = dna
        self._x = randint(0, self.world.width)
        self._y = randint(0, self.world.height)
        self.size = Animal.SIZE
        self.angle = 0
        self._smell = (0.0, 0.0, 1.0, )
        self.smell_size = 0

        self.sensor_values = []
        self._sensors_positions = []
        self._sensors_positions_calculated = False

        self.energy = self.ENERGY_FOR_BUD
        self.readiness_to_sex = 0
        self.close_females = []
        self.lock = Lock()
        self.answer = []

        if not self._dna:
            self._dna = "".join([ str(randint(0, Animal.DNA_BASE-1)) for _ in range(Animal.DNA_LEN) ])
            print(self._dna)

        self.gender = int(self._dna[0], base=4) % 2
        self.brain = Animal.create_brain(self._dna[1:])
        
    @property
    def sensors_positions(self):
        if not self._sensors_positions_calculated:
            self._calculate_sensor_positions()
            self._sensors_positions_calculated = True
        return self._sensors_positions

    def _calculate_sensor_positions(self):
        self._sensors_positions = []
        angle_between_sensors = TWO_PI / self.SENSOR_COUNT
        sensor_angle = self.angle
        for i in range(self.SENSOR_COUNT):
            x = math.cos(sensor_angle) * self.size + self._x
            y = math.sin(sensor_angle) * self.size + self._y
            self._sensors_positions.append((x, y))
            sensor_angle += angle_between_sensors

    def update(self):
        self.answer = self.brain.calculate(self.sensor_values)

        self.energy -= Animal.ENERGY_FOR_EXIST

        if self.energy_fullness > Animal.ENERGY_FULLNESS_TO_INCREASE_READINESS_TO_SEX:
            self.readiness_to_sex += Animal.READINESS_TO_SEX_INCREMENT

        if self.can_request_for_sex():
            self._search_partner_and_try_to_sex()

        self.smell_size = (max(-1, self.answer[2]) + 1) / 2.0 * Animal.MAX_SMELL_SIZE
        self.move(self.answer[0], self.answer[1])

    def can_request_for_sex(self):
        return self.gender == Gender.MALE and self.is_ready_do_sex()

    def is_ready_do_sex(self):
        return self.readiness_to_sex >= Animal.READINESS_TO_SEX_THRESHOLD

    def _search_partner_and_try_to_sex(self):
        for female in self.close_females:
            success = self._thread_safe_request_for_sex(female)
            if success:
                break

    def _thread_safe_request_for_sex(self, female):
        with female.lock:
            success = female.be_requested_for_sex(self)
        return success

    def be_requested_for_sex(self, male):
        if self.is_ready_do_sex():
            self.sex(male)
            return True
        return False

    def sex(mother, father):
        child_count = randint(Animal.MIN_CHILD_COUNT, Animal.MAX_CHILD_COUNT)
        # if it tries to birth more child than it can - bud so many as it can and die.
        if not mother.can_make_n_children(child_count):
            child_count = int(mother.energy / Animal.ENERGY_FOR_BUD)
            mother.energy = 0
        if not father.can_make_n_children(child_count):
            child_count = int(father.energy / Animal.ENERGY_FOR_BUD)
            father.energy = 0

        print("{}\n{}\n{}".format("="*10, mother.dna, father.dna))
        for _ in range(child_count):
            mother.make_child(father)

        mother.readiness_to_sex = 0
        father.readiness_to_sex = 0

    def can_make_n_children(self, child_count):
        return child_count*Animal.ENERGY_FOR_BUD <= self.energy

    def make_child(mother, father):
        mother.energy -= Animal.ENERGY_FOR_BUD
        father.energy -= Animal.ENERGY_FOR_BUD
        child = Animal(mother.world, Animal.mix_dna(mother.dna, father.dna))
        print(child.dna)
        child.x = mother.x + randint(-30, 30)
        child.y = mother.y + randint(-30, 30)
        mother.world.add_animal(child)

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
    def smell(self):
        return self._smell

    @property
    def energy_fullness(self):
        return self.energy / Animal.MAX_ENERGY

    @property
    def dna(self):
        return self._dna

    @staticmethod
    def create_brain(dna):
        def dna_iter(dna):
            for i in range(0, len(dna), Animal.DNA_BRAIN_VALUE_LEN):
                cur = dna[i:i+Animal.DNA_BRAIN_VALUE_LEN]
                yield (int(cur, Animal.DNA_BASE) - Animal.DNA_HALF_MAX_VALUE) / Animal.DNA_HALF_MAX_VALUE

        dna = dna_iter(dna)
        brain = NeuralNetwork([Animal.INPUT_LAYER_SIZE, Animal.MIDDLE_LAYER_SIZE, Animal.OUTPUT_LAYER_SIZE])
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

    @staticmethod
    def mix_dna(dna1, dna2):
        m = randint(0, len(dna1))
        if randint(0, 1):
            return Animal.mutate_dna(dna1[:m] + dna2[m:])
        else:
            return Animal.mutate_dna(dna2[:m] + dna1[m:])
