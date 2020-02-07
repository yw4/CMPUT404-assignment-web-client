#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        try:
            if port is None:
                port = 80
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except (socket.error,msg):
            print('Failed to create socket. Error code:,')
            sys.exit()
        print("Socket created successfully")
        return self.socket

    def get_code(self, data):
        if not data:
            return None
        return int(data.split(' ')[1])

    def get_headers(self,data):
        if not data:
            return None
        return int(data.split('\r\n\r\n')[0])

    def get_body(self, data):
        if not data:
            return None
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #urllib.parse.urlparse(url)
        host,port,path = self.get_components(url)
        self.connect(host,port)
        headers = (f"GET {path} HTTP/1.1\r\n"
                   f"Host: {host}\r\n"
                   "Accept: */*\r\n"
                   "Connection: close\r\n"
                   "\r\n")
        self.sendall(headers)
        receive_all = self.recvall(self.socket)
        #print(receive_all)
        code = self.get_code(receive_all)
        body = self.get_body(receive_all)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host,port, path = self.get_components(url)
        self.connect(host,port)
        content_type = "application/x-www-form-urlencoded"
        if args:
            body = urllib.parse.urlencode(args)
            content_length = len(body)
        else:
            body =""
            content_length = 0

        headers = (f"POST {path} HTTP/1.1\r\n"
                   f"Host: {host}\r\n"
                   f"Content-Length: {content_length}\r\n"
                   f"Content-Type: {content_type}\r\n"
                   "Accept: */*\r\n"
                   "Connection: close\r\n"
                   "\r\n")
        self.sendall(headers+body)
        receive_all = self.recvall(self.socket)
        code = self.get_code(receive_all)
        body = self.get_body(receive_all)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def get_components(self,url):
        if (url.startswith("https://")):
            components = urllib.parse.urlparse(url)
        elif (url.startswith("http://")):
            components = urllib.parse.urlparse(url)
        else:
            components = urllib.parse.urlparse("https://" + url)

        host = components.hostname
        port = components.port
        path = components.path
        if not path:
            path = "/"
        if not host:
            host = 'localhost'
        if not port:
            port = 80
        return host,port,path


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
