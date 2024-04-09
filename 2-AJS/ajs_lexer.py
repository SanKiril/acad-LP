import os
import re
from decimal import Decimal
import ply.lex as lex


class AJSLexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)
    
    # DEFINE LITERALS
    literals = ['{', '}', '(', ')', '[', ']', '=', ':', ',', ';']
    
    # DEFINE RESERVED TOKENS
    reserved = {
        "TR": True,
        "FL": False,
        "LET": "let",
        "INT": "int",
        "FLOAT": "float",
        "CHARACTER": "character",
        "WHILE": "while",
        "BOOLEAN": "boolean",
        "FUNCTION": "function",
        "RETURN": "return",
        "TYPE": "type",
        "IF": "if",
        "ELSE": "else",
        "NULL": None
    }
    
    # DEFINE TOKENS
    tokens = [
        "STRING_EXPLICIT",
        "STRING_IMPLICIT",
        "CHAR",
        "COMMENT",
        "REAL",
        "INTEGER",
        "ARITHMETIC",
        "BOOL",
        "COMPARATOR"
    ] + list(reserved.keys())
    
    # RECOGNIZE TOKENS
    def t_STRING_EXPLICIT(self, t):
        r'\"[^\"\n\r]*\"'
        t.value = t.value[1:-1]
        return t

    def t_STRING_IMPLICIT(self, t):
        r'[a-zA-Z_]\w*'
        if t.value.islower() and t.value.upper() in self.reserved:
            t.type = t.value.upper()
            t.value = self.reserved[t.value.upper()]
        return t

    def t_CHAR(self, t):
        r'\'[\x00-\x7F]\''
        t.value = t.value[1:-1]
        return t

    def t_COMMENT(self, t):
        r'(\/\/.*)|(\/\*(?:(?!\*\/).|\n)*\*\/)'
        pass
    
    def t_REAL(self, t):
        r'((?:(?:(?:[1-9]\d*|0)\.\d*)|(?:\.\d+))[eE](?:[1-9]\d*|0))|((?:(?:[1-9]\d*|0)\.\d*)|(?:\.\d+))'
        match = re.match(r'((?:(?:(?:[1-9]\d*|0)\.\d*)|(?:\.\d+))[eE](?:[1-9]\d*|0))|((?:(?:[1-9]\d*|0)\.\d*)|(?:\.\d+))', t.value)
        if match.group(1):  # arbitrary precision
            t.value = Decimal(match.group(1))
        else:  # single precision
            t.value = float(match.group(2))
        return t

    def t_INTEGER(self, t):
        r'(0[bB][01]+)|(0[0-7]+)|(0[xX][0-9a-fA-F]+)|([1-9]\d*|0)'
        match = re.match(r'(0[bB][01]+)|(0[0-7]+)|(0[xX][0-9a-fA-F]+)|([1-9]\d*|0)', t.value)
        if match.group(1):  # base 2
            t.value = int(match.group(1), 2)
        elif match.group(2):  # base 8
            t.value = int(match.group(2), 8)
        elif match.group(3):  # base 16
            t.value = int(match.group(3), 16)
        else:  # base 10
            t.value = int(match.group(4))
        return t

    t_ARITHMETIC = r'\+|\-|\*|\/'
    t_BOOL = r'\&\&|\|\||\!'
    t_COMPARATOR = r'\=\=|\>\=|\>|\<\=|\<'

    # INPUT BEHAVIOR
    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n|\r\n?'
        t.lexer.lineno = t.value.count(os.linesep)

    # ERROR HANDLING
    def t_error(self, t):
        raise ValueError(f"[ERROR][LEXER]: Illegal character:\n"
            f"# PROVIDED: {t.value[0]}")

    # RUN
    def tokenize(self, file_path: str):
        # open file
        try:
            with open(file_path, 'r', encoding="UTF-8") as file:
                data = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"FILE PATH NOT EXIST:\n"
                f"# PROVIDED: {file_path}")
        
        # tokenize
        self.lexer.input(data)
        
        # output directory
        if not os.path.exists("./output/"):
            os.makedirs("./output/")

        # output file
        with open("./output/" + os.path.splitext(os.path.basename(file_path))[0] + ".lexer", 'w', encoding="UTF-8") as file:
            file.write("\n".join([f"{t.type} {t.value}" for t in self.lexer]))