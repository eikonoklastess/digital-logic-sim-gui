from circuit import Point, tk
from pin import Input, Output
import uuid

class Gate():
    def __init__(self, canvas, pos):
        self.c = canvas
        self.pos = pos
        self.inputs = []
        self.outputs = []
        self.tag = str(uuid.uuid4())
        self.padding = 10
        self.catching_area = None
        
    def calc_output(self):
        raise NotImplementedError("Subclass must implement this method")

    def draw(self):
        raise NotImplementedError("Subclass must implement this method")

    def draw_pins(self):
        for input in self.inputs:
            input.draw()
        for output in self.outputs:
            output.draw()

    def add_input(self, id):
        input = Input(self.c, self, id)
        self.inputs.append(input)
    
    def add_output(self, id):
        output = Output(self.c, self, id)
        self.outputs.append(output)

class And_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(1)
        self.add_input(2)
        self.add_output(0)

    def draw(self):
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x+self.h-30, self.pos.y, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y+self.w, self.pos.x+self.h-30, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_arc(self.pos.x+self.h-60, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))

        self.draw_pins()

    def calc_output(self):
        pass

class Or_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(1)
        self.add_input(2)
        self.add_output(0)

    def draw(self):
        self.c.create_arc(self.pos.x-10, self.pos.y, self.pos.x+10, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.c.create_arc(self.pos.x-60, self.pos.y, self.pos.x+60, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))

        self.draw_pins()

    def calc_output(self):
        pass

class Not_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(0)
        self.add_output(0)

    def draw(self):
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+(self.w//2), fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y+self.w, self.pos.x+self.h, self.pos.y+(self.w//2), fill="blacK", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))
        self.draw_pins()

    def calc_output(self):
        pass
