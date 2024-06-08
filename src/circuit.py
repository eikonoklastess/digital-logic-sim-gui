import uuid
from pin import Input, Output
from gate import And_Gate, Or_Gate, Not_Gate
import tkinter as tk
from tkinter import Canvas, ttk

window = tk.Tk()
window.title("Digital Logic GUI")
window.geometry("1920x1080")
c = Canvas(window, height=1080, width=1920, bg="white")
c.pack()

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Circuit():
    def __init__(self, canvas):
        self.c = canvas
        self.gates = []
        self.drag_data = {"x":0, "y":0, "gate":None, "output":None}
        self.c.tag_bind("gate_catching_area", "<ButtonPress-1>", self.gate_on_click)
        self.c.tag_bind("gate_catching_area", "<B1-Motion>", self.gate_on_dragbis)
        self.c.tag_bind("gate_catching_area", "<ButtonRelease-1>", self.gate_on_release)
        self.c.tag_bind("output_catching_area", "<ButtonPress-1>", self.pin_on_click)
        self.c.tag_bind("output_catching_area", "<B1-Motion>", self.pin_on_drag)
        self.c.tag_bind("input_catching_area", "<ButtonRelease-1>", self.pin_on_release)
        
    def add_gate(self, gate):
        self.gates.append(gate)

    def draw(self):
        for gate in self.gates:
            gate.draw()

    def gate_on_click(self, event):
        for gate in self.gates:
            tags = self.c.gettags(gate.catching_area)
            if "current" in tags:
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["gate"] = gate
    def gate_on_dragbis(self, event):
        if self.drag_data["gate"] is not None:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.c.move(self.drag_data["gate"].tag, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            coords = self.c.coords(self.drag_data["gate"].catching_area)
            self.drag_data["gate"].pos = Point(coords[0], coords[1])
            for input in self.drag_data["gate"].inputs:
                if input.connexion is not None:
                    output = input.connexion
                    tag = "connection"+output.tag
                    self.c.delete(tag)
                    output.draw_connections()

            for output in self.drag_data["gate"].outputs:
                tag = "connection"+output.tag
                self.c.delete(tag)
                output.draw_connections()
            

    def gate_on_release(self, event):
        coords = self.c.coords(self.drag_data["gate"].catching_area)
        self.drag_data["gate"].pos = Point(coords[0], coords[1])
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0
        self.drag_data["gate"] = None

    def pin_on_click(self, event):
        for gate in self.gates:
            for output in gate.outputs:
                tags = self.c.gettags(output.catching_area)
                if "current" in tags:
                    self.drag_data["x"] = output.get_tip().x
                    self.drag_data["y"] = output.get_tip().y
                    self.drag_data["output"] = output

    def pin_on_drag(self, event):
        tag = "connection"+self.drag_data["output"].tag
        self.c.delete(tag)
        self.drag_data["output"].draw_connections(x=event.x, y=event.y)
    
    def pin_on_release(self, event):
        if self.drag_data["output"] is not None:
            tag = "connection"+self.drag_data["output"].tag
            self.c.delete(tag)
            for gate in self.gates:
                for input in gate.inputs:
                    tags = self.c.gettags(input.catching_area)
                    if "current" in tags:
                        self.drag_data["x"] = input.get_tip().x
                        self.drag_data["y"] = input.get_tip().y
                        self.drag_data["output"].add_connection(input)
                        self.drag_data["output"].draw_connections()
            self.drag_data["output"] = None






circuit = Circuit(c)
circuit.add_gate(And_Gate(c, Point(600, 600)))
circuit.add_gate(Or_Gate(c, Point(600, 800)))
circuit.add_gate(Not_Gate(c, Point(800, 600)))
circuit.draw()











window.mainloop()
