function AssemblyParser(cpu){
    this.cpu = cpu;
    this.insn_length = 0;
}

AssemblyParser.prototype.parseTokens = function(tokens){
    var insn = tokens_to_insn(tokens);
    console.log("insn from token: " + insn);
    var integer = insn_to_integer(insn);
    this.cpu.memory[this.insn_length] = integer;
    this.insn_length += 1;
    this.cpu.run_cycle();
};
