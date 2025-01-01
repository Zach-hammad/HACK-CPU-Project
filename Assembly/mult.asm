//unsigned multiplication

    @18
    M = 0       //initialize solution to 0
(BEGIN)
    @17
    D = M       //get B
    @END
    D;JEQ       //end if B == 0
    @16         //get A
    D = M
    @18 
    M = M + D   //set solution to solution + A
    @17
    M = M - 1   //decrement B
    @BEGIN
    0;JMP       //go back to (BEGIN)
(END)
    @END 
    0;JMP       //Finish