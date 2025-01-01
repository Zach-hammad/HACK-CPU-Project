//left shift
    @18
    M = 0 //Initialize Solution

(BEGIN)
    @17
    D = M //Get s
    @END
    D;JEQ //all left shift done > goto end
    //else double the value of A and decrement s
    @16
    D = M
    M = M + D
    D = M
    @18
    M = D
    @17
    M = M - 1
    @BEGIN
    0;JMP
(END)
    @END
    0;JMP