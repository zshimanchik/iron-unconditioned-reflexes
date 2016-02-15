
class WorldConstants(object):

    EATING_DISTANCE = 20
    EATING_VALUE = 0.03
    FOOD_SMELL_SIZE_RATIO = 13.0

    DEFAULT_TIMER = 60

    APPEAR_FOOD_COUNT = 3
    APPEAR_FOOD_SIZE_MIN = 6
    APPEAR_FOOD_SIZE_MAX = 10

    SEX_DISTANCE = 20

    # Animal

    ANIMAL_MAX_ENERGY = 30
    ENERGY_FOR_EXIST = 0.007
    MOVE_DISTANCE_TO_CONSUMED_ENERGY_RATIO = 0.01

    # neural_network shape
    ANIMAL_SENSOR_COUNT = 7
    ANIMAL_SENSOR_DIMENSION = 3  # how many values in one sensor

    MIDDLE_LAYER_SIZE = 2
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
    MAX_ANIMAL_SMELL_SIZE = 50

    def __init__(self):
        pass

    @property
    def INPUT_LAYER_SIZE(self):
        return self.ANIMAL_SENSOR_COUNT * self.ANIMAL_SENSOR_DIMENSION

    @property
    def DNA_MAX_VALUE(self):
        return self.DNA_BASE ** self.DNA_BRAIN_VALUE_LEN

    @property
    def DNA_HALF_MAX_VALUE(self):
        return int(self.DNA_MAX_VALUE / 2)

    @property
    def DNA_FOR_BRAIN_LEN(self):
        return (self.MIDDLE_LAYER_SIZE * (self.INPUT_LAYER_SIZE + 1) + self.OUTPUT_LAYER_SIZE * (self.MIDDLE_LAYER_SIZE + 1)) * self.DNA_BRAIN_VALUE_LEN

    @property
    def DNA_LEN(self):
        return 1 + self.DNA_FOR_BRAIN_LEN
