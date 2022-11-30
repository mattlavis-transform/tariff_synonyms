import os
import glob
from dotenv import load_dotenv
from classes.line import Line


class Application(object):
    def __init__(self):
        self.synonym_files = []
        load_dotenv('.env')
        self.resources_path = os.path.join(os.getcwd(), "resources")
        self.synonym_path = os.path.join(self.resources_path, "synonyms")
        self.out_path = os.path.join(self.synonym_path, "trimonyms")
        self.synonym_pattern = os.path.join(self.synonym_path, "synonyms*")
        self.get_synonym_files()

    def get_synonym_files(self):
        for name in glob.glob(self.synonym_pattern):
            # print(name)
            print(os.path.basename(name))
            self.synonym_files.append(os.path.basename(name))
        self.synonym_files.sort()
        a = 1

    def trim_files(self):
        for file in self.synonym_files:
            self.trim_file(file)
            self.write_out_file(file)

    def trim_file(self, file):
        path = os.path.join(self.synonym_path, file)
        f = open(path, 'r')
        self.lines = []
        lines_in_file = f.readlines()
        for line in lines_in_file:
            line = line.strip("\n")
            if "#" in line:
                # This is a comment
                pass
            elif len(line) == 0:
                # This is a blank line
                pass
            else:
                a = 1
                line_obj = Line(line)
                self.lines.append(line_obj)

    def write_out_file(self, file):
        path = os.path.join(self.out_path, file)
        with open(path, 'w') as f:
            for line in self.lines:
                if line.valid:
                    f.write(line.line_out + "\n")
        f.close()
