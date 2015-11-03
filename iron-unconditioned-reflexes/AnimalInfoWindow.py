from gi.repository import Gtk, GObject
from Animal import Animal


class AnimalInfoWindow(object):
    def __init__(self, selected_animal):
        self._animal = selected_animal
        self.energy_graphic = Graphic(100, 100, lambda: self.animal.energy / Animal.MAX_ENERGY)
        self.bud_graphic = Graphic(100, 100, lambda: self.animal.readiness_to_bud / Animal.READINESS_TO_BUD_THREADSHOULD)

        builder = Gtk.Builder()
        builder.add_from_file("AnimalInfo.glade")
        builder.connect_signals(self)

        self.window = builder.get_object("window1")

        self.window.realize()
        self.window.set_reallocate_redraws(True)
        self.window.set_title("Animals")

        self.drawing_area1 = builder.get_object("drawingarea1")
        self.drawing_area2 = builder.get_object("drawingarea2")

        self.window.show_all()

    def update_graphics(self):
        if self.animal:
            self.energy_graphic.update()
            self.bud_graphic.update()

    def on_drawingarea1_configure(self, widget, event):
        self.energy_graphic.resize(widget.get_allocated_width(), widget.get_allocated_height())
        return True

    def on_drawingarea2_configure(self, widget, event):
        self.bud_graphic.resize(widget.get_allocated_width(), widget.get_allocated_height())
        return True

    def on_drawingarea1_draw(self, widget, cr):
        cr.set_line_width(1)
        cr.set_source_rgb(1,0,0)

        cr.move_to(0, self.energy_graphic[0])
        for i in range(1, len(self.energy_graphic)):
            cr.line_to(i, self.energy_graphic[i])
        cr.stroke()

    def on_drawingarea2_draw(self, widget, cr):
        cr.set_line_width(1)
        cr.set_source_rgb(0,1,0)

        cr.move_to(0, self.bud_graphic[0])
        for i in range(1, len(self.bud_graphic)):
            cr.line_to(i, self.bud_graphic[i])
        cr.stroke()

    @property
    def animal(self):
        return self._animal

    @animal.setter
    def animal(self, value):
        self._animal = value
        self.energy_graphic.reset()
        self.bud_graphic.reset()


class Graphic(object):
    def __init__(self, width, height, getter):
        self._width = width
        self._height = height
        self.getter = getter

        self.history = [0]*width
        self.index = 0


    def update(self):
        self.history[self.index] = (1.0 - self.getter()) * self._height
        self.index += 1
        if self.index >= self._width:
            self.index = 0

    def resize(self, width, height):
        self._width = width
        self._height = height
        self.reset()

    def reset(self):
        self.history = [0]*self._width
        self.index = 0

    def __len__(self):
        return self._width

    def __getitem__(self, i):
        return self.history[(self.index + i) % self._width]