//game has objects and their machines.

function GameBot{
    this.machine; //machine that runs
    this.name;
}

function GameObject{
    this.gamebot;
    this.box; //boundary box for collision stuff
    this.view; //appearance.
}

