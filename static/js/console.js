var KEY_ENTER = 13;
function WebConsole(containerId, onInput){
    this.container = $('#'+containerId);
    this.clickArea = $('<pre></pre>');
    this.inputArea = $('<span></span>');
    this.clickArea.append(this.inputArea);
    this.keyboard = $('<textarea></textarea>');
    this.container.append(this.clickArea);
    this.container.append('<div/>');
    this.container.append(this.inputListener);

    this.keyboard.keypress(this.onKeyPress);

    this.onInput = onInput;
    this.input = "";
}

WebConsole.prototype.onKeyPress(event){
    var key = event.which;
    var text = "";
    if (key === KEY_ENTER){
        //is done.
        this.onInput(this.inputArea.text());
    }
    else{
      text = this.inputArea.text() + String.fromCharCode(key);
    }
      this.inputArea.text(text);
}
