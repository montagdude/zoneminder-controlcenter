import curses_dialog
import time

class CC_Console:
    def __init__(self, zmapi, pin, refresh=25, incorrect_pin_timeout=2):
        '''Displays a user interface for changing the ZoneMinder runstate.
           zmapi: ZMAPI instance. You need to login/logout outside of this class.
           pin: entry required to change the runstate when user interacts with the dialog.
           refresh: how frequently to check the runstate and refresh the display, in seconds. This
                    is also the timeout for pin entry. Acceptable range is 5-25.
           incorrect_pin_timeout: how long to wait after an incorrect PIN entry before displaying
                                  the menu again'''
        self.zmapi = zmapi
        self.pin = pin
        timeout = int(refresh*10)   # Curses half-delay is in tenths of a second
        timeout = min(max(50, timeout), 250)
        self.incorrect_pin_timeout = incorrect_pin_timeout
        self.dialog = curses_dialog.Dialog(timeout)

    def execute(self):
        '''Main control loop'''

        while True:
            runstates, response = self.stateDialog()
            try:
                stateidx = int(response)-1
                if stateidx in range(0, len(runstates)):
                    response = self.pinEntryDialog()
                    if response == self.pin:
                        self.dialog.writeMessage("Please wait...")
                        check = self.zmapi.changeRunState(runstates[stateidx]["name"])
                    else:
                        self.dialog.writeMessage("Incorrect PIN!")
                        time.sleep(self.incorrect_pin_timeout)
            except ValueError:
                pass

    def stateDialog(self):
        '''Displays a dialog showing ZoneMinder's state and gets user input'''

        title = "ZoneMinder Control Center"

        # Info lines
        runstates, active = self.getRunStates()
        running = self.zmapi.getDaemonStatus()
        if running:
            statusline = "ZoneMinder is running in {:s} mode.".format(active)
        else:
            statusline = "ZoneMinder is stopped."
        runstatelines = ["Available run states:"]
        for i, runstate in enumerate(runstates):
            runstatelines.append("{:d}: {:s}".format(i+1, runstate["name"]))
        lines = [statusline, ""] + runstatelines

        prompt = "Enter new run state (1-{:d}):".format(len(runstates))

        # Display the dialog and return the response
        response = self.dialog.execute(title, lines, prompt, echo_mode="On")
        return runstates, response

    def getRunStates(self):
        '''Builds a list of runstates. Returns the list and the name of the active runstate.'''

        # Get runstates and append a 'stop' state since this isn't provided by the API
        runstates = self.zmapi.getRunStates()
        runstates.append({"id": -1, "name": "stop", "active": False})
        active = None
        for runstate in runstates:
            if runstate["active"]:
                active = runstate["name"]
                break

        return runstates, active

    def pinEntryDialog(self):
        '''Displays the pin entry dialog'''

        title = "PIN Entry"
        prompt = "Enter PIN:"
        lines = ["PIN is required to change run state.", ""]
        return self.dialog.execute(title, lines, prompt, echo_mode="*", bottom_prompt=False)
