import wpf

from System import TimeSpan
from System.Windows import Application, Window, Point
from System.Windows.Threading import DispatcherTimer
from System.Windows.Shapes import *
from System.Windows.Controls import Grid, Canvas
from System.Windows.Media import Brushes, ScaleTransform, TranslateTransform, RotateTransform, TransformGroup, RadialGradientBrush, Color

import math
from time import time

import World
from Animal import Gender
from animal_window import AnimalWindow


class MyWindow(Window):
    def __init__(self):        
        self.mouse_drag = False
        self.renew_food_shapes_flag = True
        self.renew_animal_shapes_flag = True
        self.world = World.World(400, 200)
        self.mouse_start_point = Point(0, 0)
        
        self.timer= DispatcherTimer()        
        self.timer.Tick += self.dispatcherTimer_Tick
        self.timer.Interval = TimeSpan(0, 0, 0, 0, 100)
        self.timer.Start()
        self.start_time = time()

        self.window = wpf.LoadComponent(self, 'iron_unconditioned_reflexes.xaml') 
        self.timer.Interval = TimeSpan(0, 0, 0, 0, self.timer_slider.Value)
        self.world.food_timer = self.food_slider.Value

        self.animal_window = None
        self.selected_animal = None
        
    def add_line(self, x1, y1, x2, y2, brush=Brushes.Gray):
        ln = Line()
        ln.X1 = x1
        ln.Y1 = y1
        ln.X2 = x2
        ln.Y2 = y2
        ln.StrokeThickness = 0.1
        ln.Stroke = brush
        self.canvas.Children.Add(ln)
        


    def make_food_shape(self):
        canvas = Canvas()

        el = Ellipse()
        el.Fill = Brushes.Gray
        el.Height=1
        el.Width=1
        el.RenderTransform = TranslateTransform(-0.5, -0.5)
        canvas.Children.Add(el)

        if self.food_smell_checkBox.IsChecked:
            smell_el = Ellipse()

            color1 = Color.FromArgb(40, 0, 220, 20)
            color2 = Color.FromArgb(0, 0, 220, 20)
            smell_el.Fill = RadialGradientBrush(color1, color2)

            smell_el.StrokeThickness = 0.03
            smell_el.Stroke = Brushes.Gray

            smell_el.Height = World.World.SMELL_SIZE_RATIO * 2
            smell_el.Width = World.World.SMELL_SIZE_RATIO * 2
            smell_el.RenderTransform = TranslateTransform(-World.World.SMELL_SIZE_RATIO, -World.World.SMELL_SIZE_RATIO)
        
            canvas.Children.Add(smell_el)
        
        canvas.SetZIndex(el, 1)
        return canvas

    def make_eat_distance_shape(self, food):
        canvas = Canvas()

        eat_el =Ellipse()
        eat_el.StrokeThickness = 0.1
        eat_el.Stroke = Brushes.Black
        size = World.World.EATING_DISTANCE + food.size
        eat_el.Height = size*2
        eat_el.Width = size*2
        eat_el.RenderTransform = TranslateTransform(-size + food.x, -size + food.y)
        canvas.Children.Add(eat_el)
        return canvas

    def make_smell_shape(self, animal):
        canvas = Canvas()
        smell_el = Ellipse()

        color1 = Color.FromArgb(40, 220, 0, 20)
        color2 = Color.FromArgb(0, 220, 0, 20)
        smell_el.Fill = RadialGradientBrush(color1, color2)

        smell_el.StrokeThickness = 0.1
        smell_el.Stroke = Brushes.Gray

        smell_el.Height = animal.smell_size * 2
        smell_el.Width = animal.smell_size * 2
        smell_el.RenderTransform = TranslateTransform(-animal.smell_size, -animal.smell_size)

        canvas.Children.Add(smell_el)
        return canvas

    def make_animal_shape(self, animal):
        canvas = Canvas()

        el = Ellipse()
        if animal == self.selected_animal:
            el.Fill = Brushes.Gold
        elif animal.gender == Gender.FEMALE:
            el.Fill = Brushes.DarkRed
        else:
            el.Fill = Brushes.Green

        el.Height=1
        el.Width=1
        el.RenderTransform = TranslateTransform(-0.5, -0.5)

        ln = Line()
        ln.X1 = 0.5
        ln.Y1 = 0.5
        ln.X2 = 1
        ln.Y2 = 0.5
        ln.StrokeThickness = 0.1
        ln.Stroke = Brushes.Black
        ln.RenderTransform = TranslateTransform(-0.5, -0.5)

        canvas.Children.Add(el)
        canvas.Children.Add(ln)
        canvas.RenderTransformOrigin = Point(0, 0)
        
        return canvas

    def dispatcherTimer_Tick(self, sender, e):
        if (self.world.time % 10 == 0):
            performance = (time() - self.start_time) / 10.0
            self.label1.Text = "performance={}".format(performance)
            self.start_time = time()

        self.label.Text = "world time={}".format(self.world.time)
        self.label4.Text = "animal count={}\nfood count={}".format(len(self.world.animals), len(self.world.food))        
        self.world.update()
        self.draw()
        if self.animal_window:
            self.animal_window.draw_animal_brain()

    def draw(self):
        self.canvas.Children.Clear()

        if self.chunks_checkBox.IsChecked:
            self.draw_grid(self.world.FEMALE_CHUNK_SIZE, Brushes.Gray)
            self.draw_grid(self.world.FOOD_SMELL_CHUNK_SIZE, Brushes.Red)

        for animal in self.world.animals:
            if self.renew_animal_shapes_flag or not hasattr(animal, 'shape'):
                animal.shape = self.make_animal_shape(animal)
                self.canvas.SetZIndex(animal.shape, 2)
            tg = TransformGroup()
            tg.Children.Add(ScaleTransform(animal.size, animal.size))
            tg.Children.Add(RotateTransform(math.degrees(animal.angle)))
            tg.Children.Add(TranslateTransform(animal.x, animal.y))
            animal.shape.RenderTransform = tg            
            self.canvas.Children.Add(animal.shape)

            if self.animal_smell_checkBox.IsChecked:
                smell_el = self.make_smell_shape(animal)
                smell_el.RenderTransform = TranslateTransform(animal.x, animal.y)
                self.canvas.Children.Add(smell_el)

        self.renew_animal_shapes_flag = False

        for food in self.world.food:
            if self.renew_food_shapes_flag or not hasattr(food, 'shape'):
                food.shape = self.make_food_shape()
                
            tg = TransformGroup()
            tg.Children.Add(ScaleTransform(food.size, food.size))
            tg.Children.Add(TranslateTransform(food.x, food.y))
            food.shape.RenderTransform = tg
            self.canvas.Children.Add(food.shape)

            if self.eat_distance_checkBox.IsChecked:
                eat_shape = self.make_eat_distance_shape(food) #xxx
                self.canvas.Children.Add(eat_shape)
                
        self.renew_food_shapes_flag = False

    def draw_grid(self, size, brush):
        for row in range(1, int(self.world.height / size)+1):
            self.add_line(0, size * row, self.world.width, size * row, brush)

        for col in range(1, int(self.world.width/ size)+1):
            self.add_line(size * col, 0, size * col, self.world.height, brush)
                    
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
    
    def renew_food_shapes(self, sender, e):
        self.renew_food_shapes_flag = True
    
    def MenuItem_Click(self, sender, e):
        if self.animal_window is None or not self.animal_window.IsLoaded:
            self.animal_window = AnimalWindow()            
            self.animal_window.animal = self.selected_animal
            self.animal_window.Show()
    
    def canvas_MouseLeftButtonDown(self, sender, e):
        point = e.GetPosition(self.canvas)
        self.selected_animal = self.world.get_animal(point.X, point.Y)
        if self.animal_window:
            self.animal_window.animal = self.selected_animal
        self.renew_animal_shapes_flag = True


if __name__ == '__main__':
    Application().Run(MyWindow())