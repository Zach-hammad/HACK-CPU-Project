# -*- coding: utf-8 -*-
"""
Compiler back-end for the Hack processor.
Translates from a stack-based language for the virtual machine to the Hack assembly code.

Adds support for program flow and subroutines.

Author: Naga Kandasamy
Date created: September 1, 2020
Date modified: May 11, 2021


Student names(s): Zach Hammad

"""
import os
import sys

line_number = 1

def generate_exit_code():
    """Generate epilogue code that places the program, upon completion, into 
    an infinite loop. 
    """
    s = []
    s.append('(THATS_ALL_FOLKS)')
    s.append('@THATS_ALL_FOLKS')
    s.append('0;JMP')
    return s

def generate_push_code(segment, index):
    """Generate assembly code to push value into the stack.
    In the case of a variable, it is read from the specified memory segment using (base + index) 
    addressing.
    """
    s = [] 
    strindex = str(index)
    numindex = int(index)

    if segment == 'constant':
        s.append('@'+strindex)
        s.append('D = A')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')   #store at SP top
        s.append('@SP')
        s.append('M = M + 1') #iterate SP
        return s
    if segment == 'local':
        s.append('@'+strindex)
        s.append('D = A')
        s.append('@LCL')
        s.append('A = M + D')
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    if segment == 'argument':
        s.append('@'+strindex)
        s.append('D = A')
        s.append('@ARG')
        s.append('A = M + D')
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    if segment == 'this':
        s.append('@'+strindex)
        s.append('D = A')
        s.append('@THIS')
        s.append('A = M + D')
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    if segment == 'that':
        s.append('@'+strindex)
        s.append('D = A')
        s.append('@THAT')
        s.append('A = M + D')
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    if segment == 'temp':
        s.append('@'+str(5+numindex))
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    if segment == 'pointer':
        if (index == '0'):
            s.append('@THIS')
            s.append('D = M')
            s.append('@SP')
            s.append('A = M')
            s.append('M = D')
            s.append('@SP')
            s.append('M = M + 1')
            return s
        else:
            s.append('@THAT')
            s.append('D = M')
            s.append('@SP')
            s.append('A = M')
            s.append('M = D')
            s.append('@SP')
            s.append('M = M + 1')
            return s
    if segment == 'static':
        s.append('@'+str(16+numindex))
        s.append('D = M')
        s.append('@SP')
        s.append('A = M')
        s.append('M = D')
        s.append('@SP')
        s.append('M = M + 1')
        return s
    
    return s
    
def generate_pop_code(segment, index):
    """Generate assembly code to pop value from the stack.
    The popped value is stored in the specified memory segment using (base + index) 
    addressing.
    """
    s = []
    segstring = ''
    if(segment == 'local'):
        segstring = 'LCL'
    elif(segment == 'argument'):
        segstring == 'ARG'
    elif(segment == 'this'):
        segstring == 'THIS'
    elif(segment == 'that'):
        segstring == 'THIS'

    if(segment == 'local' or segment == 'argument' or segment == 'this' or segment == 'that'):
        s.append('@'+segstring)
        s.append('D = M')
        s.append('@'+index)
    elif(segment == 'temp'):
        s.append('@'+str(5+int(index)))
    elif(segment == 'pointer'):
        if(index == '0'):
            s.append('@THIS')
        else:
            s.append('@THAT')
    elif(segment == 'static'):
        s.append('@'+str(16+int(index)))
    else:
        return s
    s.append('D = D + A')
    s.append('@R13') #temp
    s.append('M = D') #store address
    s.append('@SP')
    s.append('A = M')
    s.append('D = M')
    s.append('@R13')
    s.append('A = M')
    s.append('M = D') #push to segment, index
    s.append('@SP') #decrement SP
    s.append('M = M - 1')

    return s

def generate_arithmetic_or_logic_code(operation):
    """Generate assembly code to perform the specified ALU operation. 
    The two operands are popped from the stack and the result of the operation 
    placed back in the stack.
    """
    s = []
    
    #pop first to R13 and second to R14
    s.append('@SP')
    s.append('M = M - 1')
    s.append('A = M')
    s.append('D = M')
    s.append('@13')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M - 1')
    s.append('A = M')
    s.append('D = M')
    s.append('@14')
    s.append('M = D')
    #perform opertion on R13 and R14
    s.append('@13')
    s.append('D = M')
    s.append('@14')
    if(operation == 'add'):
        s.append('D = M + D')
    elif(operation == 'sub'):
        s.append('D = M - D')
    elif(operation == 'or'):
        s.append('D = M | D')
    elif(operation == 'and'):
        s.append('D = M & D')
    #push M of R14 back to SP
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')                 
    return s

def generate_unary_operation_code(operation):
    """Generate assembly code to perform the specified unary operation. 
    The operand is popped from the stack and the result of the operation 
    placed back in the stack.
    """
    s = []
    
    #pop first to R13
    s.append('@SP')
    s.append('A = M')
    s.append('D = M')
    s.append('@13')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M - 1')
    #perform opertion on R13
    s.append('@13')
    if(operation == 'neg'):
        s.append('D = -M')
    elif(operation == 'not'):
        s.append('D = !M')
    #push M of R13 back to SP
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')  
    return s

def generate_relation_code(operation, line_number):
    """Generate assembly code to perform the specified relational operation. 
    The two operands are popped from the stack and the result of the operation 
    placed back in the stack.
    """
    s = []
    label_1 = ''
    label_2 = ''
    
    s.append('@SP')
    s.append('A=M')
    s.append('D=M')             # D  = operand2
    s.append('@SP')
    s.append('M=M-1')           # Adjust stack pointer
    s.append('A=M')
        
    if operation == 'lt':
        s.append('D=M-D')       # D = operand1 - operand2
        label_1 = 'IF_LT_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JLT')       # if operand1 < operand2 goto IF_LT_*
        s.append('@SP')
        s.append('A=M')
        s.append('M=0')          # Save result on stack 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1')        # Save result on stack
        s.append('(' + label_2 + ')')
    
    if operation == 'eq':
        s.append('D=M-D')       # D = operand1 - operand2
        label_1 = 'IF_LT_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JGT')       # if operand1 < operand2 goto IF_LT_*
        s.append('@SP')
        s.append('A=M')
        s.append('M=0')          # Save result on stack 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1')        # Save result on stack
        s.append('(' + label_2 + ')')
    
    if operation == 'gt':
        s.append('D=M-D')       # D = operand1 - operand2
        label_1 = 'IF_LT_' + str(line_number)
        s.append('@' + label_1)
        s.append('D;JGT')       # if operand1 < operand2 goto IF_LT_*
        s.append('@SP')
        s.append('A=M')
        s.append('M=0')          # Save result on stack 
        label_2 = 'END_IF_ELSE_' + str(line_number)
        s.append('@' + label_2)
        s.append('0;JMP')
        s.append('(' + label_1 + ')')
        s.append('@SP')
        s.append('A=M')
        s.append('M=-1')        # Save result on stack
        s.append('(' + label_2 + ')')
    return s
 
def generate_if_goto_code(label):
    """Generate code for the if-goto statement. 

    Behavior:
    
    1. Pop result of expression from stack.
    2. If result is non-zero, goto LABEL.
    
    """
    s = []
    
    # FIXME: complete implementation
    #pop from stack
    s.append('@SP')
    s.append('M = M - 1')
    s.append('A = M')
    s.append('D = M')
    #if D non-zero goto label
    s.append('@'+label)
    s.append('D;JNE')
    return s

def generate_goto_code(label):
    """Generate assembly code for goto."""
    s = []
    
    s.append('@'+label)
    s.append('0;JMP')

    return s

def generate_pseudo_instruction_code(label):   
    """Generate pseudo-instruction for label."""
    s = []
    
    s.append('(' + label + ')')
    return s

def generate_set_code(register, value):
    """Generate assembly code for set"""
    s = []
    
    s.append('@' + value)
    s.append('D=A')
    
    if register == 'sp':
        s.append('@SP')
    
    if register == 'local':
        s.append('@LCL')
    
    if register == 'argument':
        s.append('@ARG')
        
    if register == 'this':
        s.append('@THIS')
        
    if register == 'that':
        s.append('@THAT')
        
    s.append('M=D')
    
    return s

def generate_function_call_code(function, nargs, line_number):  
    """Generate preamble for function"""
    s = []
    
    # FIXME: Push return address to stack
    s.append("@EXIT_"+function+"_"+str(line_number))
    s.append('D = A')
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')
    # FIXME: Push LCL, ARG, THIS, and THAT registers to stack
    #LCL
    s.append('@LCL')
    s.append('D = M')
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')
    #ARG
    s.append('@ARG')
    s.append('D = M')
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')
    #THIS
    s.append('@THIS')
    s.append('D = M')
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')
    #THAT
    s.append('@THAT')
    s.append('D = M')
    s.append('@SP')
    s.append('A = M')
    s.append('M = D')
    s.append('@SP')
    s.append('M = M + 1')
    # FIXME: Set ARG register to point to start of arguments in the current frame
    arglocal = 5 + int(nargs)     #Location is SP - (5 + numargs)
    s.append('@'+str(arglocal))
    s.append('D = A')
    s.append('@SP')
    s.append('D = M - D')   #store address to push to arg
    s.append('@ARG')
    s.append('M = D')
    # FIXME: Set LCL register to current SP
    s.append('@SP')
    s.append('D = M')
    s.append('@LCL')
    s.append('M = D')
    # FIXME: Generate goto code to jump to function 
    s.append("@"+function)
    s.append('0;JMP')
    # FIXME: Generate the pseudo-instruction/label corresponding to the return address
    s.append("(EXIT_"+function+"_"+str(line_number)+")")
    return s

def generate_function_body_code(f, nvars):
    """Generate code for function f.
    f: name of the function, which should be located in a separate file called f.vm
    n: number of local variables declared within the function.
    """
    s = []
    
    # FIXME: Generate the pseudo instruction -- the label
    s.append("("+f+")")
    # FIXME: Push nvars local variables into the stack, each intialized to zero
    for i in range(0, int(nvars)):
        s.append('@SP')
        s.append('A = M')
        s.append('M = 0')
        s.append('@SP')
        s.append('M = M + 1') #increment SP
    return s

def generate_function_return_code():
    """Generate assembly code for function return"""
    s = []
    
    s.append('// Copy LCL to temp register R14 (FRAME)')
    # FIXME: Copy LCL to temp register R14 (FRAME)
    s.append('@LCL')
    s.append('D = M')
    s.append('@R14')
    s.append('M = D')
    s.append('// Store return address in temp register R15 (RET)')
    # FIXME: Store return address in temp register R15 (RET)
    #RET is stored at frame - 5
    s.append('@5')
    s.append('D = A')
    s.append('@LCL')
    s.append('A = M')
    s.append('A = A - D')
    s.append('D = M') #got RET
    s.append('@R15')
    s.append('M = D') #stored
    s.append('// Pop result from the working stack and move it to beginning of ARG segment')
    # FIXME: Pop result from the working stack and move it to beginning of ARG segment
    s.append('@SP')
    s.append('M = M - 1')
    s.append('A = M')
    s.append('D = M')
    s.append('@ARG')
    s.append('M = D')
    # FIXME: Adjust SP = ARG + 1
    s.append('D = A + 1')
    s.append('@SP')
    s.append('M = D')
    # FIXME: Restore THAT = *(FRAME - 1)
    s.append("@R14")
    s.append('A = M - 1')
    s.append('D = M')
    s.append('@THAT')
    s.append('M = D')
    # FIXME: Restore THIS = *(FRAME - 2)
    s.append('@2')
    s.append('D = A')
    s.append("@R14")
    s.append('A = M - D')
    s.append('D = M')
    s.append('@THIS')
    s.append('M = D')
    # FIXME: Restore ARG = *(FRAME - 3)
    s.append('@3')
    s.append('D = A')
    s.append("@R14")
    s.append('A = M - D')
    s.append('D = M')
    s.append('@ARG')
    s.append('M = D')    
    # FIXME: Restore LCL = *(FRAME - 4)
    s.append('@4')
    s.append('D = A')
    s.append("@R14")
    s.append('A = M - D')
    s.append('D = M')
    s.append('@LCL')
    s.append('M = D')
    # FIXME: Jump to return address stored in R15 back to the caller code
    s.append('@R15')
    s.append('A = M')
    s.append('0;JMP')
    return s

def translate_vm_commands(tokens, line_number):
    """Translate a VM command into corresponding Hack assembly commands."""
    s = []
    
    if tokens[0] == 'push':
        s = generate_push_code(tokens[1], tokens[2])    # Generate code to push into stack
        
    elif tokens[0] == 'pop':
        s = generate_pop_code(tokens[1], tokens[2])     # Generate code to pop from stack
        
    elif tokens[0] == 'add' or tokens[0] == 'sub' \
         or tokens[0] == 'or' or tokens[0] == 'and':
        s = generate_arithmetic_or_logic_code(tokens[0])  # Generate code for ALU operation
        
    elif tokens[0] == 'neg' or tokens[0] == 'not':
        s = generate_unary_operation_code(tokens[0])    # Generate code for unary operations
        
    elif tokens[0] == 'eq' or tokens[0] == 'lt' or tokens[0] == 'gt':
        s = generate_relation_code(tokens[0], line_number)
    
    elif tokens[0] == 'label':
        s = generate_pseudo_instruction_code(tokens[1])
    
    elif tokens[0] == 'if-goto':
        s = generate_if_goto_code(tokens[1]) 
        
    elif tokens[0] == 'goto':
        s = generate_goto_code(tokens[1])
    
    elif tokens[0] == 'end':
        s = generate_exit_code()
        
    elif tokens[0] == 'set':
        s = generate_set_code(tokens[1], tokens[2])
        
    elif tokens[0] == 'function':
        s = generate_function_body_code(tokens[1], int(tokens[2]))
        
    elif tokens[0] == 'call':
        s = generate_function_call_code(tokens[1], tokens[2], line_number)
        
    elif tokens[0] == 'return':
        s = generate_function_return_code()
        
    else:
        print('translate_vm_commands: Unknown operation')           # Unknown operation 
    
    return s
    
def translate_file(input_file):
    """Translate VM file to Hack assembly code"""
    global line_number
    assembly_code = []
    assembly_code.append('// ' + input_file)
    
    with open(input_file, 'r') as f:
        for command in f:        
            # print("Translating line:", line_number, command)
            tokens = (command.rstrip('\n')).split()
            
            if not tokens:
                continue                                        # Ignore blank lines  
            
            if tokens[0] == '//':
                continue                                        # Ignore comment       
            else:
                s = translate_vm_commands(tokens, line_number)
                line_number = line_number + 1        
            if s:
                
                for i in s:
                    assembly_code.append(i)
            else:
                return False
            
    # Write translated commands to .i file
    file_name_minus_extension, _ = os.path.splitext(input_file)
    output_file = file_name_minus_extension + '.i'
    out = open(output_file, 'w')
    for s in assembly_code:
        out.write('%s\n' %s)
    out.close()
    print('Assembly file generated: ', output_file)
        
    return True

def run_vm_to_asm_translator(path):
    """Main translator code"""
    files = os.listdir(path)
    
    cwd = os.getcwd()
    os.chdir(path)
    
    if 'sys.vm' in files:
        idx = files.index('sys.vm')
        f = files.pop(idx)
        print('Translating:', f)
        status = translate_file(f)
        if status == False:
            print('Error translating ', f)
            return False
    else:
        print('Missing sys.vm file')
        return False
        
    if 'main.vm' in files:
        idx = files.index('main.vm')
        f = files.pop(idx)
        print('Translating:', f)
        status = translate_file(f)
        if status == False:
            print('Error translating ', f)
            return False
    else:
        print('Missing main.vm file')
        return False
    
    for f in files:
        print('Translating:', f)
        status = translate_file(f)
        if status == False:
            print('Error translating ', f)
            return False
    
    os.chdir(cwd)
    
    return True

def assemble_final_file(output_file, path):
    """Assemble final output file"""
    intermediate_files = []
    files = os.listdir(path)
    for f in files:
        if f.endswith('.i'):
            intermediate_files.append(f)
            
    cwd = os.getcwd()
    os.chdir(path)
    
    with open(output_file, 'w') as outfile:    
        idx = intermediate_files.index('sys.i')
        f = intermediate_files.pop(idx)
        with open(f, 'r') as infile:
            for line in infile:
                outfile.write(line)
        
        idx = intermediate_files.index('main.i')
        f = intermediate_files.pop(idx)
        with open(f, 'r') as infile:
            for line in infile:
                outfile.write(line)
        
        for f in intermediate_files:
            with open(f, 'r') as infile:
                for line in infile:
                    outfile.write(line)

    os.chdir(cwd)
    return True
    
def clean_intermediate_files(path):
    """Removes intermediate .i files from supplied path"""
    intermediate_files = []
    
    files = os.listdir(path)
    for f in files:
        if f.endswith('.i'):
            intermediate_files.append(f)
            
    cwd = os.getcwd()
    os.chdir(path)
    
    for f in intermediate_files:
        os.remove(f)
    
    os.chdir(cwd)
        
def clean_old_files(path):
    """Removes old files from supplied path"""
    old_files = []
    
    files = os.listdir(path)
    for f in files:
        if f.endswith('.asm') or f.endswith('.i') or f.endswith('.hack'):
            old_files.append(f)
            
    cwd = os.getcwd()
    os.chdir(path)
    
    for f in old_files:
        os.remove(f)
    
    os.chdir(cwd)
    
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python vm_translator_v2.py file-name.asm path-name")
        print("file-name.asm: assembly file to be generated by the translator")
        print("path-name: directory containing .vm source files")
        print("Example: vm_translator_v2.py mult-final.asm ./mult")
    else:
        output_file = sys.argv[1]
        path = sys.argv[2]
        clean_old_files(path)
        
        status = run_vm_to_asm_translator(path)
        if status == True:
            print('Intermediate assembly files were generated successfully');
            print('Generating final assembly file: ', output_file)
            assemble_final_file(output_file, path)
            # clean_intermediate_files(path)
        else:
            print('Error generating assembly code')