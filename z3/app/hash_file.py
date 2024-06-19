#!/usr/bin/python

from app.binary_file import BinaryFile


class HashFile(BinaryFile):
    def __init__(self, filename, record, blocking_factor, b, empty_key=-1):
        BinaryFile.__init__(self, filename, record, blocking_factor, empty_key)
        # broj baketa
        self.b = b
        # pokazivac na lanac baketa sa slobodnim lokacijama
        self.E = 0

    def hash(self, id):
        return id % self.b

    def init_file(self):
        with open(self.filename, "wb") as f:
            i = 0
            while i != self.b:
                block = [self.get_header_rec(i, self.b)] + self.blocking_factor*[self.get_empty_rec()]
                self.write_block(f, block)
                i += 1

    def change_reference(self, block):
        with open(self.filename, "rb+") as f:
            before_block_idx = block[0].get("before")
            next_block_idx = block[0].get("next")

            block[0]["before"] = "*"
            block[0]["next"] = "*"
            if before_block_idx != "*":
                before_block_idx = int(before_block_idx)
                f.seek(before_block_idx * self.block_size)
                before_block = self.read_block(f)
                before_block[0]["next"] = str(next_block_idx)
                f.seek(before_block_idx * self.block_size)
                self.write_block(f, before_block)
            if next_block_idx != "*":
                next_block_idx = int(next_block_idx)
                f.seek(next_block_idx * self.block_size)
                next_block = self.read_block(f)
                next_block[0]["before"] = str(before_block_idx)
                f.seek(next_block_idx * self.block_size)
                self.write_block(f, next_block)

    def insert_record(self, rec):
        id = rec.get("id")
        block_idx = self.hash(int(id))
        if self.find_by_id(id):
            return False

        with open(self.filename, "rb+") as f:
            f.seek(block_idx * self.block_size)
            block = self.read_block(f)

            u = block[0].get("u")
            if u == "":
                rec["u"] = "*"
                block[1] = rec
                empty = block[0].get("empty")
                block[0]["empty"] = empty-1
                block[0]["u"] = str(block_idx) + str(1)
                f.seek(block_idx * self.block_size)
                self.write_block(f, block)
                return True

            overflow = False
            if block[0].get("empty") == 0:
                block_idx = self.E
                f.seek(block_idx * self.block_size)
                block = self.read_block(f)
                overflow = True

            i = 1
            while i < self.blocking_factor + 1:
                if block[i].get("status") == 1:
                    if block[i].get("id") == id:
                        return False
                    i += 1
                    continue
                rec["u"] = "*"
                block[i] = rec
                new_empty = block[0].get("empty") - 1
                block[0]["empty"] = new_empty
                if new_empty == 0:
                    if self.E == block_idx:
                        self.E = int(block[0].get("next"))
                    self.change_reference(block)
                if overflow and i == 1:
                    block[0]["u"] = "*"
                f.seek(block_idx * self.block_size)
                self.write_block(f, block)
                break
            if u == "*":
                block[0]["u"] = str(block_idx) + str(i)
                f.seek(block_idx * self.block_size)
                self.write_block(f, block)
                return True
            f.seek(int(u[0]) * self.block_size)
            block = self.read_block(f)
            last = block[int(u[1])]

            lastj = int(u[0])
            while True:
                ij = last.get("u")
                if ij == "*":
                    last["u"] = str(block_idx) + str(i)
                    f.seek(lastj * self.block_size)
                    self.write_block(f, block)
                    return True
                lasti = int(ij[1])
                lastj = int(ij[0])
                f.seek(lastj * self.block_size)
                block = self.read_block(f)
                last = block[lasti]

    def print_file(self):
        with open(self.filename, "rb") as f:
            a = 0
            for i in range(self.b):
                block = self.read_block(f)
                print("Baket {}".format(i), "Adresa {}".format(a))
                a += self.block_size
                self.print_block(block)

    def find_by_id(self, id):
        block_idx = self.hash(int(id))
        with open(self.filename, "rb+") as f:
            address = block_idx * self.block_size
            f.seek(address)
            block = self.read_block(f)
            u = block[0]["u"]
            while True:
                if u == "" or u == "*":
                    return None
                i = int(u[1])
                j = int(u[0])
                if j != block_idx:
                    address = j * self.block_size
                    f.seek(address)
                    block = self.read_block(f)
                record = block[i]
                if record.get("id") == id:
                    return record, address, i, j
                else:
                    u = record.get("u")

    def change_reference_delete(self, block, block_idx):
        with open(self.filename, "rb+") as f:
            before = block_idx - 1
            after = block_idx + 1

            while before >= 0:
                f.seek(before * self.block_size)
                before_block = self.read_block(f)
                if before_block[0].get("empty") != 0:
                    block[0]["before"] = str(before)
                    before_block[0]["next"] = str(block_idx)

                    f.seek(before * self.block_size)
                    self.write_block(f, before_block)
                    break
                before -= 1

            while after <= self.b:
                f.seek(after * self.block_size)
                after_block = self.read_block(f)
                if after_block[0].get("empty") != 0:
                    block[0]["next"] = str(after)
                    after_block[0]["before"] = str(block_idx)

                    f.seek(after * self.block_size)
                    self.write_block(f, after_block)
                    break
                after += 1

    def delete_by_id(self, id):
        found = self.find_by_id(id)
        if not found:
            return False
        record, address, i, j = found
        with open(self.filename, "rb+") as f:
            f.seek(j * self.block_size)
            block = self.read_block(f)
            for_delete = block[i]
            next_index = for_delete.get("u")
            block[i] = self.get_empty_rec()
            new_empty = block[0].get("empty") + 1
            block[0]["empty"] = new_empty
            pr = False
            if block[0].get("u") == str(j) + str(i):
                if next_index == "*":
                    block[0]["u"] = ""
                    pr = True
                else:
                    block[0]["u"] = next_index
                    pr = True
            if new_empty == 1:
                self.change_reference_delete(block, j)
                if j < self.E:
                    self.E = j
            f.seek(j * self.block_size)
            self.write_block(f, block)
            if block[0].get("u") == "":
                return True
            # find before
            first_block_idx = self.hash(int(id))
            f.seek(self.block_size * first_block_idx)
            b = self.read_block(f)
            first = b[int(b[0].get("u")[1])]
            while True:
                if pr:
                    break
                next = first.get("u")
                if next == str(j) + str(i):
                    first["u"] = next_index
                    print(first["u"])
                    f.seek(first_block_idx * self.block_size)
                    self.write_block(f, b)
                    break
                first_block_idx = int(next[0])
                f.seek(first_block_idx * self.block_size)
                first = self.read_block(f)[int(next[1])]
            return True

    def update_e(self):
        with open(self.filename, "rb") as f:
            i = 0
            while i < self.b - 1:
                f.seek(i * self.block_size)
                block = self.read_block(f)
                if block[0].get("empty") != 0:
                    self.E = i
                    break
                i += 1
