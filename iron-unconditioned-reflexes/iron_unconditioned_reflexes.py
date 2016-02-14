import wpf

from System import TimeSpan
from System.Windows import Application, Window, Point
from System.Windows.Threading import DispatcherTimer
from System.Windows.Media import ScaleTransform

from time import time

import World
from animal_window import AnimalWindow
from renderer import Renderer


class MyWindow(Window):
    def __init__(self):        
        self.mouse_drag = False
        self.animal_window = None
        self.selected_animal = None
        self.mouse_start_point = Point(0, 0)
        self.start_time = time()

        self.world = World.World(500, 200)

        self.window = wpf.LoadComponent(self, 'iron_unconditioned_reflexes.xaml')
        self._create_and_start_timer()

        self._renderer = Renderer(self.canvas, self.world)

        self.world.food_timer = self.food_slider.Value

        self._renderer.draw_food_smell = self.food_smell_checkBox.IsChecked
        self._renderer.draw_eat_distance = self.eat_distance_checkBox.IsChecked
        self._renderer.draw_chunks = self.chunks_checkBox.IsChecked
        self._renderer.draw_animal_smell = self.animal_smell_checkBox.IsChecked

    def _create_and_start_timer(self):
        self.timer = DispatcherTimer()
        self.timer.Tick += self.dispatcherTimer_Tick
        self.timer.Interval = TimeSpan(0, 0, 0, 0, self.timer_slider.Value)
        self.timer.Start()
        
    def dispatcherTimer_Tick(self, sender, e):
        # if self.world.time == 150000:
        #     self.world.restart()
        #     self._renderer.restart()

        if (self.world.time % 10 == 0):
            performance = (time() - self.start_time) / 10.0
            self.label1.Text = "performance={}".format(performance)
            self.start_time = time()

        self.label.Text = "world time={} w={} h={}".format(self.world.time, self.world.width, self.world.height)
        self.label4.Text = "animal count={}\nfood count={}".format(len(self.world.animals), len(self.world.food))        
        self.world.update()
        self._renderer.render()
        if self.animal_window:
            self.animal_window.draw_animal_brain()

    def timer_slider_ValueChanged(self, sender, e):        
        self.timer.Interval = TimeSpan(0, 0, 0, 0, sender.Value)
    
    def scale_slider_ValueChanged(self, sender, e):
        # todo fix this crutch
        if hasattr(self,'canvas'):
            self.canvas.RenderTransform = ScaleTransform(sender.Value, sender.Value)
        
    def canvas_SizeChanged(self, sender, e):
        self.world.width = int(sender.ActualWidth)
        self.world.height= int(sender.ActualHeight)
        
    def canvas_MouseRightButtonDown(self, sender, e):
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


if __name__ == '__main__':
    Application().Run(MyWindow())