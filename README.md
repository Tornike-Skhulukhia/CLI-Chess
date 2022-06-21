# CLI CHESS / Command line based Chess with Python

![Image](./static/draft_image.png)

# What is it?
This is the cutest Chess I have ever played in the command line.

# Why does it exist?
To play directly or use as a standalone basic chess engine

# How to install?
If you plan to just Play it, the only requirement will be rich
```bash
python3 -m pip install rich
```
If you would like to continue development and run tests, also some type of pgn parser would be beneficial for chess notation loading functionality, ex:
```bash
python3 -m pip install git+https://github.com/renatopp/pgnparser
```

# How to play?


## using 1 player
## using 2 players

### special types of moves
. Castling  
. En passant  
. Pawn promotion  

### what you can do with it?

## Currently Known bugs
None

## Things that are not implemented
. Stalemate and draw - I think for now they were not necessary, but can be added in the future

## running tests

## contribution

## license


# When playing, make sure to increase font size and change settings to make board more square-like if needed.


. Maybe add some kind of historical info live visibility like famous players that had similar situations and some link or small info, if game is started in this specific info-ish mode, which can make game a bit more funny  

# how moves work
. some explanation
. special cases explanations, like castling - using O-O (O-s, not zeros) or O-O-O for short/long castling, plus using just basic notation for only king movement


# todo after basic functionalities
. add info how to run multiplayer and singleplayer games on local and local + server + other cases
. remove breakpoints and unnecessary commented parts of code 
. add good docs for each functions about their input/output and functionalities/roles
. ability to play using 2 different computers on same network using IP sharing
. add logging for different levels of info that can be controlled with just pytho logging module to have more idea about debug info if needed
. make sure debug info is printed when needed(maybe always should be the default?)
. maybe also add functionality for messages when loading to show who win even without checkmate when having notation like 1-0 (not not very important for now)

# how to play, supported moves e.t.c


# how to run tests
. ex: python -m tests.test_pawn

# other
. for castling, moving king 2 places is enough, and even in chess notation
if it is written that way and not O-O for example, it will load it and store as O-O move
. currently no draws and stalemates are implemented in game logic, but can be implemented easily using existing functionality. So, you still need to know what you are doing do play chess here :)
. pawn promotion notation ex: "E7 E8=Q" , "E7 F8=K" to make pawn Queen and Knight accordingly


# errors ?
. do colors show up properly? after installing some old package on my PC, it stopped
working on terminal until doing apt update and apt upgrade, then worked again only in terminal, not in vscode terminal.

# installation
. for usage
. for testing  
    . also install https://github.com/renatopp/pgnparser from github directly:
        ```bash
        python3 -m pip install git+https://github.com/renatopp/pgnparser
        ```

