import uuid
from collections import deque
from pin import Input, Output
from gate import And_Gate, Circuit_Input, Circuit_Output, Gate, Or_Gate, Not_Gate
import tkinter as tk
from tkinter import BOTH, Canvas, Scrollbar, Widget, ttk
import tkinter.simpledialog
from tkinter.simpledialog import askstring
import pprint, itertools, csv, os

# style = ttk.Style()
# style.theme_use("alt")
# style.configure("Treeview",
#                 background="#d3d3d3",
#                 foreground="black",
#                 rowheight=25,
#                 fieldbackground="#d3d3d3")
# style.map("Treeview",
#           background=[("selected", "#d3d3d3")],
#           foreground=[("selected", "white")])
# style.configure("Treeview.Heading",
#                 font=("Arial", 18, "bold"),
#                 background="#007bff",
#                 foreground="white")
#
def _zoom_in(c, event):
    c.scale("all", event.x, event.y, 1.1, 1.1)
    c.configure(scrollregion=c.bbox("all"))

def _zoom_out(c, event):
    c.scale("all", event.x, event.y, 1/1.1, 1/1.1)
    c.configure(scrollregion=c.bbox("all"))

def _on_mousewheel(c, event):
        if event.delta > 0:
            _zoom_in(c, event)
        elif event.delta < 0:
            _zoom_out(c,event)

window = tk.Tk()
window.title("Digital Logic GUI")
window.geometry("1920x1080")

c = Canvas(window, height=1060, width=1480, bg="#f5f5dc")

y_scroll = ttk.Scrollbar(window, orient="vertical", command=c.yview)
y_scroll.grid(row=0, column=2, sticky="ns")
x_scroll = ttk.Scrollbar(window, orient="horizontal", command=c.xview)
x_scroll.grid(row=1, column=1, sticky="ew")
c.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
c.grid(row=0, column=1)
c.configure(scrollregion=(0, 0, 2060, 2480))

c.bind("<ButtonPress-1>", lambda event: c.scan_mark(event.x, event.y))
c.bind("<B1-Motion>", lambda event: c.scan_dragto(event.x, event.y, gain=1))
c.bind("<MouseWheel>", lambda event: _on_mousewheel(c, event))
def motion_fun(event):
    x = c.canvasx(event.x)
    y = c.canvasy(event.y)
    print(f"x:{x}, y:{y}") 
c.bind("<Motion>", motion_fun)

# c.place(x=420, y=0)
menu = tk.Frame(window, height= 1060, width=420, bg="#c2c2c2")
menu.grid(row=0, column=0)
# menu.place(x=0, y=0)


set_circuit = ttk.Button(menu, text="TRUTH TABLE", command=lambda: circuit.set_circuit())
set_circuit.grid(row=0, column=0)
#set_circuit.place(x=20, y=10, width=380, height=40)

start_circuit = ttk.Button(menu, text="START", command=lambda: circuit.solve_circuit())
start_circuit.grid(row=1, column=0)
# start_circuit.place(x=20, y=60, width=380, height=40)

reset = ttk.Button(menu, text="RESET", command=lambda: circuit.reset())
reset.grid(row=0, column=1)
# reset.place(x=20, y=110, width=380, height=40)

save_circuit = ttk.Button(menu, text="SAVE", command=lambda: circuit.save())
save_circuit.grid(row=1, column=1)
# save_circuit.place(x=20, y=110, width=380, height=40)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

popup_menu = tk.Menu(window, tearoff=0)

def configure_menu(event, circuit, item=None):
    if item is None:
        popup_menu.delete(0, "end")
        popup_menu.add_command(label="INPUT", command=lambda: circuit.add_circuit_input(Point(int(c.canvasx(event.x)), int(c.canvasy(event.y)))))
        popup_menu.add_command(label="OUTPUT", command=lambda: circuit.add_circuit_output(Point(int(c.canvasx(event.x)), int(c.canvasy(event.y)))))
        popup_menu.add_command(label="AND Gate", command=lambda: circuit.add_and_gate(Point(int(c.canvasx(event.x)), int(c.canvasy(event.y)))))
        popup_menu.add_command(label="OR Gate", command=lambda: circuit.add_or_gate(Point(int(c.canvasx(event.x)), int(c.canvasy(event.y)))))
        popup_menu.add_command(label="NOT Gate", command=lambda: circuit.add_not_gate(Point(int(c.canvasx(event.x)), int(c.canvasy(event.y)))))
    else:
        tags = c.gettags(item)
        if "gate_catching_area" in tags:
            to_delete = None
            for gate in circuit.gates:
                if gate.tag == tags[0]:
                    to_delete = gate
            if isinstance(to_delete, Gate):
                popup_menu.add_command(label="Delete Gate", command=lambda: circuit.delete_gate(to_delete))
                popup_menu.add_command(label="Truth Table", command=lambda: to_delete.generate_truth_table())
    try:
        popup_menu.tk_popup(event.x_root, event.y_root)
    finally:
        popup_menu.grab_release()

def do_popup(event, circuit):
    item = c.find_withtag("current")
    if len(item) == 0:
        print("canvas menu")
        configure_menu(event, circuit)
        return
    popup_menu.delete(0, "end")
    print("gate menu")
    configure_menu(event, circuit, item)

#if you have to call a var from outside its probably better to bind the event in the class
c.bind("<ButtonPress-2>", lambda event: do_popup(event, circuit))


class Circuit():
    def __init__(self, canvas):
        self.c = canvas
        self.gates = []
        self.inputs = []
        self.outputs = []
        self.truth_table = None
        self.buffer = None
        self.drag_data = {"x":0, "y":0, "gate":None, "output":None, "corner": None, "connexion_number":None}
        self.c.tag_bind("gate_catching_area", "<ButtonPress-1>", self.gate_on_click)
        self.c.tag_bind("gate_catching_area", "<B1-Motion>", self.gate_on_dragbis)
        self.c.tag_bind("gate_catching_area", "<ButtonRelease-1>", self.gate_on_release)
        self.c.tag_bind("output_catching_area", "<ButtonPress-1>", self.pin_on_click)
        # self.c.tag_bind("output_catching_area", "<B1-Motion>", self.pin_on_drag)
        self.c.tag_bind("input_catching_area", "<ButtonRelease-1>", self.pin_on_release)
        self.c.tag_bind("output_catching_area", "<ButtonPress-3>", self.delete_connections)

    def save(self):
        if not os.path.exists("circuits"):
            os.makedirs("circuits")

        circuit_name = tkinter.simpledialog.askstring("Input", "Enter the name of the circuit:")
        if circuit_name:
            file_path = os.path.join("circuits", f"{circuit_name}.csv")
            
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["inputs"] + ["A", "B"])
                writer.writerow(["outputs"] + ["X"])
                writer.writerow([[0, 0, 1, 1], [0, 1, 0, 1], [0, 0, 0, 1]])
            print(f"circuit saved as {file_path}")
        
    def reset(self):
        list(map(self.c.delete, self.c.find_all()))
        self.gates = []
        self.inputs = []
        self.outputs = []
        self.truth_table = []
        self.buffer = None

    def add_gate(self, gate):
        self.gates.append(gate)

    def delete_gate(self, gate):
        gate.delete()
        self.gates.remove(gate)
        if isinstance(gate, Circuit_Input):
            print("isinstance of input")
            self.inputs.remove(gate)
        elif isinstance(gate, Circuit_Output):
            print("isinstance of output")
            self.outputs.remove(gate)

    def draw(self):
        for gate in self.gates:
            gate.draw()
        for input in self.inputs:
            input.draw()
        for output in self.outputs:
            output.draw()

    def gate_on_click(self, event):
        print("gate clicked")
        for gate in self.gates:
            tags = self.c.gettags(gate.catching_area)
            if "current" in tags:
                print("hello?")
                self.drag_data["x"] = int(self.c.canvasx(event.x))
                self.drag_data["y"] = int(self.c.canvasy(event.y))
                self.drag_data["gate"] = gate

    def gate_on_dragbis(self, event):
        if self.drag_data["gate"] is not None:
            dx = int(self.c.canvasx(event.x)) - self.drag_data["x"]
            dy = int(self.c.canvasy(event.y)) - self.drag_data["y"]
            self.c.move(self.drag_data["gate"].tag, dx, dy)
            self.drag_data["x"] = int(self.c.canvasx(event.x))
            self.drag_data["y"] = int(self.c.canvasy(event.y))
            coords = self.c.coords(self.drag_data["gate"].catching_area)
            self.drag_data["gate"].pos = Point(coords[0], coords[1])
            for input in self.drag_data["gate"].inputs:
                if input.connexion is not None:
                    output = input.connexion
                    tag = "connection"+output.tag
                    self.c.delete(tag)
                    if len(output.connections) > 0:
                        output.draw_connections()

            for output in self.drag_data["gate"].outputs:
                tag = "connection"+output.tag
                self.c.delete(tag)
                if len(output.connections) > 0:
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


    def pin_on_release(self, event):
        if self.drag_data["output"] is not None:
            tag = "connection"+self.drag_data["output"].tag
            self.c.delete(tag)
            for gate in self.gates:
                for input in gate.inputs:
                    tags = self.c.gettags(input.catching_area)
                    if "current" in tags:
                        if input.connexion is None:
                            self.drag_data["x"] = input.get_tip().x
                            self.drag_data["y"] = input.get_tip().y
                            self.drag_data["output"].add_connection(input)
                            self.drag_data["output"].draw_connections()
            self.drag_data["output"] = None

    def delete_connections(self, event):
        for gate in self.gates:
            for output in gate.outputs:
                tags = self.c.gettags(output.catching_area)
                if "current" in tags:
                    for input in output.connections:
                        input.connexion = None
                    output.connections = []
                    self.c.delete("connection"+output.tag)

    def add_and_gate(self, click_pos):
        new_gate = And_Gate(self.c, click_pos)
        self.add_gate(new_gate)
        self.draw()
        
    def add_or_gate(self, click_pos):
        new_gate = Or_Gate(self.c, click_pos)
        self.add_gate(new_gate)
        self.draw()

    def add_not_gate(self, click_pos):
        new_gate = Not_Gate(self.c, click_pos)
        self.add_gate(new_gate)
        self.draw()

    def add_circuit_input(self, click_pos):
        new_gate = Circuit_Input(self.c, click_pos)
        self.inputs.append(new_gate)
        self.add_gate(new_gate)
        self.draw()

    def add_circuit_output(self, click_pos):
        new_gate = Circuit_Output(self.c, click_pos)
        self.outputs.append(new_gate)
        self.add_gate(new_gate)
        self.draw()

    def set_circuit(self):
        self.generate_truth_table()
        table = tk.Tk()
        table.title("Truth Table")
        truth_table = ttk.Treeview(table, show="headings")
        columns = []
        for n in range(len(self.inputs)):
            header = "input"+str(n)
            columns.append(header)
        for n in range(len(self.outputs)):
            header = "output"+str(n)
            columns.append(header)
        truth_table.configure(columns=tuple(columns))
        for n in range(len(self.inputs)):
            header = "input"+str(n)
            truth_table.heading(header, text=header)
        for n in range(len(self.outputs)):
            header = "output"+str(n)
            truth_table.heading(header, text=header)

        for m in range(2**len(self.inputs)):
            value = []
            for n in range(len(self.inputs)):
                if self.truth_table is not None:
                    value.append(self.truth_table[n][m])
            for n in range(len(self.outputs)):
                n += len(self.inputs)
                if self.truth_table is not None:
                    value.append(self.truth_table[n][m])
            truth_table.insert(parent="", index=m, values=tuple(value))
        truth_table.pack(expand=True, fill=tk.BOTH)
        truth_table.pack_propagate(False)

    def solve_circuit(self):
        solving_queue = deque()
        for gate in self.gates:
            if gate not in self.inputs or gate not in self.outputs:
                print(gate)
                solving_queue.append(gate)
        for input in self.inputs:
            input.outputs[0].propagate_signal()

        while len(solving_queue) > 0:
            current_gate = solving_queue.popleft()
            will_continue = False
            for input in current_gate.inputs:
                if input.val == -1:
                    solving_queue.append(current_gate)
                    will_continue = True
                    break
            if will_continue:
                continue
            current_gate.calc_output()
            if len(current_gate.outputs) > 0:
                current_gate.outputs[0].propagate_signal()
                for input in current_gate.outputs[0].connections:
                    solving_queue.append(input.gate)
                
        # circuit_ouputs = self.c.find_withtag("circuit_output") 
        # if len(circuit_ouputs) > 0:
        #     for output in self.outputs:
        #         for circuit_out in circuit_ouputs:
        #             tags = self.c.gettags(circuit_out)
        #             if tags[0] == self.c.gettags(output.tag)[0]:
        #                 output.circuit_output["text"] = output.val
        for gate in self.gates:
            print(gate)
            
        
        self.draw()

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
            self.solve_circuit()
            self.truth_table[-1][output] = self.outputs[0].inputs[0].val
        pprint.pprint(self.truth_table)



circuit = Circuit(c)
circuit.draw()











window.mainloop()
