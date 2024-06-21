import tkinter as tk
from tkinter import ttk


BG_COLOR: str = "#FFFFFF"
BG_COLOR_DM: str = "#6C6C6C"
GRID_COLOR: str = "#B6B6B6"
MIN_GRID_S: int = 100
MAX_GRID_S: int = 100


# defining the main app window
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Digital Logic Simulator")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.update_idletasks()


# defingin a canvas widget where the circuit building will take place
# the grid determines the scrollable region
class CircuitDesigner(tk.Canvas):
    def __init__(self, parent: App) -> None:
        super().__init__(parent, 
                         bg=BG_COLOR, 
                         height=parent.winfo_height(), 
                         width=parent.winfo_width(), 
                         scrollregion=(0, 0, parent.winfo_width(), parent.winfo_height()))
        self.parent = parent
        # defining scrollable region starting at min zoom size
        self._grid_size: int = MIN_GRID_S
        self.width: int = parent.winfo_width()//self._grid_size + 1  # added ones repr red barrier
        self.height: int = parent.winfo_height()//self._grid_size + 1
        self.ratio: float = self.width / self.height
        self.n_grid: int = self.width * self.height  # max number of grid in the canvas total 
        self.factor = 1.5
        self.zoom_level: int = 0
        self.is_gridded: bool = True
        self.theme: str = BG_COLOR
        self.update_grid()  # add grid

        self.circuit = None  # adding a circuit to design area for connecting zoom functionality to circuit element

        # events
        # pan functionality
        def fun(event):
            self.delete("tes")
            self.create_rectangle((event.x, event.y, event.x+100, event.y+100), fill="red", outline="black", tags=("tes"))
            # print("screen coord")
            # print(f"X:{event.x}Y:{event.y}")
            # print("canvas coord")
            # print(f"X:{self.canvasx(event.x)}Y:{self.canvasy(event.y)}")
            # print("input")
            # if self.circuit is not None:
            #     print(f"X:{self.circuit.io[0].pos.x}Y:{self.circuit.io[0].pos.y}")

        self.tag_bind("red", "<B3-Motion>", fun)
        self.tag_bind("grid", "<ButtonPress-1>", lambda event: self.scan_mark(event.x, event.y))
        self.tag_bind("grid", "<B1-Motion>", lambda event: self.scan_dragto(event.x, event.y, gain=1))
        # zoom functionality
        self.bind("<MouseWheel>", self.zoom)

    # change theme and make the grid same or different color as background
    def update_grid(self) -> None:
        self.delete("grid")
        self.delete("barrier")
        if self.is_gridded:
            grid_color: str = GRID_COLOR
        else:
            grid_color: str = self.theme
        for m in range(self.height):
            for n in range(self.width):
                if n == 0 or n == self.width - 1 or m == self.height - 1 or m == 0:
                    self.create_rectangle(
                        0 + n*self._grid_size, 
                        0 + m*self._grid_size,
                        self._grid_size + n*self._grid_size,
                        self._grid_size + m*self._grid_size,
                        fill="black",
                        outline="black",
                        tags=("barrier"))
                else:
                    self.create_rectangle(
                        0 + n*self._grid_size, 
                        0 + m*self._grid_size,
                        self._grid_size + n*self._grid_size,
                        self._grid_size + m*self._grid_size,
                        fill=self.theme,
                        outline=grid_color,
                        tags=("grid"))
        self.tag_lower("grid", "all")  # give precedence to all items that dont have the "grid" tag

    # the number of grid never change only the visible amount
    def zoom(self, event: tk.Event) -> None:
        #gain: int = self._grid_size  # how much does a grid element grow by call
        # choose zoom level based on scroll wheel
        if event.delta > 0:
            if self.zoom_level < 2:
                self.zoom_level += 1
                self._grid_size = int(MIN_GRID_S * self.factor**self.zoom_level)
                if self.circuit is not None:
                    self.circuit.update_graphic(event=event)
        else:
            if self.zoom_level > 0:
                self.zoom_level -= 1
                self._grid_size = int(MIN_GRID_S * self.factor**self.zoom_level)
                if self.circuit is not None:
                    self.circuit.update_graphic(event=event)

        self.update_grid() #  update grid size

        # canvas only grow to the right and bottom to avoid neg coords
        self.configure(scrollregion=(self.width*self._grid_size - self.parent.winfo_width(),
                                     self.height*self._grid_size - self.parent.winfo_height(),
                                     self.parent.winfo_width(),
                                     self.parent.winfo_height()))  


        # recenter view to middle
        # self.xview_moveto(1 - self.width * gain * self.zoom_level / 2 / (self.width*gain*self.zoom_level+self.parent.winfo_width()))
        #self.xview(self.xview_moveto(1 - self.width * gain * self.zoom_level / 2 / (self.width*gain*self.zoom_level+self.parent.winfo_width())))
        # self.xview_scroll(, "pixels")
        # print(self.xview())

    def set_circuit(self, circuit):
        self.circuit = circuit


class Menu(tk.Frame):
    def __init__(self, parent: App, circuit, gui: CircuitDesigner) -> None:
        super().__init__(parent,
                         bg="darkgrey",
                         height=100)

        self.pack(side="top",fill="x")

        run_button = ttk.Button(self, text="RUN", command=circuit.solve)
        run_button.pack(side="left", padx=5, pady=5)

        tt_button = ttk.Button(self, text="TRUTH TABLE", command=circuit.gen_truth_table)
        tt_button.pack(side="left", padx=5, pady=5)

        save_button = ttk.Button(self, text="SAVE", command=circuit.save)
        save_button.pack(side="left", padx=5, pady=5)

        reset_button = ttk.Button(self, text="RESET", command=circuit.reset)
        reset_button.pack(side="left", padx=5, pady=5)

        view_button = ttk.Menubutton(self, text="VIEW")
        view_button.pack(side="left", padx=10, pady=5)

        is_dark = tk.BooleanVar(value=False)
        is_grid = tk.BooleanVar(value=True)
        def darken():
            if is_dark.get():
                gui.theme = BG_COLOR_DM
            else:
                gui.theme = BG_COLOR
            gui.update_grid()
        def grid():
            if is_grid.get():
                gui.is_gridded = True
            else:
                gui.is_gridded = False
            gui.update_grid()
        view_sub_menu = tk.Menu(view_button, tearoff=False)
        view_sub_menu.add_checkbutton(label="Dark Mode", variable=is_dark, command=darken)
        view_sub_menu.add_checkbutton(label="Grid", variable=is_grid, command=grid)
        view_button["menu"] = view_sub_menu



def main() -> None:
    from circuit import Circuit
    from gate import Gate
    from point import Point
    app = App()
    app_canva = CircuitDesigner(app)
    circuit: Circuit = Circuit(app_canva)
    menu = Menu(app, circuit, app_canva)
    app_canva.pack(side="top", fill="both")
    app_canva.set_circuit(circuit)

    app.mainloop()

if __name__ == "__main__":
    main()
