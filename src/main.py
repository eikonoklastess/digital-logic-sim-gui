from gui import And_Gate, Circuit, Gui, Gate, Or_Gate, Not_Gate, Point

def main():
    gui = Gui(1080, 1080)
    canvas = gui.canvas
    # conec = Connection(gui)
    gate = Or_Gate(Point(300, 300), canvas)
    gate2 = And_Gate(Point(500, 300), canvas)
    gate3 = Not_Gate(Point(700, 300), canvas)
    # gate4 = Or_Gate(20, 20, gui)
    # gate5 = Not_Gate(700, 700, gui)
    # gate6 = And_Gate(500, 700, gui)
    circuit = Circuit(canvas)
    circuit.add_gate(gate)
    circuit.add_gate(gate2)
    circuit.add_gate(gate3)
    # circuit.add_gate(gate4)
    # circuit.add_gate(gate5)
    # circuit.add_gate(gate6)
    circuit.draw()
    gui.wait_for_close()


main()
