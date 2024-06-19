#!/usr/bin/python

import struct


class BinaryFile:
    def __init__(self, filename, record, blocking_factor, empty_key=-1):
        self.filename = filename
        self.record = record
        self.record_size = struct.calcsize(self.record.format_data)
        self.header_size = struct.calcsize(self.record.format_header)
        self.blocking_factor = blocking_factor
        self.block_size = self.header_size + self.blocking_factor * self.record_size
        self.empty_key = empty_key

    def write_block(self, file, block):
        binary_data = bytearray()
        i = 0
        for rec in block:
            if i == 0:
                rec_binary_data = self.record.dict_to_encoded_values(rec, True)
            else:
                rec_binary_data = self.record.dict_to_encoded_values(rec, False)
            binary_data.extend(rec_binary_data)
            i += 1

        file.write(binary_data)

    def read_block(self, file):
        binary_data = file.read(self.block_size)
        block = []

        if len(binary_data) == 0:
            return block

        for i in range(self.blocking_factor + 1):   # slajsingom izdvajamo niz bita za svaki slog, i potom vrsimo otpakivanje
            if i == 0:
                begin = 0
                end = self.header_size
                block.append(self.record.encoded_tuple_to_dict(
                    binary_data[begin:end], True))
            else:
                begin = self.header_size + self.record_size*(i-1)
                end = self.header_size + self.record_size*i
                block.append(self.record.encoded_tuple_to_dict(
                    binary_data[begin:end], False))

        return block

    def write_record(self, f, rec):
        binary_data = self.record.dict_to_encoded_values(rec, False)
        f.write(binary_data)

    def read_record(self, f):
        binary_data = f.read(self.record_size)

        if len(binary_data) == 0:
            return None

        return self.record.encoded_tuple_to_dict(binary_data, False)

    def print_block(self, b):
        for i in range(self.blocking_factor + 1):
            print(b[i])

    def get_empty_rec(self):
        return {"id": str(self.empty_key), "senderAddress": "", "dateTime": "",
                "receiveAddress": "", "price": 0, "u": "", "status": 0}

    def get_header_rec(self, i, b):
        before = "*" if i == 0 else str(i-1)
        next = "*" if i == b-1 else str(i+1)
        return {"u": "", "before": before, "next": next, "empty": self.blocking_factor}
