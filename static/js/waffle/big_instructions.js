var BigInstruction = {};

BigInstruction.set_int = function(register_no, value){
    return set_insn(register_no, value);
}
BigInstruction.subtract_int= function(dest, one, two){
    return subtract_insn(dest, one, two);
}
