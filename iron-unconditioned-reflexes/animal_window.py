import wpf

from System.Windows import Window
from System.Windows.Shapes import Ellipse, Line
from System.Windows.Media import Brushes, Color, SolidColorBrush

class AnimalWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'animal_window.xaml')
        self.animal = None

    def draw_animal_brain(self):
        if not self.animal:
            return

        self.canvas.Children.Clear()
        brain = self.animal.brain
        width_count = max(len(brain.layers[0]), len(brain.layers[1]), len(brain.layers[-1]))
        neuron_size = min(self.canvas.ActualWidth / (width_count * 1.5), self.canvas.ActualHeight / (3.0 * 2.0))
        
        for layer_index, layer in enumerate(brain):
            neuron_margin = (self.canvas.ActualWidth - len(layer) * neuron_size) / (len(layer) + 1)
            for neuron_index, neuron in enumerate(layer):
                el = Ellipse()
                el.Height = neuron_size
                el.Width = neuron_size
                el.Fill = SolidColorBrush(get_color(neuron.out))
                self.canvas.AddChild(el)
                self.canvas.SetTop(el, layer_index * neuron_size * 2) 
                self.canvas.SetLeft(el, neuron_index * (neuron_size + neuron_margin) + neuron_margin)

        input_layer_margin = (self.canvas.ActualWidth - len(brain.layers[0]) * neuron_size) / (len(brain.layers[0]) + 1)
        middle_layer_margin = (self.canvas.ActualWidth - len(brain.layers[1]) * neuron_size) / (len(brain.layers[1]) + 1)
        output_layer_margin = (self.canvas.ActualWidth - len(brain.layers[-1]) * neuron_size) / (len(brain.layers[-1]) + 1)
        
        for middle_neuron_index, middle_neuron in enumerate(brain.layers[1]):
            for input_neuron_index, input_neuron in enumerate(brain.layers[0]):
                line = Line()
                line.X1 = middle_layer_margin + middle_neuron_index * (neuron_size + middle_layer_margin) + neuron_size / 2.0
                line.Y1 = 1 * neuron_size * 2.0 + neuron_size / 2.0
                line.X2 = input_layer_margin + input_neuron_index * (neuron_size + input_layer_margin) + neuron_size / 2.0
                line.Y2 = 0 * neuron_size * 2.0 + neuron_size / 2.0
                line.StrokeThickness = 2
                line.Stroke = SolidColorBrush(get_color(middle_neuron.w[input_neuron_index]))
                self.canvas.AddChild(line)

        for output_neuron_index, output_neuron in enumerate(brain.layers[-1]):
            for middle_neuron_index, middle_neuron in enumerate(brain.layers[1]):
                line = Line()
                line.X1 = output_layer_margin + output_neuron_index * (neuron_size + output_layer_margin) + neuron_size / 2.0
                line.Y1 = 2 * neuron_size * 2.0 + neuron_size / 2.0
                line.X2 = middle_layer_margin + middle_neuron_index * (neuron_size + middle_layer_margin) + neuron_size / 2.0
                line.Y2 = 1 * neuron_size * 2.0 + neuron_size / 2.0                
                line.StrokeThickness = 2
                line.Stroke = SolidColorBrush(get_color(output_neuron.w[middle_neuron_index]))
                self.canvas.AddChild(line)

def get_color(value):
    r = 0
    g = min(255, max(0, value * 255))
    b = min(255, max(0, -value * 255))
    return Color.FromRgb(r, g, b)

          