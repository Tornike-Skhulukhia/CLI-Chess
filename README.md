# CLI CHESS/Command line based Chess

![Image](./static/draft_image.png)


# this readme is draft, still in development

# When playing, make sure to increase font size and change settings to make board more square-like. On Linux mint terminal for example, this can be done using  Edit -> Preferences -> Cell -> Text Spacing . (1.8-2 seems good enough)


. Maybe add some kind of historical info live visibility like famous players that had similar situations and some link or small info, if game is started in this specific info-ish mode, which can make game a bit more funny  

# how moves work
. some explanation
. special cases explanations, like castling - using O-O (O-s, not zeros) or O-O-O for short/long castling, plus using just basic notation for only king movement


# todo after basic functionalities
. remove breakpoints and unnecessary commented parts of code 
. add good docs for each functions about their input/output and functionalities/roles
. ability to play using 2 different computers on same network using IP sharing


# how to run tests
. ex: python -m tests.test_pawn

# other
. for castling, moving king 2 places is enough, and even in chess notation
if it is written that way and not O-O for example, it will load it and store as O-O move

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

