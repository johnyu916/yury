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

var WaffleMaker = {
    cpu: null,
    parser: null,
    semantics: null,
    insn_length: null
};

function WaffleMakerMake(cpu){
    var maker = object(WaffleMaker);
    this.cpu = cpu;
    this.parser = WaffleParserMake();
    this.semantics = WaffleSemanticsMake();
    this.insn_length = 0;
    return maker;
}

WaffleMaker.parseTokens = function(line){
    text = this.parser.parse(line);
    code = this.semantics.process(text);
    instructions = this.writer.process(code);
    for (var i = 0; i < instructions.length; i++){
        var j = this.insn_length + i;
        this.cpu.memory[j] = instructions[j];
    }
    this.cpu.run()
}
