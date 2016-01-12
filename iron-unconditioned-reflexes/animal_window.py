import wpf

from System.Windows import Window

class AnimalWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'animal_window.xaml')
        self.animal = None
