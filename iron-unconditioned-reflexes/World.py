from Queue import Queue
from math import sqrt
from random import randint
from threading import Thread

from Animal import Animal, Food, Gender


def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)


def close_enough(animal1, animal2, max_distance):
    return distance(animal1.x, animal1.y, animal2.x, animal2.y) < max_distance + animal1.size + animal2.size


class World(object):
    THREADS_COUNT = 3

    MAX_ANIMAL_COUNT = 100

    EATING_DISTANCE = 20
    EATING_VALUE = 0.03
    FOOD_SMELL_SIZE_RATIO = 13.0

    APPEAR_FOOD_COUNT = 3
    APPEAR_FOOD_SIZE_MIN = 6
    APPEAR_FOOD_SIZE_MAX = 10

    SEX_DISTANCE = 20

    FOOD_CHUNK_SIZE = EATING_DISTANCE + Animal.SIZE
    FEMALE_CHUNK_SIZE = SEX_DISTANCE + Animal.SIZE * 2

    FOOD_MAX_SMELL = APPEAR_FOOD_SIZE_MAX * FOOD_SMELL_SIZE_RATIO
    ANIMAL_MAX_SMELL = Animal.MAX_SMELL_SIZE
    SMELL_CHUNK_SIZE = max(FOOD_MAX_SMELL, ANIMAL_MAX_SMELL)

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.restart()
        self._food_timer = 80

        self.queue = Queue()
        self.threads = []
        for _ in range(World.THREADS_COUNT):
            t = Thread(target=self.animal_worker, args=[self.queue])
            t.daemon = True
            t.start()
            self.threads.append(t)

    @property
    def food_timer(self):
        return int(self._food_timer * (200 * 500) / (self.width * self.height))

    @food_timer.setter
    def food_timer(self, value):
        self._food_timer = int(value * (self.width * self.height) / (200 * 500))


    def restart(self):
        self.animals = [Animal(self) for _ in range(35)]
        self.animals_to_add = []
        self.food = [Food(randint(3, self.width), randint(3, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)) for _ in range(80)]
        self.time = 0

    def update(self):
        self.time += 1
        self.food_chunks = self._make_empty_chunks(self.FOOD_CHUNK_SIZE)
        self.female_chunks = self._make_empty_chunks(self.FEMALE_CHUNK_SIZE)
        self.smell_chunks = self._make_empty_chunks(self.SMELL_CHUNK_SIZE)

        for food in self.food:
            self.check_in_bounds(food)
            # food chunks
            chunk_row, chunk_col = self.get_chunk_index(food.x, food.y, self.FOOD_CHUNK_SIZE)
            self.food_chunks[chunk_row][chunk_col].append(food)
            # smell chunks
            chunk_row, chunk_col = self.get_chunk_index(food.x, food.y, self.SMELL_CHUNK_SIZE)
            self.smell_chunks[chunk_row][chunk_col].append(food)

        for animal in self.animals:
            self.check_in_bounds(animal)
            # female chunks
            if animal.gender == Gender.FEMALE:
                chunk_row, chunk_col = self.get_chunk_index(animal.x, animal.y, self.FEMALE_CHUNK_SIZE)
                self.female_chunks[chunk_row][chunk_col].append(animal)
            # smell chunks
            chunk_row, chunk_col = self.get_chunk_index(animal.x, animal.y, self.SMELL_CHUNK_SIZE)
            self.smell_chunks[chunk_row][chunk_col].append(animal)

        for animal in self.animals:
            self.queue.put(animal)
        self.queue.join()

        self.animals.extend(self.animals_to_add)
        self.animals_to_add = []
        self._remove_dead_animals()
        self._clear_empty_food()

        # add some food some fixed time
        if self.time % self._food_timer == 0:
            for _ in range(World.APPEAR_FOOD_COUNT):
                self.food.append(Food(randint(0, self.width), randint(0, self.height), randint(World.APPEAR_FOOD_SIZE_MIN, World.APPEAR_FOOD_SIZE_MAX)))
                
    
    def animal_worker(self, queue):
        while True:
            animal = queue.get()
            sensor_values = []
            for pos in animal.sensors_positions:
                sensor_values.extend(self.get_sensor_value(pos))
            animal.sensor_values = sensor_values
            food = self.get_closest_food(animal.x, animal.y, self.EATING_DISTANCE + animal.size)
            if food:
                animal.eat(food)
            animal.close_females = [female for female in self.adjacent_females(animal.x, animal.y) if close_enough(animal, female, self.SEX_DISTANCE)]
            animal.update()
            queue.task_done()

    def get_sensor_value(self, pos):
        res = [0] * Animal.SENSOR_DIMENSION
        for smeller in self.adjacent_smells(*pos):
            try:
                smell_strength = max(0, (1.0 - distance(smeller.x, smeller.y, pos[0], pos[1]) / smeller.smell_size)) ** 2
                for i, v in enumerate(smeller.smell):
                    val = v * smell_strength
                    if val > res[i]:
                        res[i] = val
            except ZeroDivisionError:
                pass
        return res

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

    def _adjacent_elements(self, chunks, chunk_size, x, y):
        for chunk_row, chunk_col in self.adjacent_chunks(chunks, *self.get_chunk_index(x, y, chunk_size)):
            chunk = chunks[chunk_row][chunk_col]
            for element in chunk:
                yield element

    def adjacent_food(self, x, y):
        return self._adjacent_elements(self.food_chunks, self.FOOD_CHUNK_SIZE, x, y)

    def adjacent_females(self, x, y):
        return self._adjacent_elements(self.female_chunks, self.FEMALE_CHUNK_SIZE, x, y)

    def adjacent_smells(self, x, y):
        return self._adjacent_elements(self.smell_chunks, self.SMELL_CHUNK_SIZE, x, y)

    def adjacent_chunks(self, chunks, row, col):
         r, c = row - 1, col -1
         for i in range(9):
             ri = r + i/3
             ci = c + i%3
             if 0 <= ri < len(chunks) and 0 <= ci < len(chunks[0]):
                yield (r + i/3, c + i%3)

    def get_chunk_index(self, x, y, chunk_size):
        return (int(y / chunk_size), int(x / chunk_size))

    def _remove_dead_animals(self):
        for animal in self.animals[:]:
            if animal.energy <= 0:
                # self.food.append(Food(randint(0, self.width),randint(0, self.height), animal.size))
                self.animals.remove(animal)

    def _clear_empty_food(self):
        for food in self.food[:]:
            if food.size <= 0:
                self.food.remove(food)

    def add_animal(self, animal):
        self.animals_to_add.append(animal)

    def get_animal(self, x, y):
        closest_animal = None
        closest_dist = Animal.SIZE + 10
        for animal  in self.animals:
            dist = distance(x, y, animal.x, animal.y)
            if dist < closest_dist:
                closest_animal = animal
                closest_dist = dist
        return closest_animal

    def _make_empty_chunks(self, chunk_size):
        return [
            [[] for _ in range(int(self.width / chunk_size) + 1)]
            for _ in range(int(self.height / chunk_size) + 1)
        ]
