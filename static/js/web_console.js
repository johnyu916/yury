var KEY_ENTER = 13;
var KEY_BACKSPACE = 8;

var PROMPT = '>';
var CURSOR_COLOR_BLUR = '#cccccc';
var CURSOR_COLOR_FOCUS = '#999999';

function WebConsole(containerId){
    this.container = $('#'+containerId);
    this.clickArea = $('<pre></pre>');
    this.container.append(this.clickArea);
    this.clickArea.css({
        "height": "100%",
        "overflow": "scroll"
    });
    this._newPrompt();
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
        that.keyboard.focus();
    });
    this.keyboard.focus(function() {
        that.cursor.css({
            'background-color': CURSOR_COLOR_FOCUS
        });
    });
    this.keyboard.blur(function(){
        that.cursor.css({
            'background-color': CURSOR_COLOR_BLUR
        });
    });
    this.keyboard.keypress(function(event) {
        var key = event.which;
        var text = that.inputArea.text();
        if (key === KEY_ENTER){
            //is done.
            console.log("enter pressed");
            that.onRead(that.inputArea.text());
            //remove cursor
            that.cursor.remove();
            that._newPrompt();
            //scroll to bottom.
            that._scrollToBottom();
            that.keyboard.focus();
        }
        else{
            text += String.fromCharCode(key);
            that.inputArea.text(text);
        }

    });
    this.keyboard.keydown(function(event) {
        var key = event.which;
        var text = that.inputArea.text();
        if (key === KEY_BACKSPACE){
            text = text.substr(0, text.length-1);
            that.inputArea.text(text);
        }
    });

    this.input = "";
    this.onRead = null;
}

WebConsole.prototype._scrollToBottom = function() {
    // scrollHeight gives total area inside the border (so includes padding).
    // innerHeight is the viewable area inside the border.
    var height = this.clickArea.prop('scrollHeight') - this.clickArea.innerHeight();
    this.clickArea.scrollTop(height);
};


WebConsole.prototype._newPrompt = function(){
    this.inputContainer = $('<div></div>');
    this.inputArea = $('<span></span>');
    this.prompt = $('<span>> </span>');
    this.cursor = $('<span> </span>');
    this.cursor.css({
        'background-color': CURSOR_COLOR_BLUR
    });
    this.inputContainer.append(this.prompt);
    this.inputContainer.append(this.inputArea);
    this.inputContainer.append(this.cursor);
    this.clickArea.append(this.inputContainer);
};

WebConsole.prototype.write = function(text){
    var output = $('<div>'+ text + '</div>');
    this.clickArea.append(output);
};
