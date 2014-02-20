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
    writer: null,
    insn_length: null
};

function WaffleMakerMake(cpu){
    var maker = object(WaffleMaker);
    maker.cpu = cpu;
    maker.parser = WaffleParserMake();
    maker.semantics = WaffleSemanticsMake();
    maker.writer = WaffleWriterMake();
    maker.insn_length = 0;
    return maker;
}

WaffleMaker.parseTokens = function(line){
    var text = this.parser.parse(line);
    console.log(JSON.stringify(text));
    var code = this.semantics.process(text);
    console.log(JSON.stringify(code));

    //fresh set of insns each time.
    var instructions = this.writer.process(code);
    for (var i = 0; i < instructions.length; i++){
        var j = this.insn_length + i;
        this.cpu.memory[j] = instructions[j];
    }
    // also should write "pause" instruction.
    //this.cpu.run()
}
