import os
import glob
from dotenv import load_dotenv
from classes.line import Line
import spacy

from classes.database import Database


class Application(object):
    def __init__(self):
        self.synonym_files = []
        self.synonym_terms = {}
        load_dotenv('.env')
        self.resources_path = os.path.join(os.getcwd(), "resources")
        self.validations_path = os.path.join(self.resources_path, "validations")
        self.synonym_path = os.path.join(self.resources_path, "synonyms")
        self.out_path = os.path.join(self.synonym_path, "trimonyms")
        self.synonym_pattern = os.path.join(self.synonym_path, "synonyms*")
        self.max_codes = int(os.getenv('MAX_CODES'))
        self.nlp = spacy.load("en_core_web_md")
        self.get_synonym_files()

    def get_synonym_files(self):
        print("Getting synonym files")
        for name in glob.glob(self.synonym_pattern):
            if "combined" in name:
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

    def get_database_descriptions(self):
        print("Getting descriptions")
        self.codes = {}
        self.database_terms = []
        sql = """
        select goods_nomenclature_item_id, productline_suffix, description
        from utils.materialized_commodities mcn order by goods_nomenclature_item_id
        """
        params = []
        d = Database()
        rows = d.run_query(sql, params)
        for row in rows:
            key = row[0] + "-" + row[1]
            self.codes[key] = row[2]

        self.tokenise_database_descriptions()

    def tokenise_database_descriptions(self):
        print("Tokenising - likely to take 3 minutes")
        terms = []
        index = 0
        for code in self.codes:
            index += 1
            description = self.codes[code].lower()
            doc = self.nlp(description)
            terms = [token.lemma_.lower() for token in doc if (not (token.lemma_.isnumeric()) and len(token.lemma_) > 2)]
            self.database_terms += terms
            print(index)
            if index > self.max_codes:
                break

        self.database_terms = list(set(self.database_terms))
        self.database_terms = sorted(self.database_terms)
        print(self.database_terms)

    def get_synonym_terms(self):
        print("Tokenising synonym files")
        for file in self.synonym_files:
            self.get_synonym_terms_from_file(file)

    def get_synonym_terms_from_file(self, file):
        print("Tokenising synonym file: " + file)
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
                line = line.replace(" => ", ", ")
                doc = self.nlp(line)
                terms = [token.lemma_.lower() for token in doc if len(token.lemma_) > 2]
                for term in terms:
                    if term == "and":
                        a = 1
                    if term in self.synonym_terms:
                        self.synonym_terms[term] += 1
                    else:
                        self.synonym_terms[term] = 1

    def check_synonyms_in_database(self):
        self.matches = []
        for term in self.synonym_terms:
            if term in self.database_terms:
                self.matches.append(term)

        path = os.path.join(self.validations_path, "matches.csv")
        with open(path, 'w') as f:
            for match in self.matches:
                f.write(match + "\n")
        f.close()
