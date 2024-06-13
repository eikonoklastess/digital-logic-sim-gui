from pin import Input, Output
import tkinter as tk
from tkinter import ttk
import uuid
import pprint
import itertools

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Gate():
    def __init__(self, canvas, pos):
        self.c = canvas
        self.pos = pos
        self.inputs = []
        self.outputs = []
        self.tag = str(uuid.uuid4())
        self.padding = 10
        self.catching_area = None
        self.truth_table = None
        
    def __repr__(self):
        raise NotImplementedError("Subclass must implement this method")

    def calc_output(self):
        raise NotImplementedError("Subclass must implement this method")

    def draw(self):
        raise NotImplementedError("Subclass must implement this method")

    def delete(self):
        self.c.delete(self.tag)
        for input in self.inputs:
            input.delete()
        for output in self.outputs:
            output.delete()
        self.inputs = []
        self.outputs = []

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

    def generate_truth_table(self):
        self.truth_table = [[0 for n in range(2**len(self.inputs))] for n in range(len(self.inputs)+len(self.outputs))]
        for n in range(2**len(self.inputs)):
            for m in range(len(self.inputs)):
                pass
        pprint.pprint(self.truth_table)
        k = len(self.inputs)+1
        for cols in range(len(self.inputs)):
            k -= 1
            for rows, i in zip(range(2**len(self.inputs)), itertools.cycle(range(2**k))):
                value = 1 if i >= (2**k)//2 else 0
                self.truth_table[cols][rows] = value
        for output in range(2**len(self.inputs)):
            for n in range(len(self.inputs)):
                self.inputs[n].val = self.truth_table[n][output]
            self.calc_output()
            self.truth_table[-1][output] = self.outputs[0].val
        pprint.pprint(self.truth_table)


class And_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(1)
        self.add_input(2)
        self.add_output(0)

    def __repr__(self):
        return f"AND Gate: tag={self.tag}, input1 val={self.inputs[0].val}, input2 val={self.inputs[1].val}, output val ={self.outputs[0].val}"

    def draw(self):
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x+self.h-30, self.pos.y, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y+self.w, self.pos.x+self.h-30, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_arc(self.pos.x+self.h-60, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))
        
        self.draw_pins()

    def calc_output(self):
        if self.inputs[0].val != -1 and self.inputs[1].val != -1:
            self.outputs[0].val = self.inputs[0].val & self.inputs[1].val
        else:
            raise ValueError(f"tried to calc output while inputs uninitialized of: {self.__repr__}")

class Or_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(1)
        self.add_input(2)
        self.add_output(0)

    def __repr__(self):
        return f"OR Gate: tag={self.tag}, input1 val={self.inputs[0].val}, input2 val={self.inputs[1].val}, output val ={self.outputs[0].val}"

    def draw(self):
        self.c.create_arc(self.pos.x-10, self.pos.y, self.pos.x+10, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.c.create_arc(self.pos.x-60, self.pos.y, self.pos.x+60, self.pos.y+self.w, outline="black", extent=180, start=270, style=tk.ARC, tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))

        self.draw_pins()

    def calc_output(self):
        if self.inputs[0].val != -1 and self.inputs[1].val != -1:
            self.outputs[0].val = self.inputs[0].val or self.inputs[1].val
        else:
            raise ValueError(f"tried to calc output while inputs uninitialized of: {self.__repr__}")

class Not_Gate(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 60
        self.w = 50
        # self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", tags=(self.tag, "gate_catching_area", "gate"))
        self.add_input(0)
        self.add_output(0)

    def __repr__(self):
        return f"NOT Gate: tag={self.tag}, input1 val={self.inputs[0].val}, output val ={self.outputs[0].val}"

    def draw(self):
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+(self.w//2), fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y+self.w, self.pos.x+self.h, self.pos.y+(self.w//2), fill="blacK", tags=(self.tag, "gate", "gate_proper"))
        self.c.create_line(self.pos.x, self.pos.y, self.pos.x, self.pos.y+self.w, fill="black", tags=(self.tag, "gate", "gate_proper"))
        self.catching_area = self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x+self.h, self.pos.y+self.w, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate"))
        self.draw_pins()

    def calc_output(self):
        if self.inputs[0].val != -1:
            self.outputs[0].val = abs(self.inputs[0].val - 1)
        else:
            raise ValueError(f"tried to calc output while inputs uninitialized of: {self.__repr__}")

class Circuit_Input(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 30
        self.w = 30
        self.settable_in = None
        self.val = 0
        self.add_output(0)

    def draw(self):
        self.catching_area = self.c.create_rectangle(
            self.pos.x,
            self.pos.y,
            self.pos.x+self.h,
            self.pos.y+self.w,
            fill="red",
            outline="red",
            tags=(self.tag, "gate", "gate_proper", "gate_catching_area", "circuit_input_catching_area"),)

        self.draw_pins()

        stringvar1 = tk.StringVar(value=f"{self.outputs[0].val}")
        def button_fun_1():
            if stringvar1.get() == "0":
                stringvar1.set("1")
                self.outputs[0].val = 1
                self.val = 1
            else:
                self.outputs[0].val = 0
                self.val = 0
                stringvar1.set(f"{self.outputs[0].val}")
        button1 = ttk.Button(self.c, text="1", width=1, textvariable=stringvar1, command=button_fun_1)
        self.c.create_window(self.pos.x-30, self.pos.y, window=button1, tags=(self.tag, "gate", "input"))

    def __repr__(self):
        return f"input Gate: tag={self.tag}, output1 val={self.outputs[0].val}"

    def calc_output(self):
        self.outputs[0].val = self.val 

class Circuit_Output(Gate):
    def __init__(self, canvas, pos):
        super().__init__(canvas, pos)
        self.h = 30
        self.w = 30
        self.settable_out = None
        self.add_input(0)

    def draw(self):
        self.catching_area = self.c.create_rectangle(
            self.pos.x,
            self.pos.y,
            self.pos.x+self.h,
            self.pos.y+self.w,
            fill="red",
            outline="red",
            tags=(self.tag, "gate", "gate_proper", "gate_catching_area", "circuit_output_catching_area"),)

        self.draw_pins()

        self.settable_out = ttk.Button(self.c, text=f"{self.inputs[0].val}")
        self.c.create_window(self.pos.x+self.h, self.pos.y, window=self.settable_out, tags=(self.tag, "gate", "output", "circuit_output"))

    def __repr__(self):
        return f"Output Gate: tag={self.tag}, input1 val={self.inputs[0].val}"

    def calc_output(self):
        print("calc_output circuit output")



















