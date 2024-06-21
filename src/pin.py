from gate import Gate
from point import Point, Line
import tkinter as tk
from tkinter import ttk
import uuid
from main import CircuitDesigner


# i/0 pin can be on a gate or free standing in the circuit
class Pin():
    def __init__(self, canvas, type_, order, pos, in_gate=False, relative_pos=None) -> None:
        # Logical representation
        if type_ != "input" and type_ != "output":
            raise ValueError("pin objects can only be initialized by type input, output")
        self.type_ = type_  
        self.order = order
        self.in_gate = in_gate
        self.val: int = -1 if not in_gate else 0
        self.connexions: list["Pin"] = []  # out can have many in only one

        # Graphical representation
        # tkinter property
        self.c: CircuitDesigner = canvas
        self.tag: str = str(uuid.uuid4())
        # graphics
        self.pos = Point(int(pos.x), int(pos.y))
        self.relative_pos = Point(int(relative_pos.x), int(relative_pos.y)) if relative_pos is not None else Point(0, 0)
        self.size: int = int(14 * canvas.factor**canvas.zoom_level) if not self.in_gate else int(7 * canvas.factor**canvas.zoom_level)
        self.font_size = int(15 * canvas.factor**canvas.zoom_level)
        self.connexion_width = int(2 * canvas.factor**canvas.zoom_level)

    # Functions for Logical Representation 
    def propagate(self):
        for connexion in self.connexions:
            connexion.val = self.val
    def update_value(self, val: int) -> None:
        self.val = val
        # propagate
        if self.type_ == "output":
            for input in self.connexions:
                input.update_value(self.val)

    def add_connexion(self, connexion: "Pin") -> None:
        self.connexions.append(connexion)
        self.draw()

    def delete_connexion(self, connexion: "Pin") -> None:
        if self.type_ == "output":
            self.connexions.remove(connexion)
            connexion.connexions.remove(self)
        else:
            connexion.delete_connexion(self)
        self.draw()
    
    def delete_all_connexion(self):
        for connexion in self.connexions:
            self.delete_connexion(connexion)
        self.draw()

    def update_graphic(self, event=None, pos=None) -> None:
        self.c.delete(self.tag+"connexionset")
        for pin in self.connexions:
            self.c.delete(pin.tag+"connexionset")
        if isinstance(pos, Point):
            self.pos = Point(pos.x,pos.y)
        if isinstance(event, tk.Event):
            origin_size = 7 if self.in_gate else 14
            self.size = int(origin_size * self.c.factor ** self.c.zoom_level)
            self.font_size = int(15 * self.c.factor**self.c.zoom_level)
            if event.delta > 0:
                self.pos.x = int(self.pos.x * self.c.factor)
                self.pos.y = int(self.pos.y * self.c.factor)

                self.relative_pos.x = int(self.relative_pos.x * self.c.factor)
                self.relative_pos.y = int(self.relative_pos.y * self.c.factor)
            else:
                self.pos.x //= self.c.factor 
                self.pos.y //= self.c.factor 
                self.relative_pos.x = int(self.relative_pos.x // self.c.factor)
                self.relative_pos.y = int(self.relative_pos.y // self.c.factor)
        self.draw()

    def draw(self) -> None: #  draws depending if its and in or out and if its free or bound to a gate
        self.c.delete(self.tag)  # removes old pin graphics
        self.c.delete(self.tag+"button")  # removes old pin graphics
        self.draw_connexion()
        if not self.in_gate:
            if self.type_ == "input":
                color = "red"
            else:
                color = "green"
            self.c.create_rectangle(self.pos.x, 
                                    self.pos.y,
                                    self.pos.x + self.size,
                                    self.pos.y + self.size,
                                    fill=color,
                                    outline="black",
                                    tags=(self.tag, "circuit", self.type_))
            def button_fun():
                if value.get() == "0":
                    self.val = 1
                    value.set(str(self.val))
                else:
                    self.val = 0
                    value.set(str(self.val))

            value = tk.StringVar(value=str(self.val))
            button = tk.Button(self.c.parent, text="0", font=("purisa", self.font_size), disabledforeground="black", textvariable=value, command=button_fun, state="active" if self.type_ == "output" else "disabled")
            x = self.pos.x - self.size - 5 if self.type_ == "output" else self.pos.x + self.size*3
            self.c.create_window(x,
                                 self.pos.y,
                                 window=button, 
                                 tags=(self.tag+"button"))
        else:
            if self.type_ == "input":
                color = "green"
            else:
                color = "red"
            self.c.create_rectangle(self.pos.x + self.relative_pos.x,
                                    self.pos.y + self.relative_pos.y,
                                    self.pos.x + self.relative_pos.x + self.size,
                                    self.pos.y + self.relative_pos.y + self.size,
                                    fill=color,
                                    outline="black",
                                    tags=(self.tag, "gate", self.type_))

    def draw_connexion(self, event=None):
        import tkinter as tk
        self.c.delete(self.tag+"connexion")  # removes old pin graphics
        if isinstance(event, tk.Event):
            dx = self.c.canvasx(event.x) - (self.pos.x+self.relative_pos.x) 
            dy = self.c.canvasy(event.y) - (self.pos.y+self.relative_pos.y)
            self.c.create_line(self.pos.x + self.relative_pos.x,
                               self.pos.y + self.relative_pos.y,
                               self.pos.x + self.relative_pos.x + dx//2,
                               self.pos.y + self.relative_pos.y,
                               fill="black",
                               width=self.connexion_width,
                               tags=(self.tag+"connexion"))
            self.c.create_line(self.pos.x + self.relative_pos.x + (dx//2),
                               self.pos.y + self.relative_pos.y,
                               self.pos.x + self.relative_pos.x + dx//2,
                               self.pos.y + self.relative_pos.y + dy,
                               fill="black",
                               width=self.connexion_width,
                               tags=(self.tag+"connexion"))
            self.c.create_line(self.pos.x + self.relative_pos.x + dx//2,
                               self.pos.y + self.relative_pos.y + dy,
                               self.pos.x + self.relative_pos.x + dx,
                               self.pos.y + self.relative_pos.y + dy,
                               fill="black",
                               width=self.connexion_width,
                               tags=(self.tag+"connexion"))
            
        else:
            if self.type_ == "output":
                for connexion in self.connexions:
                    dx = (connexion.pos.x+connexion.relative_pos.x) - (self.pos.x+self.relative_pos.x)
                    dy = (connexion.pos.y+connexion.relative_pos.y) - (self.pos.y+self.relative_pos.y)
                    self.c.create_line(self.pos.x + self.relative_pos.x,
                                       self.pos.y + self.relative_pos.y,
                                       self.pos.x + self.relative_pos.x + dx//2,
                                       self.pos.y + self.relative_pos.y,
                                       fill="black",
                                       width=self.connexion_width,
                                       tags=(self.tag+"connexionset"))
                    self.c.create_line(self.pos.x + self.relative_pos.x + dx//2,
                                       self.pos.y + self.relative_pos.y,
                                       self.pos.x + self.relative_pos.x + dx//2,
                                       self.pos.y + self.relative_pos.y + dy,
                                       fill="black",
                                       width=self.connexion_width,
                                       tags=(self.tag+"connexionset"))
                    self.c.create_line(self.pos.x + self.relative_pos.x + dx//2,
                                       self.pos.y + self.relative_pos.y + dy,
                                       self.pos.x + self.relative_pos.x + dx,
                                       self.pos.y + self.relative_pos.y + dy,
                                       fill="black",
                                       width=self.connexion_width,
                                       tags=(self.tag+"connexionset"))
            elif self.type_ == "input":
                for output in self.connexions:
                    output.draw()
                    # output.draw_connexion()

    def __repr__(self):
        return f"in gate:{self.in_gate}, pin:{self.type_}{self.order}, val:{self.val}"
        # return f"pin:{self.type_}{self.order}\nin gate?{self.in_gate}\nconnexions:{print(self.connexions)}"




