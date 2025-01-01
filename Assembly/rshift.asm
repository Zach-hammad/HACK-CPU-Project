//Right Shift
    @18
    M = 0 //Initialize Solution

    @15
    M = 0 //used for division
    M = M + 1
    M = M + 1

(START)
    @17
    D = M //Get s
    @END
    D;JEQ //done if s == 0
    //else here we divide by 2 then decrement s
    @18
    M = 0 //clear this for division
    @DIVLOOP
    0;JMP
(DONEDIV)
    @17
    M = M - 1 //decrement
    @18
    D = M
    @16
    M = D //Set A to new Quotient
    @START
    0;JMP

//used to divide A by two
//will use reg 15 as the 2 like B, and A will be modified in place then rewritten
(DIVLOOP)
    @16
    D = M   //get A
    @15
    D = D - M
    @DONEDIV
    D;JLT   //Go to end
    //Else use this path to decrement A by B and Increment Q
    @15
    D = M   //get B
    @16
    M = M - D   //decrement A by B
    D = M   //Get A
    @18
    M = M + 1 //Increment Q
    @DIVLOOP 
    0;JMP   //Loop Again

(END)
    @END
    0;JMP