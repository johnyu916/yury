function AssemblyParser(cpu){
    this.cpu = cpu;
}

function Assembly.prototype.parseTokens(tokens){
    parse_tokens(tokens);
}
