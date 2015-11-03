from math import sqrt

from random import randint, random
from Animal import Animal, Food


def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)


class World(object):
    MAX_ANIMAL_COUNT = 100
    MAX_EATING_DISTANCE = 20
    EATING_VALUE = 0.03

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.restart()
        self.food_timer = 20

    def restart(self):
        self.animals = [Animal(self) for _ in range(10)]
        self.animals_to_add = []
        self.food = [Food(randint(3, self.width), randint(3, self.height), randint(4,10)) for _ in range(40)]

        self.time = 0

    def update(self):
        self.time += 1
        for food in self.food:
            self.check_animal_in_bounds(food)

        for animal in self.animals:
            self.check_animal_in_bounds(animal)
            sensor_values = map(self.get_sensor_value, animal.sensors_positions)

            food = self.get_closest_food(animal.x, animal.y, World.MAX_EATING_DISTANCE)
            if food:
                animal.eat(food)

            animal.update(sensor_values)


        self.animals.extend(self.animals_to_add)
        self.animals_to_add = []
        self.transform_dead_animals()
        self.clear_empty_food()

        # add some food some fixed time
        if self.time % self.food_timer == 0:
            for _ in range(3):
                self.food.append(Food(randint(0, self.width), randint(0, self.height), randint(2,6)))

    def get_sensor_value(self, pos):
        max_smell = 0
        for food in self.food:
            if food.size > 0:
                max_smell = max(max_smell, 1.0 - distance(food.x, food.y, pos[0], pos[1]) / food.smell_size)
        return max_smell

    def get_closest_food(self, x, y, max_distance):
        min_dist = 10000
        res = None
        for food in self.food:
            dist = distance(x,y, food.x, food.y)
            if dist <= food.size+max_distance and dist < min_dist:
                min_dist = dist
                res = food
        return res

    def check_animal_in_bounds(self, animal):
        if animal.x > self.width:
            animal.x = self.width
        if animal.x < 0:
            animal.x = 0

        if animal.y > self.height:
            animal.y = self.height
        if animal.y < 0:
            animal.y = 0

    def transform_dead_animals(self):
        for animal in self.animals[:]:
            if animal.energy <= 0:
                # self.food.append(Food(randint(0, self.width),randint(0, self.height), animal.size))
                self.animals.remove(animal)

    def clear_empty_food(self):
        for food in self.food[:]:
            if food.size <= 0:
                self.food.remove(food)

    def add_animal(self, animal):
        self.animals_to_add.append(animal)