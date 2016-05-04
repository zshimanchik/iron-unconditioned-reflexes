import wpf

from System import TimeSpan
from System.Windows import Application, Window, Point
from System.Windows.Threading import DispatcherTimer
from System.Windows.Media import ScaleTransform

from time import time

import world
from animal_window import AnimalWindow
from renderer import Renderer
from world_constants import WorldConstants
from simulation_scenario import SimulationScenario


class MyWindow(Window):
    def __init__(self):        
        self.mouse_drag = False
        self.animal_window = None
        self.selected_animal = None
        self.mouse_start_point = Point(0, 0)
        self.start_time = time()
        self.performance = 0

        world_constants = WorldConstants()
        self.world = world.World(world_constants.WORLD_WIDTH, world_constants.WORLD_HEIGHT, constants=world_constants)

        self.window = wpf.LoadComponent(self, 'iron_unconditioned_reflexes.xaml')
        self._create_and_start_timer()

        self._renderer = Renderer(self.canvas, self.world)

        self.world.food_timer = self.food_slider.Value

        self._renderer.draw_food_smell = self.food_smell_checkBox.IsChecked
        self._renderer.draw_eat_distance = self.eat_distance_checkBox.IsChecked
        self._renderer.draw_chunks = self.chunks_checkBox.IsChecked
        self._renderer.draw_animal_smell = self.animal_smell_checkBox.IsChecked
        self._renderer.draw_mammoth_smell = self.mammoth_smell_checkBox.IsChecked
        self._renderer.draw_mammoth_death_distance = self.mammoth_death_distance_checkBox.IsChecked

        self._simulation_scenario = SimulationScenario(self)
        self.Width = self.world.width + self.log_textbox.Width + self.config_panel.Width + 16
        self.Height = self.world.height + 59

    def _create_and_start_timer(self):
        self.timer = DispatcherTimer()
        self.timer.Tick += self.dispatcherTimer_Tick
        self.timer.Interval = TimeSpan(0, 0, 0, 0, 1)
        self.timer.Start()
        
    def dispatcherTimer_Tick(self, sender, e):
        self._simulation_scenario.tic()
        self._check_performance()
        self._show_world_info_in_ui()

        self.world.update()
        self._renderer.render()
        if self.animal_window:
            self.animal_window.update()

    def _check_performance(self):
        if self.world.time % 10 == 0:
            self.performance = (time() - self.start_time) / 10.0
            self.performance_textblock.Text = "performance={}".format(self.performance)
            self.start_time = time()

    def _show_world_info_in_ui(self):
        self.world_time_textblock.Text = "world time={}".format(self.world.time)
        self.animal_count_textblock.Text = "animal count={}".format(len(self.world.animals))
        self.food_count_textblock.Text = "food count={} mammoth={}".format(len(self.world.food), len(self.world.mammoths))

    def scale_slider_ValueChanged(self, sender, e):
        # todo fix this crutch
        if hasattr(self,'canvas'):
            self.canvas.RenderTransform = ScaleTransform(sender.Value, sender.Value)
        
    def canvas_SizeChanged(self, sender, e):
        self.world.width = int(sender.ActualWidth)
        self.world.height = int(sender.ActualHeight)
        self.log_textbox.Text += "\nworld width={} height={}".format(self.world.width, self.world.height)
        
    def canvas_MouseRightButtonDown(self, sender, e):
        point = e.GetPosition(self.canvas)
        self.selected_animal = self.world.add_mammoth(point.X, point.Y)
        self.mouse_drag = True   
        self.mouse_start_point = e.GetPosition(self.canvas)
    
    def canvas_MouseRightButtonUp(self, sender, e):
        self.mouse_drag = False

    def canvas_MouseLeave(self, sender, e):
        self.mouse_drag = False

    def canvas_MouseMove(self, sender, e):
        if self.mouse_drag:
            point = e.GetPosition(self.canvas)
            left = self.parent_canvas.GetLeft(self.canvas)
            top = self.parent_canvas.GetTop(self.canvas)
            if float.IsNaN(left):
                left = 0
            if float.IsNaN(top):
                top = 0
            self.parent_canvas.SetLeft(self.canvas, left + point.X - self.mouse_start_point.X)
            self.parent_canvas.SetTop(self.canvas, top + point.Y - self.mouse_start_point.Y)
    
    def canvas_MouseWheel(self, sender, e):        
        self.scale_slider.Value += (e.Delta/120)*0.05
    
    def food_slider_ValueChanged(self, sender, e):
        self.world.food_timer = int(sender.Value)

    def food_smell_changed(self, sender, e):
        self._renderer.draw_food_smell = self.food_smell_checkBox.IsChecked

    def eat_distance_changed(self, sender, e):
        self._renderer.draw_eat_distance = self.eat_distance_checkBox.IsChecked

    def chunks_changed(self, sender, e):
        self._renderer.draw_chunks = self.chunks_checkBox.IsChecked

    def animal_smell_changed(self, sender, e):
        self._renderer.draw_animal_smell = self.animal_smell_checkBox.IsChecked

    def mammoth_smell_changed(self, sender, e):
        self._renderer.draw_mammoth_smell = self.mammoth_smell_checkBox.IsChecked

    def mammoth_death_distance_changed(self, sender, e):
        self._renderer.draw_mammoth_death_distance = self.mammoth_death_distance_checkBox.IsChecked

    def MenuItem_Click(self, sender, e):
        if self.animal_window is None or not self.animal_window.IsLoaded:
            self.animal_window = AnimalWindow()            
            self.animal_window.animal = self.selected_animal
            self.animal_window.Show()
    
    def canvas_MouseLeftButtonDown(self, sender, e):
        point = e.GetPosition(self.canvas)
        self.selected_animal = self.world.get_animal(point.X, point.Y)
        self._renderer.selected_animal = self.selected_animal
        if self.animal_window:
            self.animal_window.animal = self.selected_animal
    
    def log_textbox_TextChanged(self, sender, e):
        sender.ScrollToEnd()
    
    def FreezeItem_Click(self, sender, e):
        if self.timer.IsEnabled:
            self.timer.Stop()
        else:
            self.timer.Start()


if __name__ == '__main__':
    Application().Run(MyWindow())