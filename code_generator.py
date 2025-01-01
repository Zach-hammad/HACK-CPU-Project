# -*- coding: utf-8 -*-
"""
Program to generate the abstract syntax tree (AST) for expression evaluation. Once the AST is generated, postorder traversal is 
used to obtain the postfix noation for the expression. VM commands for the stack machine are generated from the postfix 
notation.

Author: Naga Kandasamy
Date created: November 12, 2020
Date modified: November 24, 2020

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
        return 'Token({token_type}, {value})'.format(token_type = self.token_type, value = repr(self.value))
    
    def __repr__(self):
        return self.__str__()
        
class Scanner(object):
    """The Scanner class that processes tokens to provide to the parser"""
    def __init__(self, text):
        self.text = text
        self.pos = 0        # Index into the text
        self.curr_char = self.text[self.pos]
        
    def error(self):
        raise Exception('scanner: invalid character')
        
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
            
    def get_next_token(self):
        """Core of the lexical analyzer (or scanner).
            Decompose the text into tokens, one token at a time.
        """
        while self.curr_char is not None:
            
            if self.curr_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.curr_char.isdigit():
                return Token(INTEGER, self.integer())
            
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
            
            self.error()
            
        return Token(EOF, None)


####################################################################
#
# Abstract synatx tree 
#
#####################################################################       
class AST(object):
    pass

class UnaryOperator(AST):
    """Unary operator node within the AST."""
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinaryOperator(AST):
    """Binary operator node within the AST."""
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        
class Number(AST):
    """Terminal node within the AST containing the number."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

###################################################################
#
# PARSER
#
###################################################################        
class Parser(object):
    """Implements a recursive descent parser for the classic expression grammar."""
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
        """
        token = self.curr_token
        
        if token.type == PLUS:
            self.consume(PLUS)
            node = UnaryOperator(token, self.factor())
            return node
        
        if token.type == MINUS:
            self.consume(MINUS)
            node = UnaryOperator(token, self.factor())
            return node
        
        if token.type == INTEGER:
            self.consume(INTEGER)
            return Number(token)
        
        elif token.type == LPAREN:
            self.consume(LPAREN)
            node = self.expr()
            self.consume(RPAREN)
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
    
    def parse(self):
        return self.expr()


class NodeVisitor(object):
    """Node visitor class that customizes the visit function to the specific type of node being visited."""
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class InorderVisitor(NodeVisitor):
    """Class for in-order traversal of the AST"""
    def __init__(self, AST):
        self.tree = AST
        
    def visit_BinaryOperator(self, node):
        left_value = self.visit(node.left)
        root_value = node.op.value
        right_value = self.visit(node.right)
        
        return '{left} {root} {right}'.format(left = left_value, root = root_value, right = right_value)
    
    def visit_Number(self, node):
        return node.value
    
    def start(self):
        return self.visit(self.tree)

class PostorderVisitor(NodeVisitor):
    """Class for post-order traversal of the AST """
    def __init__(self, AST):
        self.tree = AST
        
    def visit_BinaryOperator(self, node):    
        #FIXME: Complete the method to perform postorder traversal of the AST.
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        root_value = node.op.value

        return '{left} {right} {root}'.format(left = left_value, root = root_value, right = right_value)
        
    
    def visit_Number(self, node):
        return node.value
    
    def start(self):
        return self.visit(self.tree)
   

class CodeGenerator(object):
    """Class for code generator"""
    def __init__(self, AST):
        self.AST = AST
        
    def generate(self):
        """
        FIXME: 
            1. Create an instance of the PostorderVisitor, providing the AST as input.
            2. Visit the AST in postorder fashion to obtain the postfix expression.
            3. Generate VM code using the postfix expression.
            """
        pv = PostorderVisitor(self.AST)
        a = pv.start()
        tokens = str.split(a)
        
        vm_code = []
        for token in tokens:
            if(token.isnumeric()):
                vm_code.append('push constant '+token)
            elif(token is '+'):
                vm_code.append('call add 2')
            elif(token is '-'):
                vm_code.append('call sub 2')
            elif(token is '/'):
                vm_code.append('call div 2')
            elif(token is '*'):
                vm_code.append('call mult 2')

        return vm_code

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: Python code_generator.py file-name.eval file-name.vm")
        print("file-name.eval: file containing the arithmetic expression")
        print("file-name.vm: output file containing the relevant VM commands")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        with open(input_file, 'r') as f:
            for expr in f:
                print('Evaluating expression', expr)
                expr.rstrip('\n')
                scanner = Scanner(expr)                         # Instantiate Scanner object
                
                print('Generating AST')
                parser = Parser(scanner)                        # Instantiate Parser object
                AST = parser.parse()                            # Generate abstract syntax tree
                
                print('Generating VM code from AST')
                generator = CodeGenerator(AST)                  # Instantiate Generator object
                vm_code = generator.generate()
                print('Writing VM code to', output_file)
                # FIXME: Write VM commands to output file
                with open(output_file, 'w') as f:
                    for string in vm_code:
                        f.write(string+"\n")
                
                
                



