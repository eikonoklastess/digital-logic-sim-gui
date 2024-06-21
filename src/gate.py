from os import posix_spawn, walk
import tkinter as tk
from tkinter import ttk
import uuid
from point import Point
from mainbis import CircuitDesigner
import pprint as pp


# if a gate object is created without option its created as a repeater gate that only propagate its input value
class Gate():
    def __init__(self, canvas: CircuitDesigner, pos, tt=None, inputs=None, outputs=None, name=None):
        from pinbis import Pin
        # Logical Representation
        self.tt: list[list] = tt if tt is not None else []  # tt for truth table
        if inputs is None and outputs is None:
            new_input = Pin(canvas, "input", 0, pos, relative_pos=Point(self.h // 2, 0)) 
            new_output = Pin(canvas, "output", 0, pos, relative_pos=Point(self.h // 2, self.w))
            self.inputs: dict = {new_input.tag : new_input}
            self.outputs: dict = {new_output.tag : new_output}
        else:
            self.inputs: dict = inputs if isinstance(inputs, dict) else {}
            self.outputs: dict = outputs if isinstance(outputs, dict) else {}

        # graphical representation
        # tkinter proprety
        self.c: CircuitDesigner = canvas
        self.tag = str(uuid.uuid4())
        # graphics
        self.name = name if name is not None else "repeater"
        self.pos: Point = Point(int(pos.x), int(pos.y))
        self.font_size = 10 * canvas.factor**canvas.zoom_level
        # size in proportion to number of input
        self.size = 50 #15 + len(self.inputs) * 15
        self.h = int(self.size // 1.2 * canvas.factor**canvas.zoom_level) if tt is not None else 50 * canvas.factor**canvas.zoom_level
        self.w = int(self.size * canvas.factor**canvas.zoom_level) if tt is not None else 50 * canvas.factor**canvas.zoom_level
        self.width = int(2 * canvas.factor**canvas.zoom_level) # width of drawings

    def display_tt(self):
        inputs = list(self.inputs.values())
        outputs = list(self.outputs.values())
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
        for n in range(len(self.tt)):
            tt_ui.insert(parent="", index=n, values=tuple(self.tt[n]))
        tt_ui.pack(expand=True, fill=tk.BOTH)
        tt_ui.pack_propagate(False)
        # tt_ui.delete(*tt_ui.get_children())

    # functions for logic
    def calc(self):
        if len(self.tt) == 0:
            list(self.outputs.values())[0].update_val(list(self.inputs.values())[0].val)
        else:
            inputs_configuration = [pin.val for pin in list(self.inputs.values()) if pin.type_ == "input"]
            for n in self.tt:
                split_index = len(inputs_configuration) #if len(inputs_configuration) > 1 else 1
                tt_inputs = n[:split_index]
                tt_outputs = n[split_index:]
                if inputs_configuration == [int(n) for n in tt_inputs]:
                    # only works with one input
                    list(self.outputs.values())[0].update_value(int(tt_outputs[0]))

    # functions for graphics
    def update_graphic(self, event=None, pos=None):
        from pinbis import Pin
        if isinstance(pos, Point):
            self.pos = Point(pos.x, pos.y)
            for input in self.inputs.values():
                input.update_graphic(pos=Point(pos.x, pos.y), event=event)
            for output in self.outputs.values():
                output.update_graphic(pos=Point(pos.x, pos.y), event=event)
        elif isinstance(event, tk.Event):
            if event.delta > 0:
                self.pos.x = int(self.pos.x * self.c.factor)
                self.pos.y = int(self.pos.y * self.c.factor)
            else:
                self.pos.x //= self.c.factor 
                self.pos.y //= self.c.factor 
            self.width = int(2 * self.c.factor ** self.c.zoom_level)
            self.h = int(self.size // 1.2 * self.c.factor ** self.c.zoom_level)
            self.w = int(self.size * self.c.factor ** self.c.zoom_level)
            self.font_size = int(10 * self.c.factor ** self.c.zoom_level)
        for pin in (list(self.inputs.values())+list(self.outputs.values())):
            if isinstance(pin, Pin):
                pin.update_graphic()
        self.draw()

    def draw(self):
        self.c.delete(self.tag)
        if not self.draw_helper():
            self.c.create_rectangle(self.pos.x,
                                    self.pos.y,
                                    self.pos.x + self.w,
                                    self.pos.y + self.h,
                                    fill="white",
                                    outline="black",
                                    tags=(self.tag, "gate proper", "gate", "element"))
            text_pos_x = self.pos.x + self.w//2
            text_pos_y = self.pos.y + self.h//2
            self.c.create_text(text_pos_x,
                               text_pos_y,
                               text=self.name,
                               fill="black",
                               width=self.w,
                               font=("purisa", int(self.font_size)),
                               tags=(self.tag, "gate", "gate proper", "element"))
        for input in self.inputs.values():
            input.draw()
        for output in self.outputs.values():
            output.draw()

    def __repr__(self):
        return f"gate:{self.name}" #\ntt:{self.tt}\ninputs:{self.inputs}\noutputs:{self.outputs}"

    def draw_helper(self):
        if self.name == "AND":
            self.c.create_line(self.pos.x,
                               self.pos.y,
                               self.pos.x + self.w//2 ,#- (self.w // (2 * self.c.factor**self.c.zoom_level)), 
                               self.pos.y, 
                               fill="black", width=self.width,
                               tags=(self.tag, "gate", "element"))
            self.c.create_line(self.pos.x,
                               self.pos.y + self.h, 
                               self.pos.x + self.w//2 ,#- (self.w // (2 * self.c.factor**self.c.zoom_level)), 
                               self.pos.y + self.h, 
                               fill="black", width=self.width, 
                               tags=(self.tag, "gate", "element"))
            self.c.create_line(self.pos.x, 
                               self.pos.y, 
                               self.pos.x, 
                               self.pos.y + self.h, 
                               fill="black", width=self.width, 
                               tags=(self.tag, "gate", "element"))
            self.c.create_arc(self.pos.x, 
                              self.pos.y, 
                              self.pos.x + self.w ,
                              self.pos.y + self.h, 
                              outline="black", 
                              width=self.width,
                              extent=180, 
                              start=270, style=tk.ARC, tags=(self.tag, "gate", "element"))
            self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x + self.w, self.pos.y + self.h, fill="", outline="", tags=(self.tag, "element", "gate"))

            return True
        elif self.name == "OR":
            self.c.create_arc(self.pos.x - self.w ,#// (6 * self.c.factor**self.c.zoom_level)),
                              self.pos.y, 
                              self.pos.x + self.w ,#// (6 * self.c.factor**self.c.zoom_level)),
                              self.pos.y + self.h, 
                              outline="black", 
                              width=self.width,
                              extent=180, start=270, style=tk.ARC,
                              tags=(self.tag, "gate", "element"))
            self.c.create_arc(self.pos.x - self.w // 6,# * self.c.factor**self.c.zoom_level)), 
                              self.pos.y, 
                              self.pos.x + self.w // 6,# * self.c.factor**self.c.zoom_level)), 
                              self.pos.y + self.h, 
                              outline="black", 
                              width=self.width,
                              extent=180, start=270, style=tk.ARC, 
                              tags=(self.tag, "gate", "element"))
            self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x + self.w, self.pos.y + self.h, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate", "element"))

            return True
        elif self.name == "NOT":
            self.c.create_line(self.pos.x,
                               self.pos.y, 
                               self.pos.x + self.w, 
                               self.pos.y + (self.h // 2), 
                               fill="black", width=self.width, tags=(self.tag, "gate", "element"))
            self.c.create_line(self.pos.x, 
                               self.pos.y + self.h, 
                               self.pos.x + self.w, 
                               self.pos.y + (self.h // 2), 
                               fill="black", width=self.width, tags=(self.tag, "gate", "element"))
            self.c.create_line(self.pos.x, 
                               self.pos.y, 
                               self.pos.x,
                               self.pos.y + self.h, 
                               fill="black", width=self.width, tags=(self.tag, "gate", "element"))
            # self.c.create_oval(self.pos.x + self.w - 2 * self.c.factor**self.c.zoom_level,
            #                    self.pos.y + self.h // 2 - (2 * self.c.factor**self.c.zoom_level),
            #                    self.pos.x + self.w + 2 * self.c.factor**self.c.zoom_level,
            #                    self.pos.y + self.h // 2 - (2 * self.c.factor**self.c.zoom_level),
            #                    fill="black", width=self.width, tags=(self.tag, "gate", "element"))

            self.c.create_rectangle(self.pos.x, self.pos.y, self.pos.x + self.w, self.pos.y + self.h, fill="", outline="", tags=(self.tag, "gate_catching_area", "gate", "element"))

            return True
        return False













