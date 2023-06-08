//getslipAdjustment: b=1 B=1 t=2 T=2
//calcLiquidityUnits: b=1 B=1 t=2 T=2 A=0
contract C{
    uint private one = 1;
    function getSlipAdustment(uint b, uint B, uint t, uint T) public view returns (uint){
        // slipAdjustment = (1 - ABS((B t - b T)/((2 b + B) (t + T))))
        // 1 - ABS(part1 - part2)/(part3 * part4))
        uint part1 = B * t;
        uint part2 = b * T;
        uint part3 = (b * 2) + B;
        uint part4 = t + T;
        uint numerator;
        if(part1 > part2){
            numerator = (part1 - part2);
        } else {
            numerator = (part2 - part1);
        }
        uint denominator = (part3 * part4);
        return one - (numerator * one) / denominator; // Multiply by 10**18
    }
    function calcLiquidityUnits(uint b, uint B, uint t, uint T, uint P) external view returns (uint){
        if(P == 0){
            return b;
        } else {
            // units = ((P (t B + T b))/(2 T B)) * slipAdjustment
            // P * (part1 + part2) / (part3) * slipAdjustment
            uint slipAdjustment = getSlipAdustment(b, B, t, T);
            uint part1 = (t * B);
            uint part2 = (T * b);
            uint part3 = (T * B) * 2;
            uint _units = (((P * part1) + part2) / part3);
            return (_units * slipAdjustment) / one;  // Divide by 10**18
        }
    }
}
