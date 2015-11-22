from math import sqrt
from threading import Thread
from Queue import Queue

from random import randint, random
from Animal import Animal, Food


def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)

class World(object):
    THREADS_COUNT = 3

    MAX_ANIMAL_COUNT = 100
    MAX_EATING_DISTANCE = 20
    EATING_VALUE = 0.03
    SMELL_SIZE_RATIO = 13.0

    APPEAR_FOOD_COUNT = 3
    APPEAR_FOOD_SIZE_MIN = 6
    APPEAR_FOOD_SIZE_MAX = 10
    
    CHUNK_SIZE = max(APPEAR_FOOD_SIZE_MAX*SMELL_SIZE_RATIO + Animal.SIZE, MAX_EATING_DISTANCE)
    
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.restart()
        self.food_timer = 80

        self.queue = Queue()
        self.threads = []
        for _ in range(World.THREADS_COUNT):
            t = Thread(target=self.animal_worker, args=[self.queue])
            t.daemon = True
            t.start()
            self.threads.append(t)
 

    def restart(self):
        self.animals = [Animal(self) for _ in range(20)]
        self.animals_to_add = []
        self.food = [Food(randint(3, self.width), randint(3, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)) for _ in range(80)]
        self.chunks = [[[]]]
        self.time = 0

    def update(self):
        self.time += 1
        self.chunks = [
            [[] for _ in range(int(self.width/self.CHUNK_SIZE)+1)] 
            for _ in range(int(self.height/self.CHUNK_SIZE)+1) 
        ]

        for food in self.food:
            self.check_in_bounds(food)
            food.chunk = self.get_chunk_index(food.x, food.y)
            self.chunks[food.chunk[0]][food.chunk[1]].append(food)

        for animal in self.animals:
            self.queue.put(animal)
        self.queue.join()

        self.animals.extend(self.animals_to_add)
        self.animals_to_add = []
        self.transform_dead_animals()
        self.clear_empty_food()

        # add some food some fixed time
        if self.time % self.food_timer == 0:
            for _ in range(World.APPEAR_FOOD_COUNT):
                self.food.append(Food(randint(0, self.width), randint(0, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)))
                
    
    def animal_worker(self, queue):
        while True:
            animal = queue.get()
            self.check_in_bounds(animal)

            sensor_values = map(self.get_sensor_value, animal.sensors_positions)
            animal.sensor_values = sensor_values
            food = self.get_closest_food(animal.x, animal.y, World.MAX_EATING_DISTANCE + animal.size)
            if food:
                animal.eat(food)
            animal.update()
            queue.task_done()

    def get_sensor_value(self, pos):
        max_smell = 0
        for food in self.adjacent_food(*pos):
            if food.smell_size > 0:
                try:
                    max_smell = max(max_smell, 1.0 - distance(food.x, food.y, pos[0], pos[1]) / food.smell_size)
                except ZeroDivisionError:
                    pass
        return max_smell

    def get_closest_food(self, x, y, max_distance):
        min_dist = 10000
        res = None
        for food in self.adjacent_food(x, y):
            dist = distance(x,y, food.x, food.y)
            if dist <= food.size+max_distance and dist < min_dist:
                min_dist = dist
                res = food
        return res

    def check_in_bounds(self, animal):
        if animal.x > self.width:
            animal.x = self.width
        if animal.x < 0:
            animal.x = 0

        if animal.y > self.height:
            animal.y = self.height
        if animal.y < 0:
            animal.y = 0

    def adjacent_chunks(self, row, col):
         r, c = row - 1, col -1
         for i in range(9):
             ri = r + i/3
             ci = c + i%3
             if ri >= 0 and ci >= 0 and ri < len(self.chunks) and ci < len(self.chunks[0]):
                yield (r + i/3, c + i%3)

    def get_chunk_index(self, x, y):
        return (int(y/self.CHUNK_SIZE), int(x/self.CHUNK_SIZE))

    def adjacent_food(self, x, y):
        for chunk_row, chunk_col in self.adjacent_chunks(*self.get_chunk_index(x, y)):
            chunk = self.chunks[chunk_row][chunk_col]
            for food in chunk:
                yield food

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