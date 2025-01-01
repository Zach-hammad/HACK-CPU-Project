# -*- coding: utf-8 -*-
"""Assembler for the Hack processor.


Student name(s): Zach Hammad
"""

import os
import sys

"""The comp field is a c1 c2 c3 c4 c5 c6"""
valid_comp_patterns = {'0':'0101010', 
                       '1':'0111111',
                       '-1':'0111010',
                       'D':'0001100',
                       'A':'0110000',
                       '!D':'0001101',
                       '!A':'0110001',
                       '-D':'0001111',
                       '-A':'0110011',
                       'D+1':'0011111',
                       'A+1':'0110111',
                       'D-1':'0001110',
                       'A-1':'0110010',
                       'D+A':'0000010',
                       'D-A':'0010011',
                       'A-D':'0000111',
                       'D&A':'0000000',
                       'D|A':'0010101',
                       'M':'1110000',
                       '!M':'1110001',
                       '-M':'1110011',
                       'M+1':'1110111',
                       'M-1':'1110010',
                       'D+M':'1000010',
                       'M+D':'1000010',
                       'D-M':'1010011',
                       'M-D':'1000111',
                       'D&M':'1000000',
                       'D|M':'1010101'
                       }

"""The dest bits are d1 d2 d3"""
valid_dest_patterns = {'null':'000',
                       'M':'001',
                       'D':'010',
                       'MD':'011',
                       'A':'100',
                       'AM':'101',
                       'AD':'110',
                       'AMD':'111'
                       }

"""The jump fields are j1 j2 j3"""
valid_jmp_patterns =  {'null':'000',
                       'JGT':'001',
                       'JEQ':'010',
                       'JGE':'011',
                       'JLT':'100',
                       'JNE':'101',
                       'JLE':'110',
                       'JMP':'111'
                       }

"""Symbol table populated with predefined symbols and RAM locations"""
symbol_table = {'SP':0,
                'LCL':1,
                'ARG':2,
                'THIS':3,
                'THAT':4,
                'R0':0,
                'R1':1,
                'R2':2,
                'R3':3,
                'R4':4,
                'R5':5,
                'R6':6,
                'R7':7,
                'R8':8,
                'R9':9,
                'R10':10,
                'R11':11,
                'R12':12,
                'R13':13,
                'R14':14,
                'R15':15,
                'SCREEN':16384,
                'KBD':24576
                }

def print_intermediate_representation(ir):
    """Print intermediate representation"""
    
    for i in ir:
        print()
        for key, value in i.items():
            print(key, ':', value)

        
def print_instruction_fields(s):
    """Print fields in instruction"""
    
    print()
    for key, value in s.items():
        print(key, ':', value)


def valid_tokens(s):
    """Return True if tokens belong to valid instruction-field patterns"""
    
    # Check for C-instruction type
    if s['instruction_type'] == 'C_INSTRUCTION':
        # Both 'dest' and 'comp' fields should match the valid patterns
        if s['dest'] in valid_dest_patterns and s['comp'] in valid_comp_patterns and s['jmp'] in valid_jmp_patterns:
            return True
        else:
            return False

    # Check for A-instruction type
    if s['instruction_type'] == 'A_INSTRUCTION':
        # For A-instruction, it can be either a SYMBOL or a NUMERIC value. 
        # So, we check the validity based on that
        if s['value_type'] == 'SYMBOL':
            # Here, we are assuming that any string is a valid SYMBOL. 
            # You might want to add more stringent checks if required.
            return True
        elif s['value_type'] == 'NUMERIC':
            # Ensure that the value is a valid non-negative integer
            try:
                value = int(s['value'])
                if value >= 0:
                    return True
            except ValueError:
                return False

    # If we reached here, the tokens aren't valid for the known instruction types
    return False

    
    


def parse(command):
    """Implements finite automate to scan assembly statements and parse them.

    WHITE SPACE: Space characters are ignored. Empty lines are ignored.
    
    COMMENT: Text beginning with two slashes (//) and ending at the end of the line is considered 
    comment and is ignored.
    
    CONSTANTS: Must be non-negative and are written in decimal notation. 
    
    SYMBOL: A user-defined symbol can be any sequence of letters, digits, underscore (_), dot (.), 
    dollar sign ($), and colon (:) that does not begin with a digit.
    
    LABEL: (SYMBOL)
    """
    
    # Data structure to hold the parsed fields for the command
    s = {}
    s['instruction_type'] = ''
    s['value'] = ''
    s['value_type'] = ''
    s['dest'] = ''
    s['comp'] = ''
    s['jmp'] = ''
    s['status'] = 0
      
    
    # Valid operands and operations for C-type instructions
    valid_operands = '01DMA'
    valid_operations = '+-&|'
    
    
    # FIXME: Implement your finite automata to extract tokens from command
        # Removing comments and spaces
    if '//' in command:
        command = command.split("//")[0]
    command = command.strip()

    # Check for empty command
    if not command:
        return s

    # A-instruction
    if command[0] == '@':
        s['instruction_type'] = 'A_INSTRUCTION'
        value = command[1:]
        if value[0].isalpha() or value[0] in ['_', '.', '$', ':']:
            s['value_type'] = 'SYMBOL'
            s['value'] = value
        elif value.isnumeric():
            s['value_type'] = 'NUMERIC'
            s['value'] = value
        else:
            s['status'] = -1
            return s
        return s

    # Pseudo-instruction
    elif command[0] == '(' and command[-1] == ')':
        s['instruction_type'] = 'PSEUDO_INSTRUCTION'
        s['value_type'] = 'SYMBOL'
        s['value'] = command[1:-1]
        return s

    # C-instruction and J-instruction
    else:
        if '=' in command:
            parts = command.split('=')
            s['dest'] = parts[0].strip()
            s['comp'] = parts[1].split(';')[0].strip().replace(" ", "")
            if ';' in parts[1]:
                s['comp'] = parts[1].split(';')[0].strip().replace(" ", "")
            else:
                s['jmp'] = 'null'
        elif ';' in command:
            parts = command.split(';')
            s['comp'] = parts[0].strip()
            s['jmp'] = parts[1].strip()
            s['dest'] = 'null'
        s['instruction_type'] = 'C_INSTRUCTION'
        return s
    s['status'] = -1
    return s

   
def generate_machine_code(commands):
    machine_code = []
    next_free_ram_address = 16  # Start RAM address for variables

    # Pass 1: Address resolution
    rom_address = 0
    for command in commands:
        if command['instruction_type'] == 'PSEUDO_INSTRUCTION':
            symbol_table[command['value']] = rom_address
        else:
            rom_address += 1

    # Pass 2: Code translation
    for command in commands:
        if command['instruction_type'] == 'A_INSTRUCTION':
            value = command['value']
            
            if value.isdigit():  # Numeric address
                address = int(value)
            elif value in symbol_table:  # Label or previously seen variable
                address = symbol_table[value]
            else:  # New variable
                address = next_free_ram_address
                symbol_table[value] = address
                next_free_ram_address += 1
            
            machine_code.append('0' + format(address, '015b'))

        elif command['instruction_type'] == 'C_INSTRUCTION':
            comp = valid_comp_patterns[command['comp']]
            dest = valid_dest_patterns[command['dest']]
            jmp = valid_jmp_patterns[command['jmp']]
            machine_code.append('111' + comp + dest + jmp)
            
    return machine_code

    

def print_machine_code(machine_code):
    """Print generated machine code"""
    
    rom_address = 0
    for code in machine_code:
        print(rom_address, ':', code)
        rom_address = rom_address + 1


def run_assembler(file_name):      
    """Pass 1: Parse the assembly code into an intermediate data structure.
    The intermediate data structure can be a list of elements, called ir, where 
    each element is a dictionary with the following structure: 
    
    s['instruction_type'] = ''
    s['value'] = ''
    s['value_type'] = ''
    s['dest'] = ''
    s['comp'] = ''
    s['jmp'] = ''
    s['status'] = 0
    
    The symbol table is also generated in this step.    
    """
    intermediate_representation = []
    
    # Pass 1: Parse the assembly code to generate the intermediate data structure
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()  # Remove white spaces
            
            # Ignore empty lines and comments
            if not line or line[:2] == "//":
                continue
            
            # Parse the command and append to intermediate representation
            parsed_command = parse(line)
            if parsed_command['status'] == 0:  # Successful parsing
                intermediate_representation.append(parsed_command)

    # Convert the intermediate representation to machine code
    machine_code = generate_machine_code(intermediate_representation)

    return machine_code
    
  
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python assembler.py file-name.asm")
        print("Example: Python assembler.py mult.asm")
    else:
        print("Assembling file:", sys.argv[1])
        print()
        file_name_minus_extension, _ = os.path.splitext(sys.argv[1])
        output_file = file_name_minus_extension + '.hack'
        machine_code = run_assembler(sys.argv[1])
        if machine_code:
            print('Machine code generated successfully');
            print('Writing output to file:', output_file)
            f = open(output_file, 'w')
            for s in machine_code:
                f.write('%s\n' %s)
            f.close()
        else:
            print('Error generating machine code')
            
        

    
    
    
    
