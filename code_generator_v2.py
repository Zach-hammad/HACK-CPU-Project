# -*- coding: utf-8 -*-
"""
Parser to generate the abstract syntax tree (AST) for a program 
containing compound statements.

Author: Naga Kandasamy
Date created: November 12, 2020

Student name(s): Zach Hammad

Notes: Adapted from "Let’s Build A Simple Interpreter" by Ruslan Spivak
https://ruslanspivak.com/lsbasi-part1/
"""

import sys

################################################################
#
# SCANNER
#
################################################################
# Token types 
INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
LPAREN = '('
RPAREN = ')'
LCURLY = '{'
RCURLY = '}'
ASSIGN = '='
SEMI = ';'
ID = 'ID'
EOF = 'EOF'


class Token(object):
    """Token class"""
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    
    def __str__(self):
        """Prints the Token object in the following format:
            Token(INTEGER, 5)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({token_type}, {value})'.format(token_type = self.type, value = repr(self.value))
    
    def __repr__(self):
        return self.__str__()
  
class Scanner(object):
    """The Scanner processes tokens to provide to the parser"""
    def __init__(self, text):
        self.text = text
        self.pos = 0        # Index into the text
        self.curr_char = self.text[self.pos]
        
    def error(self):
        raise Exception('Scanner: invalid character')
        
    def advance(self):
        """Advance 'pos' pointer and set the current character"""
        self.pos = self.pos + 1
        if self.pos > len(self.text) - 1:
            self.curr_char = None           # End of input
        else:
            self.curr_char = self.text[self.pos]
            
    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.curr_char is not None and self.curr_char.isspace():
            self.advance()
            
    def integer(self):
        """Return an integer value consumed from the input"""
        token = ''
        while self.curr_char is not None and self.curr_char.isdigit():
            token = token + self.curr_char
            self.advance()
        
        return int(token)
           
    def _id(self):
        """Handle identifiers and keywords"""
        token = ''
        while self.curr_char is not None and self.curr_char.isalnum():
            token += self.curr_char
            self.advance()
            
        return Token(ID, token)

    
    def get_next_token(self):
        """Core of the lexical analyzer (or scanner).
            Decompose text into tokens, one token at a time.
        """
        while self.curr_char is not None:
            
            if self.curr_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.curr_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.curr_char.isalpha():
                return self._id()
            
            if self.curr_char == '+':
                self.advance()
                return Token(PLUS, '+')
            
            if self.curr_char == '-':
                self.advance()
                return Token(MINUS, '-')
            
            if self.curr_char == '*':
                self.advance()
                return Token(MUL, '*')
            
            if self.curr_char == '/':
                self.advance()
                return Token(DIV, '/')
            
            if self.curr_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            
            if self.curr_char == ')':
                self.advance()
                return Token(RPAREN, ')')
                    
            if self.curr_char == '{':
                self.advance()
                return Token(LCURLY, '{')
                
            if self.curr_char == '}':
                self.advance()
                return Token(RCURLY, '}')
                    
            if self.curr_char == '=':
                self.advance()
                return Token(ASSIGN, '=')
            
            if self.curr_char == ';':
                self.advance()
                return Token(SEMI, ';')
            
            self.error()
            
        return Token(EOF, None)


"""
def test_scanner(scanner):
    token = scanner.get_next_token()
    while token.type is not EOF:
        print(token)
        token = scanner.get_next_token()
        
    print(token)
"""


####################################################################
#
# Definitions of nodes in the abstract synatx tree 
#
#####################################################################
        
class AST(object):
    pass

class UnaryOperator(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinaryOperator(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        
class Number(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class CompoundStatement(AST):
    """This AST node represents a compound statement between lCURLY and RCURLY braces. 
    It contains a list of statement nodes in its children variable."""
    def __init__(self):
        self.children = []
        
class Assign(AST):
    """AST node represents an assignment statement. 
    Left variable stores a Var node and right variable stores a node returned by the expr() method.
    """
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass
     
###################################################################
#
# PARSER
#
###################################################################        

class Parser(object):
    """Implements a recursive descent parser for the classic expression grammar.
    """
    def __init__(self, scanner):
        self.scanner = scanner
        self.curr_token = self.scanner.get_next_token()
        
    def error(self):
        raise Exception('Syntax error')      
        
    def consume(self, token_type):
        """Compare the current token type with the passed 
        token type and if the types match, consume the token and 
        assign the next token to self.current_token.
        """
        if self.curr_token.type == token_type:
            self.curr_token = self.scanner.get_next_token()
        else:
            self.error()
            
    def factor(self):
        """
         factor  -->     LPAREN expr RPAREN
                 |      (PLUS | MINUS) factor
                 |      INTEGER
                 |      variable
        """
        token = self.curr_token
        
        if token.type == LPAREN:
            self.consume(LPAREN)
            node = self.expr()
            self.consume(RPAREN)
            return node
        
        elif token.type == PLUS:
            self.consume(PLUS)
            node = UnaryOperator(token, self.factor())
            return node
        
        elif token.type == MINUS:
            self.consume(MINUS)
            node = UnaryOperator(token, self.factor())
            return node
        
        elif token.type == INTEGER:
            self.consume(INTEGER)
            return Number(token)
        
        else:
            node = self.variable()
            return node
        
            
    def term(self):
        """
        term    -->     term * factor 
                 |      term / factor
                 |      factor
        """
        node = self.factor()
        
        while self.curr_token.type in (MUL, DIV):
            token = self.curr_token
            
            if token.type == MUL:
                self.consume(MUL)
            
            elif token.type == DIV:
                self.consume(DIV)
                
            node = BinaryOperator(left = node, op = token, right = self.factor())
            
        return node
    
    def expr(self):
        """
        expr    -->     expr + term
                 |      expr - term 
                 |      term
        term    -->     term * factor 
                 |      term / factor
                 |      factor
        factor  -->     LPAREN expr RPAREN
                 |      (PLUS | MINUS) factor
                 |      INTEGER
                 |      variable
        """
        
        node = self.term()
        
        while self.curr_token.type in (PLUS, MINUS):
            token = self.curr_token
            
            if token.type == PLUS:
                self.consume(PLUS)
            
            elif token.type == MINUS:
                self.consume(MINUS)
            
            node = BinaryOperator(left = node, op = token, right = self.term())
        
        return node
    
    def empty(self):
        return NoOp()
    
    def variable(self):
        """variable ---> ID"""
        node = Var(self.curr_token)
        self.consume(ID)
        return node
    
    def assignment_statement(self):
        """assignment_statement ---> variable ASSIGN expr SEMI"""
        left = self.variable()
        op = self.curr_token.type
        self.consume(ASSIGN)
        right = self.expr()
        self.consume(SEMI)
        
        node = Assign(left, op, right)
        return node
    
    def statement(self):
        """statement ---> compound_statment 
                      |   assignment_statement 
        """
        if self.curr_token.type == LCURLY:
            node = self.compound_statment()
        elif self.curr_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
            
        return node
    
    
    def statement_list(self):
        """statement_list ---> statement 
                            |  statement_list statement
        """
        node = self.statement()
        nodes = [node]
        
        while self.curr_token.type != RCURLY:
            nodes.append(self.statement())
            
        return nodes
        
    
    def compound_statment(self):
        """compound_statement ---> LCURLY statement_list RCURLY"""
        self.consume(LCURLY)
        nodes = self.statement_list()
        self.consume(RCURLY)
        root = CompoundStatement()
        
        for node in nodes:
            root.children.append(node)
        
        return root
    
    def program(self):
        """program ---> compound_statement EOF"""
        node = self.compound_statment()
        self.consume(EOF)
        return node
    
    def parse(self):
        node = self.program()
        return node

class NodeVisitor(object):
    """Class for the node visitor"""
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class CodeGenerator(NodeVisitor):
    """Class for code generator"""
    def __init__(self, AST):
        self.tree = AST
        
    def visit_BinaryOperator(self, node):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        root_value = node.op.value   
        return '{left} {right} {root}'.format(left = left_value, right = right_value, root = root_value)
    
    def visit_Number(self, node):
        return node.value
    
    def visit_Var(self, node):
        variable_name = node.value
        return variable_name

    def visit_Assign(self, node):
        variable_name = node.left.value
        expr = self.visit(node.right)
        #print(variable_name, '=', expr)
        
        """FIXME: generate VM commands here.
        
        1. Obatain the postfix from of the expression on the RHS. 
        2. Tokenize the postfix form and scan from left to right. 
            2a. If you encounter a numeric token, generate VM command to push constant into working stack.
            2b. If you encounter an alphanumeric token, look in the symbol table for the variable's address within the local segment; 
                generate VM command to push variable into working stack.
            2c. If you encounter a bimary operator, generate VM command to perform operation.
        3. Look in the symbol table for the address of the variable on the LHS.
            3a. If you locate the variable in the symbol table, generate VM command to pop the result from the working stack 
                and save it to the specified address.
            3b. If variable is not found in the symbol table, you are encountering it for the first time; add it to the symbol table 
                along with the corresponding address in the local segment. Generate VM command to pop the result off the working stack 
                and save it to the address just added to the symbol table.
        """
        tokens = str.split(str(expr))

        #scanning RHS
        for token in tokens:
            if(token is '+'):
                vm_code.append('call add 2')
            elif(token is '-'):
                vm_code.append('call sub 2')
            elif(token is '/'):
                vm_code.append('call div 2')
            elif(token is '*'):
                vm_code.append('call mult 2')
            elif(token.isnumeric()):
                vm_code.append("push constant "+token)
            else:
                if token in symbols.keys():
                    vm_code.append("push local "+str(symbols[token]))
                else:
                    symbols[token] = max(symbols.values() or [-1]) + 1
                    vm_code.append("push local "+str(symbols[token]))

        #scanning LHS
        if variable_name in symbols.keys():
            vm_code.append("pop local "+str(symbols[variable_name]))
        else:
            symbols[variable_name] = max(symbols.values() or [-1]) + 1
            vm_code.append("pop local "+str(symbols[variable_name]))

        return vm_code
    
    def visit_CompoundStatement(self, node):
        for child in node.children:
            self.visit(child)
        
    def visit_noOp(self, node):
        pass
    
    def generate(self):
        return self.visit(self.tree)

#global symbol table
symbols = {}
vm_code = []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: Python code_generator_v2.py file-name.txt file-name.vm')
        print('file-name.txt: file containing the source program')
        print('file-name.vm: output file containing VM commands')
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        f = open(input_file, 'r')
        program = f.read()
        print('Original program:')
        print(program)
        print()
        
        print('Generating AST')
        scanner = Scanner(program)
        parser = Parser(scanner)
        AST = parser.parse()

        print('Generating code')
        code_generator = CodeGenerator(AST) 
        x = code_generator.generate() #return useless?

        # FIXME: Write VM commands to output file
        with open(output_file, "w") as f:
            f.truncate(0)
            f.write("function "+input_file.split(".")[0]+" "+str(symbols.__len__())+"\n")
            for line in vm_code:
                f.write(line+"\n")
            f.write("return")
