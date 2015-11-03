from math import sqrt
from threading import Thread

from random import randint, random
from Animal import Animal, Food


def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)


class World(object):
    MAX_ANIMAL_COUNT = 100
    MAX_EATING_DISTANCE = 20
    EATING_VALUE = 0.03
    SMELL_SIZE_RATIO = 13.0

    APPEAR_FOOD_COUNT = 3
    APPEAR_FOOD_SIZE_MIN = 6
    APPEAR_FOOD_SIZE_MAX = 10

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.restart()
        self.food_timer = 80

    def restart(self):
        self.animals = [Animal(self) for _ in range(30)]
        self.animals_to_add = []
        self.food = [Food(randint(3, self.width), randint(3, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)) for _ in range(60)]

        self.time = 0

    def update(self):
        self.time += 1

        for food in self.food:
            self.check_animal_in_bounds(food)

        threads = self.make_workers(self.animal_worker, 3, self.animals)
        for t in threads:
            t.join()        

        self.animals.extend(self.animals_to_add)
        self.animals_to_add = []
        self.transform_dead_animals()
        self.clear_empty_food()

        # add some food some fixed time
        if self.time % self.food_timer == 0:
            for _ in range(World.APPEAR_FOOD_COUNT):
                self.food.append(Food(randint(0, self.width), randint(0, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)))


    def animal_worker(self, animals, start, end):
        for i in range(start, end):
            animal = animals[i]
            self.check_animal_in_bounds(animal)

            sensor_values = map(self.get_sensor_value, animal.sensors_positions)
            animal.sensor_values = sensor_values
            food = self.get_closest_food(animal.x, animal.y, World.MAX_EATING_DISTANCE)
            if food:
                animal.eat(food)
            animals[i].update()

    def make_workers(self, worker, thread_count, animals):
        threads = []
        np  =  len(animals)/thread_count
        for i in range(thread_count):
            t =  Thread(target=worker, args=[animals, np*i, np*(i+1)])
            t.start()
            threads.append(t)
        return threads

    def get_sensor_value(self, pos):
        max_smell = 0
        for food in self.food:
            #food.lock.acquire()
            if food.smell_size > 0:
                try:
                    max_smell = max(max_smell, 1.0 - distance(food.x, food.y, pos[0], pos[1]) / food.smell_size)
                except ZeroDivisionError:
                    pass
            #food.lock.release()
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