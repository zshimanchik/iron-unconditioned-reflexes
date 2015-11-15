import wpf

from System import TimeSpan
from System.Windows import Application, Window, Point
from System.Windows.Threading import DispatcherTimer
from System.Windows.Shapes import *
from System.Windows.Controls import Grid, Canvas
from System.Windows.Media import Brushes, ScaleTransform, TranslateTransform, RotateTransform, TransformGroup

import math
from time import time
from random import random, randint

import World


class MyWindow(Window):
    def __init__(self):        
        self.mouse_drag = False
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
        
    def add_line(self, x1, y1, x2, y2):
        ln = Line()
        ln.X1 = x1
        ln.Y1 = y1
        ln.X2 = x2
        ln.Y2 = y2
        ln.StrokeThickness = 0.1
        ln.Stroke = Brushes.Gray
        self.canvas.Children.Add(ln)
        


    def make_food_shape(self, x, y, size):
        el = Ellipse()
        el.Fill = Brushes.Gray
        el.Height=1
        el.Width=1
        #el.RenderTransform = TranslateTransform(-0.5, -0.5)
        return el


    def make_animal_shape(self, x, y, size, brush):
        canvas = Canvas()

        el = Ellipse()
        el.Fill = brush
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

    def draw(self):
        self.canvas.Children.Clear()

        if self.chunks_checkBox.IsChecked:
            for row in range(1, int(self.world.height / self.world.CHUNK_SIZE)+1):
                self.add_line(0, self.world.CHUNK_SIZE * row, self.world.width, self.world.CHUNK_SIZE * row)

            for col in range(1, int(self.world.width/ self.world.CHUNK_SIZE)+1):
                self.add_line(self.world.CHUNK_SIZE * col, 0, self.world.CHUNK_SIZE * col, self.world.height)

        for animal in self.world.animals:
            if not hasattr(animal, 'shape'):
                animal.shape = self.make_animal_shape(animal.x, animal.y, animal.size, Brushes.Green)
            tg = TransformGroup()
            tg.Children.Add(ScaleTransform(10, 10))
            tg.Children.Add(RotateTransform(math.degrees(animal.angle)))
            tg.Children.Add(TranslateTransform(animal.x, animal.y))
            animal.shape.RenderTransform = tg            
            self.canvas.Children.Add(animal.shape)

        for food in self.world.food:
            if not hasattr(food, 'shape'):
                food.shape = self.make_food_shape(food.x, food.y, food.size)
                
            tg = TransformGroup()
            tg.Children.Add(TranslateTransform(-0.5, -0.5))
            tg.Children.Add(ScaleTransform(food.size, food.size))
            tg.Children.Add(TranslateTransform(food.x, food.y))
            food.shape.RenderTransform = tg
            self.canvas.Children.Add(food.shape)
                    
    def timer_slider_ValueChanged(self, sender, e):        
        self.timer.Interval = TimeSpan(0, 0, 0, 0, sender.Value)
    
    def scale_slider_ValueChanged(self, sender, e):
        # todo fix this crutch
        if hasattr(self,'canvas'):
            self.canvas.RenderTransform = ScaleTransform(sender.Value, sender.Value)
        
    def canvas_SizeChanged(self, sender, e):
        self.world.width = sender.ActualWidth
        self.world.height= sender.ActualHeight
        
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
        self.scale_slider.Value += (e.Delta/120)*0.3
    
    def food_slider_ValueChanged(self, sender, e):
        self.world.food_timer = int(sender.Value)
        

        


if __name__ == '__main__':
    Application().Run(MyWindow())