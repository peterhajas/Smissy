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

# Grab all the lines for conversations with the number
# Now, due to the way the message database is saved, we'll need the following:
#  - Just the number, sans country code or country code delimeter:   2345678900
#  - The number with the country code prepended:                    12345678900
#  - Finally, the number with both the country code and delimeter: +12345678900

messages = [ ]

number = sys.argv[1]
query = "select * from message where address=? order by date"

cursor.execute(query, (number,))
for row in cursor:
    messages.append(row)

number = "1" + number
cursor.execute(query, (number,))
for row in cursor:
    messages.append(row)

number = "+" + number
cursor.execute(query, (number,))
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

htmlFile.write("<html>\n")
htmlFile.write("    <head>\n")
htmlFile.write("        <style type=\"text/css\">\n")
htmlFile.write("            body\n")
htmlFile.write("            {\n")
htmlFile.write("                font-family: Helvetica;\n")
htmlFile.write("                max-width: 768px;\n")
htmlFile.write("                margin-left: auto;\n")
htmlFile.write("                margin-right: auto;\n")
htmlFile.write("            }\n")
htmlFile.write("            .message\n")
htmlFile.write("            {\n")
htmlFile.write("                border-radius: 15px 15px;\n")
htmlFile.write("                background-color: #EEE;\n")
htmlFile.write("                border: 1px solid #AAA;\n")
htmlFile.write("                padding: 5px 15px;\n")
htmlFile.write("                margin: 5px;\n")
htmlFile.write("                color: #000;\n")
htmlFile.write("                display: table-cell;\n")
htmlFile.write("                text-shadow: -1px 1px 0px rgba(255,255,255,0.5);\n")
htmlFile.write("                max-width: 70%;\n")
htmlFile.write("                clear:both;\n")
htmlFile.write("            }\n")
htmlFile.write("            .incoming\n")
htmlFile.write("            {\n")
htmlFile.write("                background-image: -webkit-linear-gradient(#FFF, #CCC);\n")
htmlFile.write("                float: left;\n")
htmlFile.write("            }\n")
htmlFile.write("            .outgoing\n")
htmlFile.write("            {\n")
htmlFile.write("                background-image: -webkit-linear-gradient(#CEA, #8B8);\n")
htmlFile.write("                float: right;\n")
htmlFile.write("            }\n")
htmlFile.write("            .date\n")
htmlFile.write("            {\n")
htmlFile.write("                color:#777;\n")
htmlFile.write("                text-align: center;\n")
htmlFile.write("                clear:both;\n")
htmlFile.write("                float: left, right;\n")
htmlFile.write("            }\n")
htmlFile.write("        </style>\n")
htmlFile.write("    </head>\n")
htmlFile.write("    <body>\n")

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
        htmlFile.write("        <div class=\"date\">" + dateString + "</div>\n")

    if not text:
        text = "[MMS / Invalid Entry]"
    else:
        text = text.encode('utf-8')
    
    if message[4] & 1:
        htmlFile.write("        <div class=\"message outgoing\">" + text + "</div>\n")
    else:
        htmlFile.write("        <div class=\"message incoming\">" + text + "</div>\n")

    lastMessageDate = date

# Close the file
htmlFile.close()

# Finally, call open on the file to open it in Safari
command = "open %s" % (filename)
returnValue = subprocess.Popen(command, shell=True)
returnValue.wait()

quit()
