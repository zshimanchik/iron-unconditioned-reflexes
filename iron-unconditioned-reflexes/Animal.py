from __future__ import division
import math
from random import random, randint
from threading import Lock

from NeuralNetwork.NeuralNetwork import NeuralNetwork

TWO_PI = math.pi * 2


class Food(object):
    def __init__(self, world, x, y, size):
        self._world = world
        self.x = x
        self.y = y
        self._size = size
        self._smell = (0, 1, 0,)
        self._smell_size = self._size * self._world.constants.FOOD_SMELL_SIZE_RATIO
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
        self._smell_size = self._size * self._world.constants.FOOD_SMELL_SIZE_RATIO

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
    def __init__(self, world, dna=""):
        self.world = world
        self._dna = dna
        self._x = randint(0, self.world.width)
        self._y = randint(0, self.world.height)
        self.size = self.world.constants.ANIMAL_SIZE
        self.angle = 0
        self._smell = (0.0, 0.0, 1.0, )
        self.smell_size = 0

        self.sensor_values = []
        self._sensors_positions = []
        self._sensors_positions_calculated = False

        self.energy = self.world.constants.ENERGY_FOR_BIRTH
        self.readiness_to_sex = 0
        self.close_females = []
        self.lock = Lock()
        self.answer = []

        if not self._dna:
            self._dna = "".join([ str(randint(0, self.world.constants.DNA_BASE-1)) for _ in range(self.world.constants.DNA_LEN) ])
            print(self._dna)

        self.gender = int(self._dna[0], base=4) % 2
        self.brain = Animal.create_brain(self._dna[1:], self.world.constants)
        
    @property
    def sensors_positions(self):
        if not self._sensors_positions_calculated:
            self._calculate_sensor_positions()
            self._sensors_positions_calculated = True
        return self._sensors_positions

    def _calculate_sensor_positions(self):
        self._sensors_positions = []
        angle_between_sensors = TWO_PI / self.world.constants.ANIMAL_SENSOR_COUNT
        sensor_angle = self.angle
        for i in range(self.world.constants.ANIMAL_SENSOR_COUNT):
            x = math.cos(sensor_angle) * self.size + self._x
            y = math.sin(sensor_angle) * self.size + self._y
            self._sensors_positions.append((x, y))
            sensor_angle += angle_between_sensors

    def update(self):
        self.answer = self.brain.calculate(self.sensor_values)

        self.energy -= self.world.constants.ENERGY_FOR_EXIST

        if self.energy_fullness > self.world.constants.ENERGY_FULLNESS_TO_INCREASE_READINESS_TO_SEX:
            self.readiness_to_sex += self.world.constants.READINESS_TO_SEX_INCREMENT

        if self.can_request_for_sex():
            self._search_partner_and_try_to_sex()

        self.smell_size = (max(-1, self.answer[2]) + 1) / 2.0 * self.world.constants.MAX_ANIMAL_SMELL_SIZE
        self.move(self.answer[0], self.answer[1])

    def can_request_for_sex(self):
        return self.gender == Gender.MALE and self.is_ready_do_sex()

    def is_ready_do_sex(self):
        return self.readiness_to_sex >= self.world.constants.READINESS_TO_SEX_THRESHOLD

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
        child_count = randint(mother.world.constants.MIN_AMOUNT_OF_CHILDREN, mother.world.constants.MAX_AMOUNT_OF_CHILDREN)
        # if it tries to birth more child than it can - bud so many as it can and die.
        if not mother.can_make_n_children(child_count):
            child_count = int(mother.energy / mother.world.constants.ENERGY_FOR_BIRTH)
            mother.energy = 0
        if not father.can_make_n_children(child_count):
            child_count = int(father.energy / mother.world.constants.ENERGY_FOR_BIRTH)
            father.energy = 0

        print("{}\n{}\n{}".format("="*10, mother.dna, father.dna))
        for _ in range(child_count):
            mother.make_child(father)

        mother.readiness_to_sex = 0
        father.readiness_to_sex = 0

    def can_make_n_children(self, child_count):
        return child_count * self.world.constants.ENERGY_FOR_BIRTH <= self.energy

    def make_child(mother, father):
        mother.energy -= mother.world.constants.ENERGY_FOR_BIRTH
        father.energy -= mother.world.constants.ENERGY_FOR_BIRTH
        child = Animal(mother.world, Animal.mix_dna(mother.dna, father.dna, mother.world.constants))
        print(child.dna)
        child.x = mother.x + randint(-30, 30)
        child.y = mother.y + randint(-30, 30)
        mother.world.add_animal(child)

    def eat(self, food):
        value = min(self.world.constants.EATING_VALUE, max(0, self.world.constants.ANIMAL_MAX_ENERGY - self.energy))
        value = food.beating(value)
        self.energy += value

    def move(self, move, rotate):
        self.energy -= (abs(move) + abs(rotate)) * self.world.constants.MOVE_DISTANCE_TO_CONSUMED_ENERGY_RATIO

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
        return self.energy / self.world.constants.ANIMAL_MAX_ENERGY

    @property
    def dna(self):
        return self._dna

    @staticmethod
    def create_brain(dna, world_constants):
        def dna_iter(dna):
            for i in range(0, len(dna), world_constants.DNA_BRAIN_VALUE_LEN):
                cur = dna[i:i+world_constants.DNA_BRAIN_VALUE_LEN]
                yield (int(cur, world_constants.DNA_BASE) - world_constants.DNA_HALF_MAX_VALUE) / world_constants.DNA_HALF_MAX_VALUE

        dna = dna_iter(dna)
        brain = NeuralNetwork(world_constants.NEURAL_NETWORK_SHAPE)
        for layer in brain:
            for neuron in layer:
                neuron.w = [dna.next() for _ in range(len(neuron.w))]
        return brain

    # for debug
    @staticmethod
    def brain_to_dna(brain, world_constants):
        def val_to_dna(x):
            x = max(0, int((x*world_constants.DNA_HALF_MAX_VALUE) + world_constants.DNA_HALF_MAX_VALUE))
            res = []
            while x:
                res.insert(0, str(x % world_constants.DNA_BASE))
                x /= world_constants.DNA_BASE
            return "".join(res)

        dna = []
        for layer in brain:
            for neuron in layer:
                for w in neuron.w:                
                    dna.append(val_to_dna(w))
        return "".join(dna)

    @staticmethod
    def mutate_dna(dna, world_constants):
        dna_ba = bytearray(dna)    
        for i in range(len(dna_ba)):
            if random() < world_constants.MUTATE_CHANCE:
                dna_ba[i] = ord(str(randint(0, world_constants.DNA_BASE-1)))
        return str(dna_ba)

    @staticmethod
    def mix_dna(dna1, dna2, world_constants):
        m = randint(0, len(dna1))
        if randint(0, 1):
            return Animal.mutate_dna(dna1[:m] + dna2[m:], world_constants)
        else:
            return Animal.mutate_dna(dna2[:m] + dna1[m:], world_constants)
