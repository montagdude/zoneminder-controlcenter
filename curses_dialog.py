import sys
import curses
import signal
from curses import ascii

DIALOG_TIMEOUT = "__timeout__"

def sigint_handler(sig, frame):
    pass

class Dialog:
    def __init__(self, timeout=None):
        '''Displays an input dialog with curses and returns the result. Parameters:
           timeout: half-delay timeout, in tenths of a second. Use None for no timeout.
              Returns the string DIALOG_TIMEOUT when timeout occurs.'''

        stdscr = curses.initscr()
        # In principle, we could display this dialog in a different window than stdscr, but that is
        # not implemented.
        self.win = stdscr
        curses.noecho()

        # These two things should prevent Ctrl-C from interrupting the program
        curses.raw()        # More usual option is curses.cbreak()
        signal.signal(signal.SIGINT, sigint_handler)

        # This sets a timeout when getting input, in tenths of a second (max 255)
        if timeout is not None:
            curses.halfdelay(min(timeout,255))
        self.win.keypad(True)

        # Drawing position
        self.y = 0
        self.x = 0

    def cleanup(self):
        #curses.nocbreak()      # Don't need this because we're in raw mode
        self.win.keypad(False)
        curses.echo()
        curses.endwin()

    def execute(self, title, lines, prompt, echo_mode="On", bottom_prompt=True):
        '''Displays an interactive dialog and returns the response.
           echo_mode: must be one of "On" or "*".
              "On" displays response that the user types
              "*" obscures the response with asterisks
           bottom_prompt: Controls whether the prompt is located at the bottom of the window
                          or directly below the info lines.'''

        if not echo_mode in ["On", "*"]:
            sys.stderr.write("echo_mode must be 'On' or '*'.\n")
            sys.exit(1)

        self.draw(title, lines, prompt, bottom_prompt)
        response = ""
        xpos=None

        while True:
            response, special_key = self.getInput(chars=response, xpos=xpos, echo_mode=echo_mode)
            if special_key == "__resize__":
                xpos = self.x
                self.draw(title, lines, prompt, bottom_prompt)
            elif special_key == DIALOG_TIMEOUT:
                response = special_key
                break
            else:
                break
        return response

    def getPosition(self):
        pos = self.win.getyx()
        self.y = pos[0]
        self.x = pos[1]

    def draw(self, title, lines, prompt, bottom_prompt=True):
        '''Redraws the dialog'''
        prevx = self.x
        wsize = self.win.getmaxyx()
        self.rows = wsize[0]
        self.cols = wsize[1]
        self.win.clear()

        # Draw window border
        self.win.border()
        self.win.addch(2, 0, curses.ACS_LTEE)
        self.win.addch(2, self.cols-1, curses.ACS_RTEE)
        for i in range(1, self.cols-1):
            self.win.addch(2, i, curses.ACS_HLINE)

        # Draw centered bold title
        self.y = 1
        self.x = round(self.cols/2. - len(title)/2.)
        self.win.attron(curses.A_BOLD)
        self.win.addstr(self.y,self.x,title)
        self.win.attroff(curses.A_BOLD)

        # Print lines
        self.y = 3
        self.x = 1
        self.win.move(self.y,self.x)
        for line in lines:
            self.win.addstr(self.y,self.x,line)
            self.y += 1

        # Print prompt
        if bottom_prompt:
            self.y = self.rows-2
        self.win.addstr(self.y, self.x, prompt + " ")
        self.getPosition()
        self.win.refresh()

    def getInput(self, chars="", xpos=None, echo_mode="On"):
        '''Gets user input. Also returns any key that requires special handling.'''
        special_key = None

        # Save the current x position -> this is the farthest left we can move
        beg = self.x

        # Print the given chars
        self.printResponse(beg, chars, echo_mode=echo_mode)

        # Move the cursor to a saved location
        if xpos is not None:
            if xpos >= beg and xpos <= beg+len(chars):
                self.x = xpos
                self.win.move(self.y, self.x)

        while True:
            char = self.win.getch()

            # Timeout
            if char == -1:
                special_key = DIALOG_TIMEOUT
                break

            # Enter key
            elif char == curses.KEY_ENTER or char == 10:
                break

            # Resize window
            elif char == curses.KEY_RESIZE:
                special_key = "__resize__"
                break

            # Navigation keys
            elif char == curses.KEY_LEFT:
                if self.x > beg:
                    self.win.move(self.y, self.x-1)
                    self.x -= 1
            elif char == curses.KEY_RIGHT:
                if self.x < beg+len(chars):
                    self.win.move(self.y, self.x+1)
                    self.x += 1
            elif char == curses.KEY_HOME:
                self.win.move(self.y, beg)
                self.x = beg
            elif char == curses.KEY_END:
                self.win.move(self.y, beg+len(chars))
                self.x = beg+len(chars)

            # Backspace and delete
            elif char == curses.KEY_BACKSPACE or char == 127:
                if self.x > beg:
                    self.x -= 1
                    idx = self.x-beg
                    chars = self.removeFromString(chars, idx)
                    self.printResponse(beg, chars, return_x=True, echo_mode=echo_mode)
            elif char == curses.KEY_DC:
                if self.x < beg+len(chars):
                    idx = self.x-beg
                    chars = self.removeFromString(chars, idx)
                    self.printResponse(beg, chars, return_x=True, echo_mode=echo_mode)

            # Printable ascii characters
            elif ascii.isprint(char):
                chars += ascii.unctrl(char)
                if echo_mode == "On":
                    self.win.addch(self.y, self.x, char)
                    self.x += 1
                elif echo_mode == "*":
                    self.win.addstr(self.y, self.x, "*")
                    self.x += 1

        return chars, special_key

    def printResponse(self, beg, response, return_x=True, echo_mode="On"):
        '''Prints the response that we have so far and optionally returns the cursor to its previous
          position'''
        prevx = self.x
        self.win.move(self.y, beg)
        self.clrtoeol()
        if echo_mode == "On":
            self.win.addstr(self.y, beg, response)
        elif echo_mode == "*":
            self.win.addstr(self.y, beg, len(response)*"*")
        self.getPosition()
        if return_x:
            self.x = prevx
            self.win.move(self.y, self.x)

    def removeFromString(self, string, idx):
        '''Returns a new string with the character at index idx removed'''
        newstring = string
        if idx >= 0 and idx < len(string):
            newstring = string[0:idx] + string[idx+1:]
        return newstring

    def clrtoeol(self):
        '''Clears to the end of the line and redraws erased right border'''
        pos = self.win.getyx()
        y = pos[0]
        x = pos[1]
        self.win.clrtoeol()
        self.win.addch(y, self.cols-1, curses.ACS_VLINE)
        self.win.move(y,x)

    def writeMessage(self, message):
        '''Clears the window and writes a simple message.'''
        self.win.clear()
        self.win.addstr(0,0, message)
        self.win.refresh()
