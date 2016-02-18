from random import randint, choice

class SimulationScenario:
    """
    this class is not fixed. It's ugly! This code doesn't respect any "good ways of coding" or something like that.
    I use it to create scenario for simulations, when I'm not near or sleeping,
    usually I record this simulations on video for further analyzing
    """
    def __init__(self, main_window):
        self._main_window = main_window
        self._world = self._main_window.world
        self._constants = self._world.constants
        self._world_number = 0
        self._update_worldinfo_textblock()

    def tic(self):
        return  # comment it to enable
        if self._world.time == 100:
            self._popup_animal_window()
            self._select_random_animal()
        if self._world.time == 200:
            self._close_animal_window()
        if self._world.time == 150000:
            self._world.constants.MIDDLE_LAYERS_SIZES = [randint(2,3) for _ in range(randint(1,3))]
            self._world.restart()
            self._world_number += 1
            self._main_window._renderer.restart()
            self._update_worldinfo_textblock()

    def _popup_animal_window(self):
        self._main_window.MenuItem_Click(None, None)
        self._main_window.animal_window.Width = self._main_window.ActualWidth
        self._main_window.animal_window.Height = self._main_window.ActualHeight
        self._main_window.animal_window.Left = self._main_window.Left
        self._main_window.animal_window.Top = self._main_window.Top

    def _close_animal_window(self):
        self._main_window.animal_window.Close()

    def _select_random_animal(self):
        animal = choice(self._world.animals)
        self._main_window.selected_animal = animal
        self._main_window._renderer.selected_animal = animal
        if self._main_window.animal_window:
            self._main_window.animal_window.animal = animal

    def _update_worldinfo_textblock(self):
        self._main_window.world_info_textblock.Text = "world number={}\nneural network: {}".format(
            self._world_number,
            "-".join(map(str, self._constants.NEURAL_NETWORK_SHAPE))
        )
