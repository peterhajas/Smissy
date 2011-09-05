#!/usr/bin/env python

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
# When run, Smissy will automatically open your default browser:
# $ python Smissy.py

import sqlite3
import sys
import os
import datetime
import time
import BaseHTTPServer
import re
import json
from collections import defaultdict
from operator import itemgetter, attrgetter

PORT_NUMBER = 8080

pathToBackups = "~/Library/Application Support/MobileSync/Backup/"
pathToBackups = os.path.expanduser(pathToBackups)

staticCache = {}

def load_static_file(filename):
    file = open(filename, "r")
    staticCache[filename] = file.read()
    file.close()

def serve_static_file(s, path, filename, mime):
    if s.path == path:
        s.send_response(200)
        s.send_header("Content-type", mime)
        s.end_headers()
        if not filename in staticCache:
            load_static_file(filename)
        s.wfile.write(staticCache[filename])
        return True
    return False

def find_backup():
    # Find all the directories that have the SMS backup file (3d0d7e5fb2ce288813306e4d4636395e047a3d28) in them
    # We'll use these to find the largest SMS backup file

    directoriesContainingSMSBackups = [ ]
    largestBackupBytes = 0
    largestBackupAbsolutePath = ""

    for directory in os.listdir(pathToBackups):
        pathToBackupFile = os.path.join(pathToBackups, directory, "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        if os.path.exists(pathToBackupFile):
            directoriesContainingSMSBackups.append(directory)
            if os.path.getsize(pathToBackupFile) > largestBackupBytes:
                largestBackupBytes = os.path.getsize(pathToBackupFile)
                largestBackupAbsolutePath = pathToBackupFile

    # Now that we have the largest SMS backup that they have, we'll load the database

    connection = sqlite3.connect(largestBackupAbsolutePath)
    cursor = connection.cursor()

    return cursor

def lookup_messages(number):
    query = "select text,date,flags from message where address like ? order by date"

    # Grab all the lines for conversations with the given number suffix

    cursor.execute(query, ("%{0}".format(number),))
    messages = cursor.fetchall()

    if len(messages) == 0:
        return []

    # Sort by time (the 1 index in the database row)

    sortedMessages = sorted(messages, key=itemgetter(1))

    messageObject = []

    for message in sortedMessages:
        text = message[0]

        if not text:
            text = "[MMS / Invalid Entry]"
        else:
            text = text.encode('utf-8')

        messageObject.append([message[2] & 1, text, message[1]])

    return messageObject

def list_conversations():
    cursor.execute("select address from message")
    addresses = defaultdict(int)
    for address in cursor:
        address = address[0]
        if address:
            # Remove uninteresting characters (non-digits)

            address = re.sub("[^0-9]", "", address)

            # Strip area code
            # This could cause collisions, but it seems unlikely,
            # or more likely that they're useful collisions

            if len(address) > 7:
                address = address[-7:]

            addresses[address] += 1
    return [[k,v] for k,v in addresses.iteritems() if k and v]

class SmissyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        if (serve_static_file(s, "/", "index.html", "text/html") or
            serve_static_file(s, "/jquery.js", "jquery.js", "application/x-javascript") or
            serve_static_file(s, "/noisy.js", "noisy.js", "application/x-javascript") or
            serve_static_file(s, "/date.js", "date.js", "application/x-javascript")):
            return

        conversationRequest = re.match(r"\/conversation\/([0-9]+)$", s.path)
        if conversationRequest:
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps(lookup_messages(conversationRequest.group(1))))
            return

        conversationIndexRequest = re.match(r"\/conversation\/?$", s.path)
        if conversationIndexRequest:
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps(list_conversations()))
            return

        s.send_response(404)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("Unknown resource.")

if __name__ == '__main__':
    global cursor
    cursor = find_backup()

    httpd = BaseHTTPServer.HTTPServer(("", PORT_NUMBER), SmissyHandler)
    print time.asctime(), "Server Starts - Port {0}".format(PORT_NUMBER)
    # Open the interface in the default browser
    os.system("open {0}".format("http://localhost:{0}".format(PORT_NUMBER)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - Port {0}".format(PORT_NUMBER)

