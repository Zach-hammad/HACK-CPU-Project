//signed multiplication

    @18
    M = 0       //initialize solution to 0
    @17
    D = M   //Get B
    //Determine loop to go to depending on B
    @NEG
    D;JLT   //go to negative loop if B < 0

(POS) //POS handled the same as unsigned
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
    @POS
    0;JMP       //go back

(NEG) //Like positive except increment B and decrement by A
    @17
    D = M       //get B
    @END
    D;JEQ       //end if B == 0
    @16         //get A
    D = M
    @18 
    M = M - D   //set solution to solution - A
    @17
    M = M + 1   //increment B
    @NEG
    0;JMP       //go back

(END)
    @END
    0;JMP