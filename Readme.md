Smissy, an SMS visualizer for iOS backups
=========================================

by Peter Hajas

About
-----

Smissy is a simple python tool for visualizing your iOS SMS database backups.

You pass Smissy a phone number (more on this later). With that phone number,
Smissy generates an HTML file with the conversation you've had with that
number. Messages you've sent are shown in green, and messages you've received
are shown in gray. If there's been more than 10 minutes between two messages,
a string showing the date is shown.

Smissy only shows what's in your backup, so make sure you've backed up your
device to iTunes!

Smissy currently only runs on OS X.

Usage
-----

Simply run Smissy with a phone number, including area code. For example:

`python Smissy.py 2345678900`

and Smissy will take care of the rest. After the HTML file has been created, it
will automatically open in your default browser.

Smissy logs are best viewed in Safari or Chrome.

Legal
-----

Smissy is Copyright 2011 Peter Hajas. It's BSD licensed. The full text of the
license can be found in Smissy.py.

The work in Smissy does not imply endorsement by past, current or future
employers.

