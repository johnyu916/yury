function AssemblyParser(cpu){
    this.cpu = cpu;
    this.insn_length = 0;
}

AssemblyParser.prototype.parseTokens = function(tokens){
    var status = {
        code: 0,
        detail: ""
    }
    var insn = tokens_to_insn(tokens);
    if (insn === null){
        status.code = 1;
        status.detail = "Unable to parse instructions";
        return status;
    }
    var integer = insn_to_integer(insn);
    this.cpu.memory[this.insn_length] = integer;
    this.insn_length += 1;
    this.cpu.run_cycle();
    return status;
};
