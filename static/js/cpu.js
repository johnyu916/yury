/*
 * CPU class.
 */
function CPU(args){
    var log_rows = args['STORAGE']['ROWS'];
    var log_cols = args['STORAGE']['COLUMNS'];
    var rows = Math.pow(2, log_rows);
    var cols = Math.pow(2, log_cols);
    var log_insns = args['STORAGE']['INSTRUCTIONS'];
    var insns = Math.pow(2, log_insns);

    this.storageSize = rows*cols;
    this.logStorageSize = log_rows+log_cols;
    this.instructionsSize = insns;
    this.logInstructionSize = log_insns;
    this.storage = new Array();
    this.instructions = new Array();
    this.instructionCodes = [
        {
            'name': 'STORE',
        },
        {
            'name': 'BRANCH',
        }
    ]
    this.logInstructionCodesSize = log2(this.instructionCodes.length);
    this.program_counter = 0; // current instruction location
    this.status = "RUNNING";
    this.interval = null; // setInterval variable to run periodically.
    function getStorageSize(){
        return this.storageSize;
    }
}


function cpu_run_instruction(cpu){
    if (cpu.program_counter >= cpu.instructions.length) return;

    var insn = cpu.instructions[cpu.program_counter];
    var index = 0;
    var insnCode = binaryToDecimal(insn, index, cpu.logInstructionCodesSize);
    index += cpu.logInstructionCodesSize;
    var storage_location = binaryToDecimal(insn, index, cpu.logStorageSize);
    index += cpu.logStorageSize;
    //insn is a boolean array
    var insnName = cpu.instructionCodes[insnCode].name;
    if (insnName == 'BRANCH'){
        var value = cpu.storage[storage_location];
        if (value){
            insn_location = binaryToDecimal(insn, index, cpu.logInstructionSize);
            cpu.program_counter = insn_location;
        }
    }
    else if (insnName == 'STORE'){
        var value = binaryToDecimal(insn, index, 1);
        cpu.storage[storage_location] = value;
        cpu.program_counter += 1;
    }
}

function cpu_run_cycle(cpu){
    console.log("running single cpu cycle");
    if (cpu.program_counter >= cpu.instructions.length){
        clearInterval(cpu.interval);
        return;
    }
    cpu_run_instruction(cpu);
}

function cpu_run(cpu, sleep_ms){
    // read instructions. TODO: do this at every instruction rather than here.
    $('.instruction').each(function( index ){
        //extract
        var instrutionType = $('.instruction-type option:selected', this).text();
        var instruction = new Array();
        instruction.push(instructionType);
        $('.read-location', this).each(function( index){
            var location = $(this, 'option:selected').text();
            instruction.push(location);
        });
        if (instructionType == 'Store'){

            var writeValue = $('.write-value option:selected', this).text();
            instruction.push(writeValue);
        }
        else{
            $('.branch-location', this).each(function(index){
                var location = $(this, 'option:selected').text();
                instruction.push(location);
            });
        }
        cpu.instructions.push(instruction);
    });

    // schedule
    cpu.interval = setInterval(cpu_run_cycle(cpu), sleep_ms);
}

function cpu_stop(cpu){
    cpu.program_counter = cpu.instructions.length;
}

//utility functions.
function log2(number){
    return Math.log(number)/Math.log(2);
}

function binaryToDecimal(array, begin, size){
    var value = 0;
    var multiplier = 1;
    for (var i = begin; i < begin+size; i++){
        if (array[i]) value += multiplier;
        multiplier *= 2;
    }
    return value;
}

function new_instruction(){
    //add instruction by copying an existing instruction
    var template = $('.instruction-template');
    var clone = template.clone();
    clone.removeClass('instruction-template');
    clone.addClass('instruction');
    clone.appendTo('#instructions');
    
    $('.write-div', clone).hide();
    $('.branch-div', clone).hide();
    $('.instruction-type', clone).change(function(){
        var type = $(this).val();
        console.log('type: '+type);
        
        if (type == 'Store'){
            $('.write-div', clone).show();
            $('.branch-div', clone).hide();
        }
        else{
            $('.write-div', clone).hide();
            $('.branch-div', clone).show();
        }
        
    });
    
}

// input handlers
$(document).ready(function() {
    // Handler for .ready() called.
    var args = $('#cpu-info').data('cpu');
    var data = jQuery.parseJSON(args.replace(/'/g, '"'))
    var cpu = new CPU(data);
    var cpuSpeed = 1000;
    $('#run-cpu').click(function(){
        console.log("running cpu");
        cpu_run(cpu, cpuSpeed);
    });

    $('#stop-cpu').click(function(){
        console.log("stopping cpu");
        cpu_stop(cpu);
    });

    $('#new-instruction').click(function(){
        console.log("new instruction");
        new_instruction(cpu);
    });

    
   
});
