class Line(object):
    def __init__(self, line):
        self.line = line
        self.line_out = ""
        self.process()

    def process(self):
        if "=>" in self.line:
            self.process_expansion()
        else:
            self.process_list()

    def process_expansion(self):
        self.left_side = []
        self.right_side = []

        parts = self.line.split("=>")
        if len(parts) == 2:
            left_part = parts[0]
            right_part = parts[1]
            left_parts = left_part.split(",")
            for part in left_parts:
                part = part.strip()
                if " " not in part:
                    self.left_side.append(part)

            right_parts = right_part.split(",")
            for part in right_parts:
                part = part.strip()
                if " " not in part:
                    self.right_side.append(part)

            if len(self.left_side) > 0 and len(self.right_side) > 0:
                self.valid = True
                self.line_out += ",".join(self.left_side) + " => " + ",".join(self.right_side)
                a = 1
            else:
                self.valid = False

    def process_list(self):
        out_parts = []
        parts = self.line.split(",")
        for part in parts:
            part = part.strip()
            if " " not in part:
                out_parts.append(part)

        if len(out_parts) > 1:
            self.line_out = ",".join(out_parts)
            self.valid = True
        else:
            self.valid = False
            a = 1
