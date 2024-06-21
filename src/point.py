class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other) :
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __repr__(self):
        return f"X:{self.x}, Y:{self.y}"



class Line():
    def __init__(self, p1, p2) -> None:
        self.p1 = p1
        self.p2 = p2
