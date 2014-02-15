
function CPUView(containerId, cpu){
    this.container = $('#'+ containerId);
    this.cpu = cpu;

    this.processor = $('<div></div>');
    this.set_processor_content();
    this.container.append(this.processor);

    //memory next.
    this.memory = $('<div></div>');
    var memory_length = cpu.memory.length;
    this.memory.append($("<div>Memory: " + memory_length *4 + " bytes</div>"));
    this.memory_position = memory_length;
    this.memory_show_size = 16;

    this.memory_content = $('<div></div>');
    this.set_memory_content();
    this.memory.append(this.memory_content);
    this.memory_input = $('<div></div>');
    this.input_position = $('<input type="text"></input>');
    var button = $('<button>Click</button>');

    var that = this;
    button.click(function(){
        that.memory_position = parseInt(that.input_position.val());
        that.refresh();
    });
    this.memory_input.append(this.input_position);
    this.memory_input.append(button);
    this.memory.append(this.memory_input);
    this.container.append(this.memory);
  }

CPUView.prototype.set_memory_content = function(){
    this.memory_content.empty();
    var position = this.memory_position;
    console.log("cpu position: "+position);
    for (var i = position; i < position + this.memory_show_size; i+=1){
      var byte_array = integer_to_byte_array(this.cpu.memory[i]);
        this.memory_content.append("<div>" + i*4 + " " + byte_array + "    (" + this.cpu.memory[i] + ")" + "</div>");
    }
};

CPUView.prototype.set_processor_content = function(){
    this.processor.empty();
    var texts = [];
    texts.push("<div>PC: " + this.cpu.pc + "</div>");
    var insn_str = ass_insn(integer_to_insn(this.cpu.memory[this.cpu.pc/4]));
    texts.push("<div>Next instruction: " + insn_str +'</div>');
    texts.push("<table> ");
    for (var i = 0; i < this.cpu.registers.length; i+=8){
      texts.push("<tr>")
      for (var j = 0; j < 8; j +=1){
        texts.push("<td style='border: 1px solid black'>" + "Register " + (i+j) + "</td>");
      }
      texts.push("</tr><tr>")
      for (var j = 0; j < 8; j +=1){
        texts.push("<td style='border: 1px solid black'>" + this.cpu.registers[i+j] + "</td>");
      }
      texts.push("</tr>");
    }
    texts.push("</table>");
    this.processor.html(texts.join('\n'));
};

CPUView.prototype.refresh = function(){
    console.log("refresh called. cpu 5: " +this.cpu.registers[5]);
    this.set_processor_content();
    this.set_memory_content();
};
