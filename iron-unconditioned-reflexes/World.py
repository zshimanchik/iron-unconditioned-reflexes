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
    def __init__(self, width, height, constants, thread_count=3):
        self.thread_count = thread_count
        self.constants = constants
        self._calculate_chunks_sizes()

        self.width = width
        self.height = height

        self.restart()
        self._food_timer = self.constants.DEFAULT_TIMER

        self.queue = Queue()
        self._init_workers()

    def _calculate_chunks_sizes(self):
        self.food_chunk_size = self.constants.EATING_DISTANCE + self.constants.ANIMAL_SIZE
        self.female_chunk_size = self.constants.SEX_DISTANCE + self.constants.ANIMAL_SIZE * 2

        food_max_smell_size = self.constants.APPEAR_FOOD_SIZE_MAX * self.constants.FOOD_SMELL_SIZE_RATIO
        animal_max_smell_size = self.constants.MAX_ANIMAL_SMELL_SIZE
        self.smell_chunk_size = max(food_max_smell_size, animal_max_smell_size)

    def _init_workers(self):
        self.workers = []
        for _ in range(self.thread_count):
            t = Thread(target=self._animal_worker, args=[self.queue])
            t.daemon = True
            t.start()
            self.workers.append(t)

    def restart(self):
        self.animals = [Animal(self) for _ in range(35)]
        self.animals_to_add = []
        self.dead_animals = []
        self.empty_food = []
        self.food = [self._make_random_food() for _ in range(80)]
        self.time = 0

    def _make_random_food(self):
        return Food(
                self,
                randint(0, self.width),
                randint(0, self.height),
                randint(self.constants.APPEAR_FOOD_SIZE_MIN, self.constants.APPEAR_FOOD_SIZE_MAX)
        )

    @property
    def food_timer(self):
        return int(self._food_timer * (200 * 500) / (self.width * self.height))

    @food_timer.setter
    def food_timer(self, value):
        self._food_timer = int(value * (self.width * self.height) / (200 * 500))

    def update(self):
        self.time += 1
        self._prepare_empty_chunks()
        self._split_food_to_chunks()
        self._split_animals_to_chunks()

        for animal in self.animals:
            self.queue.put(animal)
        self.queue.join()

        self.animals.extend(self.animals_to_add)
        self.animals_to_add = []
        self._remove_dead_animals()
        self._clear_empty_food()

        self._add_food_if_necessary()

    def _prepare_empty_chunks(self):
        self.food_chunks = self._make_empty_chunks(self.food_chunk_size)
        self.female_chunks = self._make_empty_chunks(self.female_chunk_size)
        self.smell_chunks = self._make_empty_chunks(self.smell_chunk_size)

    def _split_food_to_chunks(self):
        for food in self.food:
            self._check_in_bounds(food)
            # food chunks
            chunk_row, chunk_col = self.get_chunk_index(food.x, food.y, self.food_chunk_size)
            self.food_chunks[chunk_row][chunk_col].append(food)
            # smell chunks
            chunk_row, chunk_col = self.get_chunk_index(food.x, food.y, self.smell_chunk_size)
            self.smell_chunks[chunk_row][chunk_col].append(food)

    def _split_animals_to_chunks(self):
        for animal in self.animals:
            self._check_in_bounds(animal)
            # female chunks
            if animal.gender == Gender.FEMALE:
                chunk_row, chunk_col = self.get_chunk_index(animal.x, animal.y, self.female_chunk_size)
                self.female_chunks[chunk_row][chunk_col].append(animal)
            # smell chunks
            chunk_row, chunk_col = self.get_chunk_index(animal.x, animal.y, self.smell_chunk_size)
            self.smell_chunks[chunk_row][chunk_col].append(animal)

    def _add_food_if_necessary(self):
        if self.time % self._food_timer == 0:
            for _ in range(self.constants.APPEAR_FOOD_COUNT):
                self.food.append(self._make_random_food())

    def _animal_worker(self, queue):
        while True:
            animal = queue.get()
            self._update_animal(animal)
            queue.task_done()

    def _update_animal(self, animal):
        animal.sensor_values = self._get_sensors_values(animal)
        food = self.get_closest_food(animal.x, animal.y, self.constants.EATING_DISTANCE + animal.size)
        if food:
            animal.eat(food)
        animal.close_females = [female for female in self._adjacent_females(animal.x, animal.y) if close_enough(animal, female, self.constants.SEX_DISTANCE)]
        animal.update()

    def _get_sensors_values(self, animal):
        sensor_values = []
        for pos in animal.sensors_positions:
            sensor_values.extend(self.get_sensor_value(pos))
        return sensor_values

    def get_sensor_value(self, pos):
        res = [0] * self.constants.ANIMAL_SENSOR_DIMENSION
        for smeller in self._adjacent_smells(*pos):
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
        for food in self._adjacent_food(x, y):
            dist = distance(x,y, food.x, food.y)
            if dist <= food.size+max_distance and dist < min_dist:
                min_dist = dist
                res = food
        return res

    def _check_in_bounds(self, animal):
        if animal.x > self.width:
            animal.x = self.width
        if animal.x < 0:
            animal.x = 0

        if animal.y > self.height:
            animal.y = self.height
        if animal.y < 0:
            animal.y = 0

    def _adjacent_elements(self, chunks, chunk_size, x, y):
        for chunk_row, chunk_col in self._adjacent_chunks(chunks, *self.get_chunk_index(x, y, chunk_size)):
            chunk = chunks[chunk_row][chunk_col]
            for element in chunk:
                yield element

    def _adjacent_food(self, x, y):
        return self._adjacent_elements(self.food_chunks, self.food_chunk_size, x, y)

    def _adjacent_females(self, x, y):
        return self._adjacent_elements(self.female_chunks, self.female_chunk_size, x, y)

    def _adjacent_smells(self, x, y):
        return self._adjacent_elements(self.smell_chunks, self.smell_chunk_size, x, y)

    def _adjacent_chunks(self, chunks, row, col):
         r, c = row - 1, col -1
         for i in range(9):
             ri = r + i/3
             ci = c + i%3
             if 0 <= ri < len(chunks) and 0 <= ci < len(chunks[0]):
                yield (r + i/3, c + i%3)

    def get_chunk_index(self, x, y, chunk_size):
        return (int(y / chunk_size), int(x / chunk_size))

    def _remove_dead_animals(self):
        self.dead_animals = []
        for animal in self.animals[:]:
            if animal.energy <= 0:
                self.animals.remove(animal)
                self.dead_animals.append(animal)

    def _clear_empty_food(self):
        self.empty_food = []
        for food in self.food[:]:
            if food.size <= 0:
                self.food.remove(food)
                self.empty_food.append(food)

    def add_animal(self, animal):
        self.animals_to_add.append(animal)

    def get_animal(self, x, y):
        closest_animal = None
        closest_dist = self.constants.ANIMAL_SIZE + 10
        for animal in self.animals:
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
