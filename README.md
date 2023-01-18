# zoneminder-controlcenter
zoneminder-controlcenter is a simple text user interface that allows you to view and change the run state of your ZoneMinder video surveillance system. It is meant to be run on a small computer like a Raspberry Pi with a small display and keypad placed in a convenient location. It requires you to set a PIN that the user must enter in order to change the run state.

## Requirements
* ZoneMinder with API version 2.0 enabled (tested on ZoneMinder version 1.36.32)
* Python 3

## Usage
From the source directory, start up the user interface like this:
`./zm_controlcenter <server>

where <server> is the address of your ZoneMinder server, probably a LAN address (e.g. http://192.168.XX.YY). You will then be asked to enter your ZoneMinder username, password, and a PIN that a user will have to match in order to change the run state. Username, password, and PIN can optionally be specified on the command line instead.

## Security considerations
It is recommended not to store your ZoneMinder password or the zoneminder-controlcenter PIN in plain text. If you want to start zoneminder-control center automatically, it is best to store this information in an encrypted file and have the calling process decrypt it and pass the information to zm_controlcenter.

## Screenshots and images
![alt tag](https://raw.githubusercontent.com/montagdude/zoneminder-controlcenter/master/images/screenshot-1.jpg)
![alt tag](https://raw.githubusercontent.com/montagdude/zoneminder-controlcenter/master/images/screenshot-2.jpg)
