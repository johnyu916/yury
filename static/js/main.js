/* Boot sequence:
 * 1. load environment
 * 2. load machines.
 * 3. fire events to loop.
 * 4. game needs its own configuration.
 * all ncessary files are received from the web.
 * but you can also just play online if you want.
 */

var gamebots = [];

function load(){
    //load memory for gamebots

    //turn on the gamebots
}

function game(){
    //one 'turn'
    for (gamebot in gamebots){
        gamebot.machine.run() //run once
    }
    //process any actions that gamebot wants

    //do physics and game logic update.
    physics();
    gamelogic();
}

/* let's say there are 2 games, pong and galaga.
 */
function ready(){

}

