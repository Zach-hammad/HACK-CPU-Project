// Author: Naga Kandasamy

load Computer.hdl,
output-file ComputerMult.out,
// compare-to ComputerAdd.cmp,
output-list time%S1.4.1 reset%B2.1.2 ARegister[0]%D1.7.1 DRegister[0]%D1.7.1 PC[]%D0.4.0 RAM16K[0]%D1.7.1 RAM16K[1]%D1.7.1 RAM16K[2]%D1.7.1;

// Load a program written in the Hack machine language.
// The program multiplies two constants 5 and 10 and writes the result in RAM[0]. 
ROM32K load mult.hack,
output;

// Run program for 150 CPU cycles
repeat 150 {
    tick, tock, output;
}