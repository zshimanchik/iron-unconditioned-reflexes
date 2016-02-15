from System.Windows import Point
from System.Windows.Shapes import *
from System.Windows.Controls import Grid, Canvas
from System.Windows.Media import Brushes, ScaleTransform, TranslateTransform, RotateTransform, TransformGroup, RadialGradientBrush, Color

import math

from Animal import Gender
import World


class Renderer(object):
    def __init__(self, canvas, world):
        self.canvas = canvas
        self.world = world

        self.grid = ChunksGrid(world)

        self._draw_chunks = False
        self.draw_animal_smell = False
        self.draw_food_smell = False
        self.draw_eat_distance = False

        self.food_shapes = []
        self.animal_shapes = []
        self._selected_animal = None

    def restart(self):
        self.canvas.Children.Clear()
        self.food_shapes = []
        self.animal_shapes = []

    def render(self):
        self._remove_dead_animals()
        self._remove_empty_food()

        self._draw_animals()
        self._draw_food()

    def _remove_dead_animals(self):
        for animal in self.world.dead_animals:
            self.canvas.Children.Remove(animal.shape.canvas)
            self.animal_shapes.remove(animal.shape)

    def _remove_empty_food(self):
        for food in self.world.empty_food:
            self.canvas.Children.Remove(food.shape.canvas)
            self.food_shapes.remove(food.shape)

    def _draw_animals(self):
        for animal in self.world.animals:
            if not hasattr(animal, 'shape'):
                animal.shape = AnimalShape(animal, self)
                self.canvas.Children.Add(animal.shape.canvas)
                self.canvas.SetZIndex(animal.shape.canvas, 2)
                self.animal_shapes.append(animal.shape)
            animal.shape.update_state()

    def _draw_food(self):
        for food in self.world.food:
            if not hasattr(food, 'shape'):
                food.shape = FoodShape(food, self)
                self.canvas.Children.Add(food.shape.canvas)
                self.food_shapes.append(food.shape)
            food.shape.update_state()

    @property
    def draw_chunks(self):
        return self._draw_chunks

    @draw_chunks.setter
    def draw_chunks(self, value):
        self._draw_chunks = bool(value)
        if value:
            _safe_add_to_canvas(self.canvas, self.grid.canvas)
        else:
            _safe_remove_from_canvas(self.canvas, self.grid.canvas)

    @property
    def selected_animal(self):
        return self._selected_animal

    @selected_animal.setter
    def selected_animal(self, value):
        if self._selected_animal:
            self._selected_animal.shape.set_default_body_brush()

        self._selected_animal = value

        if self._selected_animal:
            self._selected_animal.shape.body_brush = Brushes.Gold


class ChunksGrid(object):
    def __init__(self, world):
        self.world = world
        self.canvas = Canvas()
        self._create_grids()

    def _create_grids(self):
        self._create_grid(self.world.FEMALE_CHUNK_SIZE, Brushes.Gray)
        self._create_grid(self.world.FOOD_CHUNK_SIZE, Brushes.Red)
        self._create_grid(self.world.SMELL_CHUNK_SIZE, Brushes.DarkGreen)

    def _create_grid(self, size, brush):
        for row in range(1, int(self.world.height / size)+1):
            self._create_line(0, size * row, self.world.width, size * row, brush)

        for col in range(1, int(self.world.width / size)+1):
            self._create_line(size * col, 0, size * col, self.world.height, brush)

    def _create_line(self, x1, y1, x2, y2, brush=Brushes.Gray):
        ln = Line()
        ln.X1 = x1
        ln.Y1 = y1
        ln.X2 = x2
        ln.Y2 = y2
        ln.StrokeThickness = 0.2
        ln.Stroke = brush
        self.canvas.Children.Add(ln)


class AnimalShape(object):
    def __init__(self, animal, renderer):
        self._draw_smell = False
        self._animal = animal
        self._renderer = renderer
        self._create_shape()
        self.update_state()

    def _create_shape(self):
        self.canvas = Canvas()
        self._create_body_shape()
        self._create_smell_shape()

    def _create_body_shape(self):
        self._body_canvas = Canvas()
        self._create_body_ellipse()
        self._create_angle_line()
        self._body_canvas.RenderTransformOrigin = Point(0, 0)
        self.canvas.Children.Add(self._body_canvas)

    def _create_body_ellipse(self):
        self._body_ellipse = Ellipse()
        self.set_default_body_brush()
        self._body_ellipse.Height = 1
        self._body_ellipse.Width = 1
        self._body_ellipse.RenderTransform = TranslateTransform(-0.5, -0.5)
        self._body_canvas.Children.Add(self._body_ellipse)

    def set_default_body_brush(self):
        if self._animal.gender == Gender.FEMALE:
            self.body_brush = Brushes.DarkRed
        else:
            self.body_brush = Brushes.Green

    def _create_angle_line(self):
        self._angle_line = Line()
        self._angle_line.X1 = 0.5
        self._angle_line.Y1 = 0.5
        self._angle_line.X2 = 1
        self._angle_line.Y2 = 0.5
        self._angle_line.StrokeThickness = 0.1
        self._angle_line.Stroke = Brushes.Black
        self._angle_line.RenderTransform = TranslateTransform(-0.5, -0.5)
        self._body_canvas.Children.Add(self._angle_line)

    def _create_smell_shape(self):
        self._smell_canvas = Canvas()
        self._smell_ellipse = Ellipse()

        color1 = Color.FromArgb(40, 220, 0, 20)
        color2 = Color.FromArgb(0, 220, 0, 20)
        self._smell_ellipse.Fill = RadialGradientBrush(color1, color2)

        self._smell_ellipse.StrokeThickness = 0.1
        self._smell_ellipse.Stroke = Brushes.Gray
        self.smell_size = self._animal.smell_size
        self._smell_canvas.Children.Add(self._smell_ellipse)

    def update_state(self):
        if self.draw_smell != self._renderer.draw_animal_smell:
            self.draw_smell = self._renderer.draw_animal_smell

        tg = TransformGroup()
        tg.Children.Add(ScaleTransform(self._animal.size, self._animal.size))
        tg.Children.Add(RotateTransform(math.degrees(self._animal.angle)))
        self._body_canvas.RenderTransform = tg

        self.smell_size = self._animal.smell_size
        self.canvas.RenderTransform = TranslateTransform(self._animal.x, self._animal.y)

    def _set_body_brush(self, new_brush):
        self._body_ellipse.Fill = new_brush

    body_brush = property(fset=_set_body_brush)

    def _set_smell_size(self, new_smell_size):
        self._smell_ellipse.Height = new_smell_size * 2
        self._smell_ellipse.Width = new_smell_size * 2
        self._smell_ellipse.RenderTransform = TranslateTransform(-new_smell_size, -new_smell_size)

    smell_size = property(fset=_set_smell_size)

    @property
    def draw_smell(self):
        return self._draw_smell

    @draw_smell.setter
    def draw_smell(self, value):
        self._draw_smell = bool(value)
        if value:
            _safe_add_to_canvas(self.canvas, self._smell_canvas)
        else:
            _safe_remove_from_canvas(self.canvas, self._smell_canvas)


class FoodShape(object):
    def __init__(self, food, renderer):
        self._food = food
        self._renderer = renderer
        self._create_shape()
        self._draw_smell = False
        self._draw_eat_distance = False

    def _create_shape(self):
        self.canvas = Canvas()
        self._create_body_shape()
        self._create_smell_shape()
        self._create_eat_distance_shape()

    def _create_body_shape(self):
        self._body_canvas = Canvas()
        self._create_food_ellipse()
        self.canvas.Children.Add(self._body_canvas)

    def _create_food_ellipse(self):
        self._food_ellipse = Ellipse()
        self._food_ellipse.Fill = Brushes.Gray
        self._food_ellipse.Height = 1
        self._food_ellipse.Width = 1
        self._food_ellipse.RenderTransform = TranslateTransform(-0.5, -0.5)
        self._body_canvas.Children.Add(self._food_ellipse)
        self._body_canvas.SetZIndex(self._food_ellipse, 1)

    def _create_smell_shape(self):
        self._smell_ellipse = Ellipse()

        color1 = Color.FromArgb(40, 0, 220, 20)
        color2 = Color.FromArgb(0, 0, 220, 20)
        self._smell_ellipse.Fill = RadialGradientBrush(color1, color2)

        self._smell_ellipse.StrokeThickness = 0.03
        self._smell_ellipse.Stroke = Brushes.Gray

        self._smell_ellipse.Height = World.World.FOOD_SMELL_SIZE_RATIO * 2
        self._smell_ellipse.Width = World.World.FOOD_SMELL_SIZE_RATIO * 2
        self._smell_ellipse.RenderTransform = \
            TranslateTransform(-World.World.FOOD_SMELL_SIZE_RATIO, -World.World.FOOD_SMELL_SIZE_RATIO)

    def _create_eat_distance_shape(self):
        self._eat_distance_canvas = Canvas()

        self._eat_distance_ellipse = Ellipse()
        self._eat_distance_ellipse.StrokeThickness = 0.007
        self._eat_distance_ellipse.Stroke = Brushes.Gray
        self._eat_distance_ellipse.Height = 1
        self._eat_distance_ellipse.Width = 1
        self._eat_distance_ellipse.RenderTransform = TranslateTransform(-0.5, -0.5)

        self._eat_distance_canvas.Children.Add(self._eat_distance_ellipse)

    def update_state(self):
        if self.draw_smell != self._renderer.draw_food_smell:
            self.draw_smell = self._renderer.draw_food_smell

        if self.draw_eat_distance != self._renderer.draw_eat_distance:
            self.draw_eat_distance = self._renderer.draw_eat_distance

        self._body_canvas.RenderTransform = ScaleTransform(self._food.size, self._food.size)

        eat_distance_size = (World.World.EATING_DISTANCE + self._food.size) * 2
        self._eat_distance_canvas.RenderTransform = ScaleTransform(eat_distance_size, eat_distance_size)

        self.canvas.RenderTransform = TranslateTransform(self._food.x, self._food.y)

    @property
    def draw_smell(self):
        return self._draw_smell

    @draw_smell.setter
    def draw_smell(self, value):
        self._draw_smell = bool(value)
        if value:
            _safe_add_to_canvas(self._body_canvas, self._smell_ellipse)
        else:
            _safe_remove_from_canvas(self._body_canvas, self._smell_ellipse)

    @property
    def draw_eat_distance(self):
        return self._draw_eat_distance

    @draw_eat_distance.setter
    def draw_eat_distance(self, value):
        self._draw_eat_distance = bool(value)
        if value:
            _safe_add_to_canvas(self.canvas, self._eat_distance_canvas)
        else:
            _safe_remove_from_canvas(self.canvas, self._eat_distance_canvas)


def _safe_remove_from_canvas(canvas, element_to_remove):
    if canvas.Children.Contains(element_to_remove):
        canvas.Children.Remove(element_to_remove)


def _safe_add_to_canvas(canvas, element_to_add):
    if not canvas.Children.Contains(element_to_add):
        canvas.Children.Add(element_to_add)
