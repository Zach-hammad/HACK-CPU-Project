//unsigned division

    @18
    M = 0 //initialize Q to 0
    @19
    M = 0 //set R to 0

(BEGIN)
    @16
    D = M   //get A
    @17     //Data = A - B
    D = D - M
    @END
    D;JLT   //Go to end if A-B < 0
    //Else use this path to decrement A by B and Increment Q
    @17
    D = M   //get B
    @16
    M = M - D   //decrement A by B
    D = M   //Get A
    @19     //set remainder to A
    M = D
    @18
    M = M + 1 //Increment Q
    @BEGIN 
    0;JMP   //Loop Again
(END)
    @END
    0;JMP
