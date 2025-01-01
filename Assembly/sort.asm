//sorting algorithm
@17
D = M //set 22 to numelements so we do not modify it (make it a temp variable)
@22
M = D - 1 //1 less to control loop (will not check 1 above last element)
(WHILE)
@18
M = 0 //0 means no swaps made
@19
M = 0 // ivalue
@20
M = 0
@21
M = 0
(LOOP)
//check to exit loop
@19
D = M
@22
D = M - D //(D = numelements - i)
@ENDLOOP
D;JEQ

//get pointer value and check if greater than one above it
@16
D = M //BASE ADDRESS
@19
D = D + M //pointer value
@21
M = D //set pointer in memory
A = M

//with address set, check if greater than index above
D = M
A = A + 1
D = D - M
@19
M = M + 1 //i++
@SWAP
D;JGT
@LOOP
0;JMP
(ENDLOOP)
@18
D = M
@WHILE
D;JGT
@END
0;JMP

//Loop that swaps values if needed
(SWAP)
@18
M = M + 1 //set swapped
@21 //set data to index val
A = M
D = M
@20 //set temp
M = D
@21 //set data to index + 1
A = M + 1
D = M
@21 //set index to D
A = M
M = D
@20 //set D to index val
D = M
@21 //set index + 1 to D
A = M + 1
M = D
@LOOP
0;JMP //end swap, back to loop

(END)
@END
0;JMP