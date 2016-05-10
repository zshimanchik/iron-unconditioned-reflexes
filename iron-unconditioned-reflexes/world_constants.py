
class WorldConstants(object):
    WORLD_WIDTH = 900
    WORLD_HEIGHT = 200

    EATING_DISTANCE = 20
    EATING_VALUE = 0.03
    FOOD_SMELL_SIZE_RATIO = 7.0

    DEFAULT_TIMER = 60 * (500 * 200) / (WORLD_WIDTH * WORLD_HEIGHT)

    APPEAR_FOOD_COUNT = 3
    APPEAR_FOOD_SIZE_MIN = 6
    APPEAR_FOOD_SIZE_MAX = 10

    MAMMOTH_COUNT = 5
    MAMMOTH_SMELL_SIZE_RATIO = 5.0
    MAMMOTH_BEAT_VALUE = 0.007
    MAMMOTH_REGENERATION_VALUE = 0.01
    FOOD_FROM_MAMMOTH_COUNT = 5

    SEX_DISTANCE = 20

    # Animal

    ANIMAL_MAX_ENERGY = 30
    ENERGY_FOR_EXIST = 0.007
    MOVE_DISTANCE_TO_CONSUMED_ENERGY_RATIO = 0.01

    # neural_network shape
    ANIMAL_SENSOR_COUNT = 7
    ANIMAL_SENSOR_DIMENSION = 3  # how many values in one sensor

    MIDDLE_LAYERS_SIZES = [3, 3]
    OUTPUT_LAYER_SIZE = 3

    # DNA
    DNA_BASE = 4  # must be less or equals than 10, but greater than 1
    DNA_BRAIN_VALUE_LEN = 5

    READINESS_TO_SEX_THRESHOLD = 30
    READINESS_TO_SEX_INCREMENT = 0.2
    ENERGY_FULLNESS_TO_INCREASE_READINESS_TO_SEX = 0.7
    ENERGY_FOR_BIRTH = 5
    MIN_AMOUNT_OF_CHILDREN = 1
    MAX_AMOUNT_OF_CHILDREN = 3

    MUTATE_CHANCE = 0.05

    ANIMAL_SIZE = 10
    MAX_ANIMAL_SMELL_SIZE = 100

    def __init__(self):
        pass

    # todo create cached properties instead of this for optimization

    @property
    def INPUT_LAYER_SIZE(self):
        return self.ANIMAL_SENSOR_COUNT * self.ANIMAL_SENSOR_DIMENSION

    @property
    def NEURAL_NETWORK_SHAPE(self):
        return [self.INPUT_LAYER_SIZE] + self.MIDDLE_LAYERS_SIZES + [self.OUTPUT_LAYER_SIZE]

    @property
    def DNA_MAX_VALUE(self):
        return self.DNA_BASE ** self.DNA_BRAIN_VALUE_LEN

    @property
    def DNA_HALF_MAX_VALUE(self):
        return int(self.DNA_MAX_VALUE / 2)

    @property
    def DNA_FOR_BRAIN_LEN(self):
        shape = self.NEURAL_NETWORK_SHAPE
        connection_count = sum([ shape[i] * (shape[i+1] + 1) for i in range(len(shape)-1)])
        return connection_count * self.DNA_BRAIN_VALUE_LEN

    @property
    def DNA_LEN(self):
        return 1 + self.DNA_FOR_BRAIN_LEN
