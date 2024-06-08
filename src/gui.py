import tkinter as tk
import uuid
GATE_H = 30
GATE_W = 50

class Gui():
    def __init__(self, width, height):
        self.root = tk.Tk()
        self.root.title("digital logic sim")
        self.root.geometry(f"{width}x{height}")
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.is_running = False

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self):
        self.is_running = True

        while self.is_running:
            self.redraw()

    def close(self):
        self.is_running = False

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pin():
    def __init__(self, gate, id, model):
        self.canvas = gate.canvas
        self.gate = gate
        #id refers to the position of the pin on the gate ex: input pin1, input pin2, output pin0
        self.id = id
        self.val = -1
        self.model = model
        self.tag = str(uuid.uuid4())
        self.padding = 10 

    def draw(self):
        print("safe")
        if self.model == "input":
            if self.id == 1:
                dy = 10
            else:
                dy = 40
            self.canvas.create_line(self.gate.pos.x-20, self.gate.pos.y+dy, self.gate.pos.x, self.gate.pos.y+dy, fill="black", activefill="red", tags=(self.tag, self.gate.tag, "gate", self.model))
        else:
            dy = GATE_W//2
            self.canvas.create_line(self.gate.pos.x+GATE_H+30, self.gate.pos.y+dy, self.gate.pos.x+GATE_H+50, self.gate.pos.y+dy, fill="black", activefill="red", tags=(self.tag, self.gate.tag, "gate", self.model))

    def set_val(self, val):
        if val == 1 or val == 0:
            self.val = val
        else:
            raise ValueError("pin value tried to be set to value outside of 0 or 1")

    def add_connection(self, cable):
        self.cable = cable

    def propagate(self):
        if self.model == "output":
            self.cable.propagate()
        else:
            raise ValueError("propagate method called on input pin")

    def get_tip(self):
        if self.model == "output":
            return Point(self.gate.pos.x+GATE_H+30+20, self.gate.pos.y)
        else:
            dy = (self.gate.gate_w//len(self.gate.inputs))*self.id
            return Point(self.gate.pos.x-20, self.gate.pos.y+dy)


class Cable():
    def __init__(self, canvas):
        self.canvas = canvas
        self.tag = str(uuid.uuid4())
        self.start_pin = None
        self.end_pin = None
        self.val = None
        self.drag_data = {"x": 0, "y": 0}
        # self.canvas.tag_bind("output","<ButtonPress-1>", self.on_click)
        # self.root.canvas.tag_bind("output", "<B1-Motion>", self.while_press)
        # self.canvas.tag_bind("input", "<ButtonRelease-1>", self.on_release)

    def add_start(self, pin):
        self.start_pin = pin
    def add_end(self, pin):
        self.end_pin = pin
    def propagate(self):
        if self.end_pin is not None and self.start_pin is not None:
            self.end_pin.val = self.start_pin.val

    def draw(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y1, fill="black", tags=(self.tag, "connection"))
        self.canvas.create_line(x2, y1, x2, y2, fill="black", tags=(self.tag, "connection"))
    def on_click(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    def while_press(self, event):
        self.canvas.delete(self.tag)
        self.draw(self.drag_data["x"], self.drag_data["y"], event.x, event.y)
    def on_release(self, event):
        self.canvas.delete(self.tag)
        self.draw(self.drag_data["x"], self.drag_data["y"], event.x, event.y)
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0 

class Gate():
    def __init__(self, pos, canvas):
        self.inputs = []
        self.outputs = []
        self.pos = pos
        self.canvas = canvas
        self.tag = str(uuid.uuid4())
        self.catching_area = self.canvas.create_rectangle(self.pos.x, self.pos.y, self.pos.x+GATE_H, self.pos.y+GATE_W, outline="", fill="", tags=(self.tag, "gate", "catching_area"))
        self.canvas.tag_bind(self.catching_area, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag, "<Leave>", self.on_leave)
    #movement
    def on_enter(self, event):
        items = self.canvas.find_withtag(self.tag)
        for item in items:
            tags = self.canvas.gettags(item)
            if "gate_proper" in tags:
                self.canvas.itemconfig(item, fill="red")
                if self.canvas.type(item) == "arc":
                    self.canvas.itemconfig(item, outline="red")
    def on_leave(self, event):
        self.canvas.itemconfig("gate_proper", fill="black")
        items = self.canvas.find_withtag(self.tag)
        for item in items:
            if self.canvas.type(item) == "arc":
                self.canvas.itemconfig(item, outline="black")

    def add_input(self):
        self.inputs.append(Pin(self, 1, "input"))
        self.inputs.append(Pin(self, 2, "input"))

    def add_output(self):
        self.outputs.append(Pin(self, 0, "output"))

    def draw_pins(self):
        for input in self.inputs:
            input.draw()
        for output in self.outputs:
            output.draw()

    def calc_output(self):
        raise NotImplementedError("Subclass must implement this method")
    def draw(self):
        raise NotImplementedError("Subclass must implement this method")

class And_Gate(Gate):
    def draw(self):
        self.canvas.create_line(self.pos.x, self.pos.y, self.pos.x+GATE_H, self.pos.y, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_line(self.pos.x, self.pos.y+GATE_W, self.pos.x+GATE_H, self.pos.y+GATE_W, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+GATE_W, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_arc(self.pos.x+GATE_H-30, self.pos.y, self.pos.x+GATE_H+30, self.pos.y+GATE_W, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        # self.canvas.create_line(self.pos.x+GATE_H+30, self.pos.y+(GATE_W//2), self.pos.x+GATE_H+50, self.pos.y+(GATE_W//2), fill="black", activefill="red", tags=(self.tag, "gate", "output"))
        # self.canvas.create_line(self.pos.x-20, self.pos.y+10, self.pos.x, self.pos.y+10, fill="black", activefill="red", tags=(self.tag, "gate", "input"))
        # self.canvas.create_line(self.pos.x-20, self.pos.y+40, self.pos.x, self.pos.y+40, fill="black", activefill="red", tags=(self.tag, "gate", "input"))
        self.add_input()
        self.add_output()
        self.draw_pins()
    # def calc_output(self):
    #     if self.input_gates[0].output != -1 and self.input_gates[1].output != -1:
    #         self.output = self.input_gates[0].output & self.input_gates[1].output
    #     else:
    #         raise ValueError("value of input was not initialized")
class Or_Gate(Gate):
    def draw(self):
        self.canvas.create_arc(self.pos.x-10, self.pos.y, self.pos.x+10, self.pos.y+GATE_W, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_arc(self.pos.x-60, self.pos.y, self.pos.x+60, self.pos.y+GATE_W, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        # self.canvas.create_line(self.pos.x+GATE_H+30, self.pos.y+(GATE_W//2), self.pos.x+GATE_H+50, self.pos.y+(GATE_W//2), fill="black", activefill="red", tags=(self.tag, "gate", "output"))
        # self.canvas.create_line(self.pos.x-20, self.pos.y+10, self.pos.x+7, self.pos.y+10, fill="black", activefill="red", tags=(self.tag, "gate", "input"))
        # self.canvas.create_line(self.pos.x-20, self.pos.y+40, self.pos.x+7, self.pos.y+40, fill="black", activefill="red", tags=(self.tag, "gate", "input"))
        self.add_input()
        self.add_output()
        self.draw_pins()
    # def calc_output(self):
    #     if self.input_gates[0].output != -1 and self.input_gates[1].output != -1:
    #         self.output = self.input_gates[0].output or self.input_gates[1].output
    #     else:
    #         raise ValueError("value of input was not initialized")
class Not_Gate(Gate):
    def draw(self):
        self.canvas.create_line(self.pos.x, self.pos.y, self.pos.x+GATE_H+30, self.pos.y+(GATE_W//2), fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_line(self.pos.x, self.pos.y+GATE_W, self.pos.x+GATE_H+30, self.pos.y+(GATE_W//2), fill="blacK", tags=(self.tag, "gate", "gate_proper"))
        self.canvas.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+GATE_W, fill="black", tags=(self.tag, "gate", "gate_proper"))
        # self.canvas.create_line(self.pos.x+GATE_H+30, self.pos.y+(GATE_W//2), self.pos.x+GATE_H+50, self.pos.y+(GATE_W//2), fill="black", activefill="red", tags=(self.tag, "gate", "output"))
        # self.canvas.create_line(self.pos.x-20, self.pos.y+(GATE_W//2), self.pos.x, self.pos.y+(GATE_W//2), fill="black", activefill="red", tags=(self.tag, "gate", "input"))
        self.add_input()
        self.add_output()
        self.draw_pins()
    # def calc_output(self):
    #     if self.input_gates[0].output != -1:
    #         if self.input_gates[0].output == 0:
    #             self.output = 1
    #         else:
    #             self.output = 0
    #     else:
    #         raise ValueError("value of input was not initialized")

class Circuit():
    def __init__(self, canvas):
        self.gates = []
        self.inputs = []
        self.cables = []
        self.canvas = canvas
        self.drag_data = {"x": 0, "y": 0}
        self.current = None
        self.canvas.tag_bind("output", "<ButtonPress-1>", self.select_start_cable)
        self.canvas.tag_bind("output", "<B1-Motion>", self.on_drag_cable)
        self.canvas.tag_bind("input", "<ButtonRelease-1>", self.on_release_cable)
        self.canvas.tag_bind("catching_area", "<ButtonPress-1>", self.on_start)
        self.canvas.tag_bind("catching_area", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("catching_area", "<ButtonRelease-1>", self.on_end)
        self.gate = None

    def select_start_cable(self, event):
        self.choose(event)
        if self.gate is not None:
            print("cable")
            cable = Cable(self.canvas)
            self.cables.append(cable)
            gate_elements = self.canvas.find_withtag(self.gate.tag)
            for element in gate_elements:
                tags = self.canvas.gettags(element)
                if "output" in tags:
                    cable.add_start(self.gate.outputs[0])
                    pin = self.gate.outputs[0]
                    tip = pin.get_tip()
                    cable.drag_data["x"] = tip.x
                    cable.drag_data["y"] = tip.y

    def on_drag_cable(self, event):
        print(len(self.cables))
        cable = self.cables[len(self.cables)-1]
        self.canvas.delete(self.cables[len(self.cables)-1].tag)
        cable.draw(cable.drag_data["x"], cable.drag_data["x"], event.x, event.y)

    def on_release_cable(self, event):
        self.canvas.delete(self.cables[len(self.cables)-1].tag)
        self.cables[len(self.cables)-1].draw()

    
    def add_gate(self, gate):
        self.gates.append(gate)

    def draw(self):
        for gate in self.gates:
            gate.draw()

    def choose(self, event):
        print("entered choose")
        x, y = event.x, event.y
        for gate in self.gates:
            if x > gate.pos.x and x < gate.pos.x+60 and y > gate.pos.y and y < gate.pos.y+40:
                print("entered loop and gate choosing")
                self.current = gate
                break
            elif x > gate.pos.x+60 and x < gate.pos.x+80 and y > gate.pos.y+10 and y < gate.pos.y+40:
                print("chose gate's output")
                self.current = [gate.pos.x+80, gate.pos.y+20]
                self.gate = gate

    def on_start(self, event):
        self.choose(event)
        if isinstance(self.current, Gate):
            print(self.current.tag)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
        elif isinstance(self.current, list):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if isinstance(self.current, Gate):
            self.canvas.move(self.current.tag, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.current.pos.x += dx
            self.current.pos.y += dy
        # elif isinstance(self.current, list):
            # connection = Connection(self.gate, self, x=dx, y=dy)
            # connection.draw()
            # self.canvas.delete(connection.tag)

    def on_end(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if isinstance(self.current, Gate):
            self.drag_data["x"] = 0
            self.drag_data["y"] = 0
            self.current = None
        # elif isinstance(self.current, list):
        #     connection = Connection(self.gate, self, x=dx, y=dy)
        #     connection.draw()

    def connect(self, event):
        pass
















