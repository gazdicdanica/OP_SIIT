#!/usr/bin/python

import struct

class Record:
    def __init__(self, attributes_data, attributes_header, format_data, format_header, coding):
        self.attributes_data = attributes_data
        self.attributes_header = attributes_header
        self.format_data = format_data
        self.format_header = format_header
        self.coding = coding

    def encoded_tuple_to_dict(self, binary_data, header):
        if not header:
            t = struct.unpack(self.format_data, binary_data)
            return {self.attributes_data[i]: t[i].decode(self.coding).strip('\x00') if isinstance(t[i], bytes) else t[i] for i in range(len(t))}
        else:
            t = struct.unpack(self.format_header, binary_data)
            return {self.attributes_header[i]: t[i].decode(self.coding).strip('\x00') if isinstance(t[i], bytes) else t[i] for i in range(len(t))}

    def dict_to_encoded_values(self, d, header):
        values = [v.encode(self.coding) if isinstance(v, str) else v for v in d.values()]
        if not header:
            return struct.pack(self.format_data, *values)
        else:
            return struct.pack(self.format_header, *values)
