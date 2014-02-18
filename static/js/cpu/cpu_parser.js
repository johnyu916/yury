function AssemblyParser(cpu){
    this.cpu = cpu;
    this.insn_length = 0;
}

AssemblyParser.prototype.parseTokens = function(line){
    var tokens = lines[i].split(' ');
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

function WaffleMaker(cpu){
    this.cpu = cpu;
    this.parser = new WaffleParser();
    this.semantics = new WaffleSemantics();
    this.insn_length = 0;
}

WaffleMaker.prototype.parseTokens = function(line){
    text = this.parser.parse(line);
    code = this.semantics.process(text);
    instructions = this.writer.process(code);
    for (int i = 0; i < instructions.length; i++){
        var j = this.insn_length + i;
        this.cpu.memory[j] = instructions[j];
    }
    this.cpu.run()
}
