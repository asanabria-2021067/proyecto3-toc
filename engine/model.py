from dataclasses import dataclass, field

BLANK = None  # blank de la cinta y del cache
MOVES = {"L": -1, "R": 1, "S": 0}


def show(sym):
    return "B" if sym is BLANK else sym


@dataclass
class TuringMachine:
    states: list
    initial: str
    finals: set
    alphabet: list
    tape_alphabet: list  # incluye BLANK (None)
    # (estado, cache, leido) -> (estado, cache, escrito, movimiento)
    delta: dict
    strings: list = field(default_factory=list)

    def to_dict(self):
        return {
            "states": self.states,
            "initial": self.initial,
            "finals": sorted(self.finals),
            "alphabet": self.alphabet,
            "tape_alphabet": self.tape_alphabet,
            "delta": [
                {"from": list(k), "to": list(v)} for k, v in self.delta.items()
            ],
            "strings": self.strings,
        }


@dataclass
class Tape:
    cells: dict = field(default_factory=dict)  # posicion absoluta -> simbolo (sin blanks)
    head: int = 0

    @classmethod
    def from_string(cls, s):
        return cls({i: c for i, c in enumerate(s)})

    def read(self):
        return self.cells.get(self.head, BLANK)

    def write(self, sym):
        if sym is BLANK:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = sym

    def move(self, d):
        self.head += MOVES[d]

    def span(self):
        """(lo, hi) de las celdas visibles: no-blanks mas la celda del cabezal."""
        pos = list(self.cells) + [self.head]
        return min(pos), max(pos)

    def snapshot(self):
        """(celdas, indice del cabezal en la lista, posicion absoluta de celdas[0])"""
        lo, hi = self.span()
        return [self.cells.get(i, BLANK) for i in range(lo, hi + 1)], self.head - lo, lo

    def content(self):
        """Cinta sin blanks en los extremos (cadena vacia si todo es blank)."""
        if not self.cells:
            return ""
        lo, hi = min(self.cells), max(self.cells)
        return "".join(show(self.cells.get(i)) for i in range(lo, hi + 1))


@dataclass
class Configuration:
    state: str
    cache: object
    tape: Tape

    def id(self):
        cells, h, _ = self.tape.snapshot()
        u = "".join(show(x) for x in cells[:h])
        v = "".join(show(x) for x in cells[h:])
        return f"{u} [{self.state},{show(self.cache)}] {v}"


@dataclass
class Step:
    i: int
    config: Configuration
    transition: dict = None  # {"from": [q,c,leido], "to": [q,c,escrito,mov]} aplicada para LLEGAR aqui

    def to_dict(self):
        cells, h, off = self.config.tape.snapshot()
        return {
            "i": self.i,
            "state": self.config.state,
            "cache": self.config.cache,
            "tape": cells,
            "head": h,
            "offset": off,
            "id": self.config.id(),
            "transition": self.transition,
        }
