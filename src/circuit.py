from os import truncate
from main import CircuitDesigner
from pin import Pin
from point import Point
from gate import Gate
from pathlib import Path
import os
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog
from tkinter.simpledialog import askstring
import csv
import pprint as pp
import itertools 
from collections import deque

class Circuit():
    def __init__(self, canvas: CircuitDesigner) -> None:
        # Logical representation
        self.truth_table: list = []  # truth table of the circuit

        # Graphical representation
        self.c: CircuitDesigner = canvas
        self.elements = {}  # all element in the circuit
        #self.pin_size = 10 
        # self.gate_h = 80
        # self.gate_w = 100

        # event handling
        self.drag_data = {"x": 0, "y": 0, "object": None}
        self.availabe_circuits = []
        self.update_available_circuits()
        self.context_menu: tk.Menu = tk.Menu(canvas.parent, tearoff=0)
        self.gate_context_menu: tk.Menu = tk.Menu(canvas.parent, tearoff=0)
        canvas.bind("<ButtonPress-1>", self.select_element)
        canvas.bind("<ButtonPress-2>", self.select_element)
        canvas.bind("<ButtonRelease-1>", self.unselect_element)
        canvas.bind("<ButtonRelease-2>", self.unselect_element)
        canvas.bind("<B1-Motion>", self.drag_element_B1)
        canvas.tag_bind("output", "<B2-Motion>", self.drag_element_B2)

    # Logic handling functions
    def solve(self) -> None:
        list(map(print, self.elements.values()))
        solving_queue = deque()
        for gate in [element for element in list(self.elements.values()) if isinstance(element, Gate)]:
            solving_queue.append(gate)
        for circuit_input in [element for element in list(self.elements.values()) if isinstance(element, Pin) and not element.in_gate]:
            circuit_input.propagate()
            if circuit_input.val == -1 and circuit_input.type_ == "output":
                return None
        while len(solving_queue) > 0:
            current_gate = solving_queue.popleft()
            will_continue = False
            for input in list(current_gate.inputs.values()):
                if input.val == -1:
                    solving_queue.append(current_gate)
                    will_continue = True
                    break
            if will_continue:
                continue
            current_gate.calc()
        list(map(print, self.elements.values()))
        self.update_graphic(event=None)

    def gen_truth_table(self) -> None:
        inputs = [element for element in list(self.elements.values()) if isinstance(element, Pin) and not element.in_gate and element.type_ == "output" and len(element.connexions) > 0]
        outputs = [element for element in list(self.elements.values()) if isinstance(element, Pin) and not element.in_gate and element.type_ == "input" and len(element.connexions) > 0]
        input_combinations = itertools.product([0, 1], repeat=len(inputs))

        for combination in list(input_combinations):
            for input, val in zip(inputs, combination):
                input.val = val
            self.solve()
            self.truth_table.append(list(combination)+[output.val for output in outputs])

        table = tk.Tk()
        table.title("Circuit Truth Table")
        tt_ui = ttk.Treeview(table, show="headings")
        columns = []
        for pin in inputs + outputs: # should ensure that output are at the end of the truth table
            header = "input" + str(pin.order) if pin.type_ == "output" else "output" + str(pin.order) #  circuit input are equivalent to gate output and vice versa
            columns.append(header)
        tt_ui.configure(columns=tuple(columns))
        for pin in inputs + outputs:
            header = "input" + str(pin.order) if pin.type_ == "output" else "output" + str(pin.order) #  circuit input are equivalent to gate output and vice versa
            tt_ui.heading(header, text=header)
        for n in range(len(self.truth_table)):
            tt_ui.insert(parent="", index=n, values=tuple(self.truth_table[n]))
        tt_ui.pack(expand=True, fill=tk.BOTH)
        tt_ui.pack_propagate(False)
        tt_ui.delete()

    def save(self):
        if len(self.truth_table) > 0:
            circuit_name = tkinter.simpledialog.askstring("Input", "Enter the name of your circuit:")
            if circuit_name:
                file_path = os.path.join("circuits", f"{circuit_name}.csv")
                
                with open(file_path, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    header = ["input:"+str(element.order) for element in self.elements.values() if isinstance(element, Pin) and not element.in_gate and element.type_ == "output"] + ["output:"+str(element.order) for element in self.elements.values() if isinstance(element, Pin) and not element.in_gate and element.type_ == "input"]
                    pp.pprint(header)
                    writer.writerow(header)
                    writer.writerows(self.truth_table)
                print(f"circuit saved in {file_path}")

    def reset(self):
        # map(self.c.delete, list(map(self.c.find_withtag, self.elements.keys())))
        # self.c.update()
        self.c.delete("all")
        self.c.update_grid()
        self.elements = {}
        self.truth_table = []

    # graphics handling function
    def add_gate(self, circuit_name: str, pos: Point) -> None:
        path = f"circuits/{circuit_name}.csv"
        with open(path, "r") as circuit_csv:
            csv_reader = csv.reader(circuit_csv)
            pins = [n for n in next(csv_reader) if len(n) > 0]# headers io type and name # slop to erase empty list
            truth_table = [n for n in list(csv_reader) if len(n) > 0]
        gate_inputs = {}
        gate_outputs = {}
        inputs = [pin for pin in pins if pin.split(":")[0] == "input"]
        outputs = [pin for pin in pins if pin.split(":")[0] == "output"]
        gate_size = 50 #15 + len(inputs) * 15
        gate_w = int(gate_size * self.c.factor**self.c.zoom_level)
        gate_h = int(gate_w // 1.2)
        pin_size = int(7 * self.c.factor**self.c.zoom_level)
        y_offset = int(10 * self.c.factor**self.c.zoom_level)
        y_pin_offset = int(3 * self.c.factor**self.c.zoom_level)
        # this is BS
        for n in range(len(inputs)):
            x = 0 - pin_size
            y = (gate_h // 2) - y_pin_offset if len(inputs) == 1 else (y_offset + (gate_h - (y_offset*2)) // (len(inputs) - 1) * n) - y_pin_offset
            new_pin = Pin(self.c, "input", n, Point(pos.x, pos.y), in_gate=True, relative_pos=Point(x, y))
            self.elements[new_pin.tag] = new_pin
            gate_inputs[new_pin.tag] = new_pin

        for n in range(len(outputs)):
            x = gate_w
            y = gate_h // 2 - y_pin_offset if len(outputs) == 1 else y_offset + (gate_h // (y_offset*2)) // (len(outputs) - 1) * n - y_pin_offset
            new_pin = Pin(self.c, "output", n, Point(pos.x, pos.y), in_gate=True, relative_pos=Point(x, y))
            self.elements[new_pin.tag] = new_pin
            gate_outputs[new_pin.tag] = new_pin

        new_gate = Gate(self.c, Point(pos.x, pos.y), tt=truth_table, inputs=gate_inputs, outputs=gate_outputs, name=circuit_name)
        self.elements[new_gate.tag] = new_gate
        new_gate.draw()

    def del_gate_connexion(self, gate: Gate) -> None:
        for pin in list(gate.inputs.values())+list(gate.outputs.values()):
            pin.delete_all_connexion()
        self.update_graphic(event=None)

    def del_gate(self, gate: Gate) -> None:
        # need polishing
        tags = []
        for pin in list(gate.inputs.values())+list(gate.outputs.values()):
            pin.delete_all_connexion()
            del self.elements[pin.tag]
            tags.append(pin.tag)
        del self.elements[gate.tag]
        tags.append(gate.tag)
        for tag in tags:
            self.c.delete(tag)
        self.update_graphic(event=None)

    def add_io(self, type_: str, pos: Point) -> None:
        if type_ == "input":
            new_pin = Pin(self.c, 
                          "input",
                          len([pin for pin in self.elements.values() if isinstance(pin, Pin) and pin.in_gate == False and pin.type_ == "input"]),
                          Point(pos.x, pos.y))
            new_pin.draw()
            self.elements[new_pin.tag] = new_pin
        else:
            new_pin = Pin(self.c, 
                          "output",
                          len([pin for pin in self.elements.values() if isinstance(pin, Pin) and pin.in_gate == False and pin.type_ == "output"]), 
                          Point(pos.x, pos.y))
            new_pin.draw()
            self.elements[new_pin.tag] = new_pin

    def del_io(self, pin: Pin) -> None:
        pass

    def update_available_circuits(self):
        path = Path("./circuits")
        self.availabe_circuits = [f.name.split(".")[0] for f in path.iterdir() if f.is_file()]

    # used for the zoom event in the circuit designer object
    def update_graphic(self, event):
        for element in self.elements.values():
            element.update_graphic(event=event)
            element.draw()

    # event handling functions 
    # select element of the circuit by clicking on it
    def select_element(self, event) -> None:
        if event.num == 1:
            selected_element = self.c.gettags(self.c.find_withtag("current")[0])[0]
            if selected_element == "grid":
                return
            try:
                selected_element = self.elements[self.c.gettags(self.c.find_withtag("current")[0])[0]]  
                if isinstance(selected_element, Pin) or isinstance(selected_element, Gate):
                    # put element and coord of the mouse in the canvas at the moment of selection in drag_data
                    self.drag_data["object"] = selected_element
                    a, b, c, d = self.c.bbox(selected_element.tag)
                    self.drag_data["x"] = self.c.canvasx(event.x)
                    self.drag_data["y"] = self.c.canvasy(event.y)
            except KeyError as key:
                print(f"object with key {key} not part of circuit")
        elif event.num == 2:
            
            selected_element = self.c.gettags(self.c.find_withtag("current")[0])[0]
            if selected_element == "grid":
                self.show_context_menu(event)
            try:
                selected_element = self.elements[self.c.gettags(self.c.find_withtag("current")[0])[0]]  
                if isinstance(selected_element, Gate):
                    self.drag_data["object"] = selected_element
                    self.show_gate_context_menu(event)
                elif isinstance(selected_element, Pin):
                    self.drag_data["object"] = selected_element
            except KeyError as key:
                print(f"object with key {key} not part of circuit")

    # move selected object with mouse
    def drag_element_B1(self, event) -> None:
        # if selected element is a pin of type output the drag motion will cause a connexion to be displayed if the release of 
        # the motion happens on another pin of type input the connexion will be set
        obj = self.drag_data["object"] 
        dx = self.c.canvasx(event.x) - self.drag_data["x"]
        dy = self.c.canvasy(event.y) - self.drag_data["y"]
        if obj == "grid":
            return 
        if isinstance(obj, Pin):
            if not obj.in_gate:
                a, b, c, d = self.c.bbox(obj.tag)
                obj.update_graphic(pos=Point(a + dx + 1, b + dy + 1))
        elif isinstance(obj, Gate):
            a, b, c, d = self.c.bbox(obj.tag)
            if obj.name == "AND":
                correction = 3 + (self.c.zoom_level if self.c.zoom_level > 0 else 0)
            elif obj.name == "OR": 
                correction = 2 + (1 if self.c.zoom_level > 0 else 0)
            elif obj.name == "NOT":
                correction = 3 + (self.c.zoom_level if self.c.zoom_level > 0 else 0)
            else:
                correction = 1
            obj.update_graphic(pos=Point(a + dx + correction, b + dy + correction))
            print(f"pos: x:{obj.pos.x}, y:{obj.pos.y}")
            print(f"a:{a}, b:{b}, dx:{dx}, dy:{dy}")
        else:
            return
        self.drag_data["x"] = self.c.canvasx(event.x)
        self.drag_data["y"] = self.c.canvasy(event.y)

    def drag_element_B2(self, event) -> None:
        # if selected element is a pin of type output the drag motion will cause a connexion to be displayed if the release of 
        # the motion happens on another pin of type input the connexion will be set
        obj = self.drag_data["object"] 
        if obj == "grid":
            return 
        if isinstance(obj, Pin):
            if obj.type_ == "output":
                obj.draw_connexion(event=event)
        else:
            return

    def unselect_element(self, event) -> None:
        obj = self.drag_data["object"] 
        if obj == "grid":
            self.drag_data["x"] = 0
            self.drag_data["y"] = 0
            self.drag_data["object"] = None
            return 
        if isinstance(obj, Gate):
            obj.draw()
            a, b, c, d = self.c.bbox(obj.tag)
            self.c.delete(obj.tag)
            obj.update_graphic(pos=Point(a, b))
        if isinstance(obj, Pin):
            obj.draw()
            if obj.type_ == "output":
                for element in self.elements.values():
                    if isinstance(element, Pin):
                        if element.type_ == "input":
                            a, b, c, d = self.c.bbox(element.tag)
                            if self.c.canvasx(event.x) > a and self.c.canvasx(event.x) < c and self.c.canvasy(event.y) > b and self.c.canvasy(event.y) < d:
                                obj.add_connexion(element)
                                element.add_connexion(obj)
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0
        self.drag_data["object"] = None

    def show_context_menu(self, event: tk.Event):
        # serve as a reset of other events too
        self.drag_data["object"] = 0
        self.motion_draw = False
        self.context_menu.delete(0, tk.END)
        self.update_available_circuits()
        self.context_menu.add_command(label="add circuit IN", command=lambda : self.add_io("output", Point(self.c.canvasx(event.x), self.c.canvasy(event.y))))
        self.context_menu.add_command(label="add circuit OUT", command=lambda : self.add_io("input", Point(self.c.canvasx(event.x), self.c.canvasy(event.y))))
        for circuit in self.availabe_circuits:
            self.context_menu.add_command(label="add "+circuit, command=lambda circuit=circuit: self.add_gate(circuit, Point(self.c.canvasx(event.x), self.c.canvasy(event.y))))

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def show_gate_context_menu(self, event: tk.Event):
        self.gate_context_menu.delete(0, tk.END)
        if isinstance(self.drag_data["object"], Gate):
            self.gate_context_menu.add_command(label="truth table", command=self.drag_data["object"].display_tt)
            self.gate_context_menu.add_command(label="delete connexions", command=lambda : self.del_gate_connexion(self.drag_data["object"]))
            #self.gate_context_menu.add_command(label="delete", command=lambda : self.del_gate(self.drag_data["object"])) # buggy

        try:
            self.gate_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.gate_context_menu.grab_release()





















