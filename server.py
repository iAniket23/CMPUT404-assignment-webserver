#  coding: utf-8
import socketserver
from os.path import isdir
from os.path import isfile
from datetime import datetime, timezone

# Copyright 2013 Abram Hindle, Eddie Antonio Santos    
# Copyright 2021 Aniket Mishra
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        all_data = self.data.decode('utf-8').split('\r\n')
        header = all_data[0].split()  # ['GET', '/base.css', 'HTTP/1.1']
        data_path = header[1]
        # if cannot handle ==> send 405 Method Not Allowed
        if header[0] != "GET":
            self.get_error_405()
        if len(data_path) == 1 and data_path[0] == "/":
            data_path = data_path + "index.html"
            self.get_content(data_path,"html")
        # if the requested resource if a directory
        elif isdir("www" + data_path):
            self.handle_dir(data_path, header)
            
        elif isfile("www"+data_path) and data_path:
            self.handle_file(data_path)
        else:
            self.get_error_404()


    def handle_dir(self, data_path, header):
        # check if need to send 301 moved permanently or not
            if data_path[-1] != "/":
                data_path += "/"
                self.get_error_301(data_path, header)
            else:
                # it's a regular directory: must return index.html & base.css of that path
                data_path = data_path + "index.html"
                self.get_content(data_path,"html")

    def handle_file(self, data_path):
        if(data_path):
            if data_path[-5:] == ".html":
                type = ".html"
                self.get_content(data_path, "html")

            elif data_path[-4:] == ".css":
                self.get_content(data_path, "css")
            
            else:
                self.get_error_404()
                    
        else:
            self.get_error_404()


    def get_content(self, data_path, type):
        try:
            file = open("www"+ data_path, 'r')
            data = file.read()
            length = len(data)
            message = "HTTP/1.1 200 OK\r\n Connection: close\r\n"
            if type == "html":
                now = datetime.now(timezone.utc)
                date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
                message += "Content-Type: text/html\r\n\r\n"+ data +" Date: {}\r\n Content-Length: {}\r\n".format(date, length)
                self.request.sendall(bytearray(message, 'utf-8'))
            else:
                message += "Content-Type: text/css\r\n\r\n"+ data
                self.request.sendall(bytearray(message, 'utf-8'))
                
        except Exception:
            self.get_error_404()

    def get_error_301(self, data_path, header):
        try:
            self.request.sendall(
                        bytearray(f"HTTP/1.1 301 Moved Permanently \nLocation:http://{header[2]}{data_path}/\r\n\r\n ","utf-8"))
        except Exception:
            self.get_error_404()

    def get_error_405(self):
        self.request.sendall(bytearray(f"HTTP/1.1 405 Method Not Allowed", "utf-8"))

    def get_error_404(self):
        self.request.sendall(bytearray(f"HTTP/1.1 404 NOT FOUND\r\n\r\n ","utf-8"))
   
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
