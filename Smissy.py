# Copyright (c) 2011, Peter Hajas
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this list of conditions and
# the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the
# distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Smissy, a utility for visualizing logs on your phone.
# Just run with a phone number and area code, like this:
# $ python Smissy.py 2345678900
# and Smissy will make an HTML file for you in the current directory and open it

import sqlite3
import sys
import os
import subprocess
import datetime
from operator import itemgetter, attrgetter

# Check arguments
if len(sys.argv) < 2:
    print "Please run Smissy with a number, including area code."
    print "For example, 2345678900 for the number 1-(234)-567-8900"
    quit()

pathToBackups = "~/Library/Application Support/MobileSync/Backup/"
pathToBackups = os.path.expanduser(pathToBackups)

# Find all the directories that have the SMS backup file (3d0d7e5fb2ce288813306e4d4636395e047a3d28) in them
# We'll use these to find the largest SMS backup file

directoriesContainingSMSBackups = [ ]
largestBackupBytes = 0
largestBackupAbsolutePath = ""

for directory in os.listdir(pathToBackups):
    pathToBackupFile = pathToBackups + directory + "/" + "3d0d7e5fb2ce288813306e4d4636395e047a3d28"
    if os.path.exists(pathToBackupFile):
        directoriesContainingSMSBackups.append(directory)
        if os.path.getsize(pathToBackupFile) > largestBackupBytes:
            largestBackupBytes = os.path.getsize(pathToBackupFile)
            largestBackupAbsolutePath = pathToBackupFile

# Now that we have the largest SMS backup that they have, we'll load the database

connection = sqlite3.connect(largestBackupAbsolutePath)
cursor = connection.cursor()

# Grab all the lines for conversations with the given number suffix
messages = [ ]

number = sys.argv[1]
query = "select * from message where address like ? order by date"

cursor.execute(query, ("%{0}".format(number),))
for row in cursor:
    messages.append(row)

if len(messages) == 0:
    print "No messages found for that number"
    exit()

# Sort by time (the 2 index in the database row)

sortedMessages = sorted(messages, key=itemgetter(2))

# A fake last message date, to make output more sanitary

lastMessageDate = datetime.datetime.fromtimestamp(0)

# Create the html file, and write the CSS and html beginnings to it

filename = os.getcwd() + "/" + sys.argv[1] + ".html"
htmlFile = open(filename, 'w')

htmlFile.write("""
<html>
    <head>
        <style type='text/css'>
            body
            {
                font-family: Helvetica;
                max-width: 768px;
                margin-left: auto;
                margin-right: auto;
            }
            .message
            {
                border-radius: 15px 15px;
                background-color: #EEE;
                border: 1px solid #AAA;
                padding: 5px 15px;
                margin: 5px;
                color: #000;
                display: table-cell;
                text-shadow: -1px 1px 0px rgba(255,255,255,0.5);
                max-width: 70%;
                clear:both;
            }
            .incoming
            {
                background-image: -webkit-linear-gradient(#FFF, #CCC);
                float: left;
            }
            .outgoing
            {
                background-image: -webkit-linear-gradient(#CEA, #8B8);
                float: right;
            }
            .date
            {
                color:#777;
                text-align: center;
                clear:both;
                float: left, right;
            }
        </style>
    </head>
    <body>""")

for message in sortedMessages:

    if message[4] & 1:
        sender = "You"
    else:
        sender = "Them"

    date = datetime.datetime.fromtimestamp(message[2])

    text = message[3]

    # If more than 15 minutes have passed, show the date

    delta = date - lastMessageDate
    if delta.seconds > 600:
        dateString = date.strftime('%b %d, %Y %I:%M')
        htmlFile.write("        <div class='date'>" + dateString + "</div>\n")

    if not text:
        text = "[MMS / Invalid Entry]"
    else:
        text = text.encode('utf-8')

    if message[4] & 1:
        htmlFile.write("        <div class='message outgoing'>" + text + "</div>\n")
    else:
        htmlFile.write("        <div class='message incoming'>" + text + "</div>\n")

    lastMessageDate = date

htmlFile.write("""
    </body>
</html>""")

# Close the file
htmlFile.close()

# Finally, call open on the file to open it in the default browser
os.system("open {0}".format(filename))
