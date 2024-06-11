import uuid
class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pin():
    def __init__(self, canvas, gate, id):
        self.c = canvas
        self.gate = gate
        self.id = id
        self.val = -1
        self.pin_l = 20
        self.tag = str(uuid.uuid4())
        self.catching_area = None
    def draw(self):
        raise NotImplementedError("Subclass must implement this method")
    def get_tip(self):
        raise NotImplementedError("Subclass must implement this method")
    def set_val(self, val):
        if val == 1 or val == 0:
            self.val = val
        else:
            raise ValueError(f"the value of pin cannot be set outside of binary values")
class Input(Pin):
    def __init__(self, canvas, gate, id):
        super().__init__(canvas, gate, id)
        self.connexion = None
            
    def draw(self):
        if self.id != 0:
            dy = (self.gate.w - (2 * self.gate.padding)) // (len(self.gate.inputs) - 1)
            self.c.create_line(self.gate.pos.x-self.pin_l, self.gate.pos.y+self.gate.padding+(dy*(self.id-1)), self.gate.pos.x, self.gate.pos.y+self.gate.padding+(dy*(self.id-1)), fill="black", tags=(self.tag, "input", self.gate.tag))
            self.catching_area = self.c.create_rectangle(self.get_tip().x-10,self.get_tip().y-10, self.get_tip().x+10, self.get_tip().y+10, fill="", activefill="red", tags=(self.tag, self.id, "input_catching_area", self.gate.tag))
        else:
            dy = self.gate.w // 2
            self.c.create_line(self.gate.pos.x-self.pin_l, self.gate.pos.y+dy, self.gate.pos.x, self.gate.pos.y+dy, fill="black", tags=(self.tag, "input", self.gate.tag))
            self.catching_area = self.c.create_rectangle(self.get_tip().x-10,self.get_tip().y-10, self.get_tip().x+10, self.get_tip().y+10, fill="", activefill="red", tags=(self.tag, self.id, "input_catching_area", self.gate.tag))
    def get_tip(self): 
        if self.id != 0:
            dy = (self.gate.w - (2 * self.gate.padding)) // (len(self.gate.inputs) - 1)
            return Point(self.gate.pos.x-self.pin_l, self.gate.pos.y+self.gate.padding+(dy*(self.id-1)))
        else:
            dy = self.gate.w // 2
            return Point(self.gate.pos.x-self.pin_l, self.gate.pos.y+dy)

class Output(Pin):
    def __init__(self, canvas, gate, id):
        super().__init__(canvas, gate, id)
        self.connections = []
    def draw(self):
        dy = self.gate.w // 2
        self.c.create_line(self.gate.pos.x+self.gate.h, self.gate.pos.y+dy, self.gate.pos.x+self.gate.h+self.pin_l, self.gate.pos.y+dy, fill="black", tags=(self.tag, "output", self.gate.tag))
        self.catching_area = self.c.create_rectangle(self.get_tip().x-10, self.get_tip().y-10, self.get_tip().x+10, self.get_tip().y+10, fill="", activefill="red", tags=(self.tag, "output_catching_area", self.gate.tag))
    def get_tip(self):
        dy = self.gate.w // 2
        return Point(self.gate.pos.x+self.gate.h+self.pin_l, self.gate.pos.y+dy)
    def add_connection(self, input_pin):
        self.connections.append(input_pin)
        input_pin.connexion = self

    def draw_connections(self, x=None, y=None):
        tag = "connection"+self.tag
        connection_number = 0
        if x is not None and y is not None:
            pos1 = self.get_tip()
            pos2 = Point(x, y)
            self.c.create_line(pos1.x, pos1.y, pos2.x, pos1.y, fill="black", tags=(self.tag, tag))
            self.c.create_line(pos2.x, pos1.y, pos2.x, pos2.y, fill="black", tags=(self.tag, tag))
        else:
            for connection in self.connections:
                tag1 = tag + str(connection_number)
                connection_number += 1
                pos1 = self.get_tip()
                pos2 = connection.get_tip()
                self.c.create_line(pos1.x, pos1.y, pos2.x, pos1.y, fill="black", tags=(self.tag, tag, tag1))
                self.c.create_line(pos2.x, pos1.y, pos2.x, pos2.y, fill="black", tags=(self.tag, tag, tag1))
                
    def propagate_signal(self):
        for connection in self.connections:
            connection.val = self.val








