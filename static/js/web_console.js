var KEY_ENTER = 13;
function WebConsole(containerId, onInput){
    this.container = $('#'+containerId);
    this.clickArea = $('<pre></pre>');
    this.container.append(this.clickArea);
    this.clickArea.css("height", "100%");
    this.inputArea = $('<span></span>');
    this.clickArea.append(this.inputArea);
    this.keyboard = $('<textarea></textarea>');
    var empty_div = $('<div></div>');
    empty_div.css({
        width: '1px',
        height: '0px',
        position: 'absolute',
        overflow: 'hidden'
    });
    empty_div.append(this.keyboard);
    this.container.append(empty_div);
    this.container.append('<div/>');

    var that = this;
    this.clickArea.click(function() {
        console.log("this: " + this);
        that.keyboard.focus();
    });
    this.keyboard.keypress(function(event) {
        var key = event.which;
        var text = "";
        if (key === KEY_ENTER){
            //is done.
            that.onInput(that.inputArea.text());
        }
        else{
            text = that.inputArea.text() + String.fromCharCode(key);
        }
        that.inputArea.text(text);

    });

    this.onInput = onInput;
    this.input = "";
}
