import struct

ATTRIBUTES = ["id", "registration", "date", "ramp", "value", "status"]
FMT = "9s11s21s5sii"
CODING = "ascii"
RECORD_SIZE = struct.calcsize(FMT)

F = 5