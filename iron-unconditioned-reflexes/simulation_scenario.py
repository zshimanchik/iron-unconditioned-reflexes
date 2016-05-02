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
        self._how_fast_three_animal_can_kill_mammoth = 200
        self._update_worldinfo_textblock()
        self.last_animal_count_changed = 0
        self.last_animal_count = 0

    def _next_scenario(self):
        self.last_animal_count_changed = 0
        self._how_fast_three_animal_can_kill_mammoth -= 50
        self._world.constants.MAMMOTH_BEAT_VALUE = 1.0 / self._how_fast_three_animal_can_kill_mammoth
        self._world.constants.MAMMOTH_REGENERATION_VALUE = self._world.constants.MAMMOTH_BEAT_VALUE * 2.0

    def tic(self):
        self._restart_if_all_dead()
        self._restart_if_all_one_gender()
        self._restart_if_no_changes()
        self._restart_if_performace_is_high()
        # return  # comment it to enable
        if self._world.time == 10:
            self._render_trash(False)
        if self._world.time == 300000:
            self._render_trash(True)
        if self._world.time == 400000:
            self._next_scenario()
            self._world.restart()
            self._world_number += 1
            self._main_window._renderer.restart()
            self._update_worldinfo_textblock()

    def _restart_if_all_dead(self):
        if len(self._world.animals) <= 1:
            self._restart()

    def _restart_if_all_one_gender(self):
        if self._only_one_gender():
            self._restart()

    def _restart_if_performace_is_high(self):
        if self._main_window.performance > 4:
            self._restart()

    def _restart_if_no_changes(self):
        if len(self._world.animals) != self.last_animal_count:
            self.last_animal_count = len(self._world.animals)
            self.last_animal_count_changed = self._world.time
        else:
            if self._world.time - self.last_animal_count_changed > 10000:
                self._restart()

    def _restart(self):
        self._world.restart()
        self._world_number += 1
        self._main_window._renderer.restart()
        self._update_worldinfo_textblock()

    def _only_one_gender(self):
        gender = self._world.animals[0].gender
        for animal in self._world.animals:
            if animal.gender != gender:
                return False
        return True

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

    def _render_trash(self, render=True):
        self._main_window._renderer.draw_food_smell = render
        self._main_window._renderer.draw_animal_smell = render
        self._main_window._renderer.draw_mammoth_smell = render
        self._main_window._renderer.draw_mammoth_death_distance = render

    def _update_worldinfo_textblock(self):
        self._main_window.world_info_textblock.Text = "world number={}\nBEAT VALUE: {}\nRegen_val: {}".format(
            self._world_number,
            self._constants.MAMMOTH_BEAT_VALUE,
            self._constants.MAMMOTH_REGENERATION_VALUE,
        )
