//signed division

    @18
    M = 0 //initialize Q to 0
    @19
    M = 0 //set R to 0
    
    //If A is negative, go to negative loop
    @16
    D = M
    @NEG
    D;JLT

//A >= 0, just do it normally
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

(NEG)
    //Modify A to be positive of itself
    @16
    D = M
    M = M - D
    M = M - D
    //Do division normally
(START)
    @16
    D = M   //get A
    @17     //Data = A - B
    D = D - M
    @MODEND //goto modified ender
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
    @START 
    0;JMP   //Loop Again

(MODEND) //modified ender for a negative A
    @19
    D = M //get R
    @REMZERO
    D;JEQ 
    //else Q = -Q - 1, R = B - R
    //negate Q
    @18
    D = M
    M = M - D
    M = M - D
    M = M - 1
    @17
    D = M //Get B
    @19
    M = D - M
    @END
    0;JMP

(REMZERO) //if R == 0 then Q = -Q, R = 0
    //negate Q
    @18
    D = M
    M = M - D
    M = M - D
    @END
    0;JMP

(END)
    @END
    0;JMP