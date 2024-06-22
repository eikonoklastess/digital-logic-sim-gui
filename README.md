# Digital Logic Simulator

## Demo
https://github.com/eikonoklastess/digital-logic-sim-gui/assets/155257788/23009d70-146d-4e0d-a583-654bab233ba5

## Overview
This Digital Logic Simulator is a Python-based application that allows users to design, simulate, and analyze digital logic circuits. It provides a graphical interface for creating circuits with various logic gates and generating truth tables.

## Features
- Graphical circuit design interface
- Start with AND, OR and NOT gates to build your own circuits
- Custom gate creation functionality
- Interactive circuit elements (drag and drop, connections)
- Truth table generation
- Circuit state simulation
- Zoom and pan capabilities
- Dark mode option
- Save and load circuits

## Requirements
- Python 3.x
- Tkinter (usually comes pre-installed with Python)
- Make sure Tkinter and Python are on the same version
- MacOS (should be OS naive soon)
- Mouse, trackpads on macs with Tkinter are buggy

## Installing and Running the Project
1. Clone this repository: 
    ```bash
    git clone https://github.com/eikonoklastess/digital-logic-sim-gui
    ```
2. Navigate to the source file of the project directory:
    ```bash
    cd digital-logic-sim-gui/src
    ```
3. Run the main.py file:
    ```bash
    python main.py
    ```

## Usage
1. **Adding Components**: Right-click on the canvas to add gates or I/O pins.
2. **Connecting Components**: Right-click and drag from an output pin to an input pin to create connections.
3. **Moving Components**: Left-click and drag to move gates and pins.
4. **Simulating**: Click the "RUN" button to simulate the current circuit state.
5. **Truth Table**: Click "TRUTH TABLE" to generate and display the circuit's truth table.
6. **Saving/Loading**: Use the "SAVE" button to save your circuit design.
7. **Resetting**: Click "RESET" to clear the current circuit.
8. **View Options**: Use the "VIEW" menu to toggle dark mode and grid display.

## Limitation
One very big limitation of this digital logic simulator is the inability to have more than one output per gate/circuit which limit very much the usability of this simulator. Although it should not be much work to add support for this functionality as the program design was planned to have this feature. This was my first ever programming project and I did not want it to last forever.

## Contributing
Contributions to improve the Digital Logic Simulator are welcome. Please feel free to fork the repository, make changes, and submit pull requests.

