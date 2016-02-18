import wpf

from System.Windows import Window
from System.Windows.Shapes import Ellipse, Line
from System.Windows.Media import Brushes, Color, SolidColorBrush

class AnimalWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'animal_window.xaml')
        self.animal = None

    def update(self):
        if not self.animal:
            return
        self.draw_animal_brain()
        self.textBlock.Text = "energy={}\nenergy_fullness={}\nreadiness_to_sex={}\nsmell_size={}".format(
            self.animal.energy,
            self.animal.energy_fullness,
            self.animal.readiness_to_sex,
            self.animal.smell_size
        )

    def draw_animal_brain(self):
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

        for i in range(len(brain)-1):
            self.draw_layers_connections(brain, i, i+1, neuron_size)


    def draw_layers_connections(self, brain, first_layer_index, second_layer_index, neuron_size):
        first_layer_margin = (self.canvas.ActualWidth - len(brain.layers[first_layer_index]) * neuron_size) / (len(brain.layers[first_layer_index]) + 1)
        second_layer_margin = (self.canvas.ActualWidth - len(brain.layers[second_layer_index]) * neuron_size) / (len(brain.layers[second_layer_index]) + 1)
        for second_layer_neuron_index, second_layer_neuron in enumerate(brain.layers[second_layer_index]):
            for first_layer_neuron_index, first_layer_neuron in enumerate(brain.layers[first_layer_index]):
                line = Line()
                line.X1 = second_layer_margin + second_layer_neuron_index * (neuron_size + second_layer_margin) + neuron_size / 2.0
                line.Y1 = second_layer_index * neuron_size * 2.0 + neuron_size / 2.0
                line.X2 = first_layer_margin + first_layer_neuron_index * (neuron_size + first_layer_margin) + neuron_size / 2.0
                line.Y2 = first_layer_index * neuron_size * 2.0 + neuron_size / 2.0
                line.StrokeThickness = 2
                line.Stroke = SolidColorBrush(get_color(second_layer_neuron.w[first_layer_neuron_index]))
                self.canvas.AddChild(line)

def get_color(value):
    r = 0
    g = min(255, max(0, value * 255))
    b = min(255, max(0, -value * 255))
    return Color.FromRgb(r, g, b)

          