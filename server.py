# https://github.com/tornadoweb/tornado/tree/stable/demos/chat

import socket
import socketserver
import select, selectors
import time

HEADER_LENGTH = 10
BLOCK_LENGHT = 1024

HOST = "127.0.0.1"
PORT = 1234

if hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
else:
    _ServerSelector = selectors.SelectSelector


class MyTCPHandler(socketserver.BaseRequestHandler):

    def read(self):
        data = self.server.users[self.client_address].decode("utf-8")
        try:
            message = self.request.recv(BLOCK_LENGHT).decode("utf-8")
            if not message:
                raise OSError
            data += " > " + message
            # data += self.request.recv(BLOCK_LENGHT).decode("utf-8")
            # self.request.flush()
        except OSError as e:
            self.server.read_selector.unregister(self.request)
            self.server.write_selector.unregister(self.request)
            del self.server.users[self.client_address]
            self.running = False
            data += " has left the chat ..."
            # print(f"In read func Ecxeption! {e}")
        except Exception as e:
            self.running = False
            print(e)
        finally:
            return data
        # print("I'm ready to accept!")

    def write(self, messages):
        # for i, message in enumerate(messages):
        #     if i == 0 and len(messages) > 1:
        #         chat = message
        #     elif i > 0 and len(messages) > 1:
        #         chat = messages + "\n"
        #     elif i == len(messages) - 1:
        #         chat = message
        chat = "\n".join(messages)
        self.request.sendall(chat.encode("utf-8"))

        print("i'm ready to write!")

    def handle(self):
        self.running = True
        data = self.request.recv(HEADER_LENGTH)
        # self.server.sockets.append(self.request)
        self.server.users[self.client_address] = data
        # self.request.flush()
        # self.request.setblocking(False)
        print(self.request)
        self.server.read_selector.register(self.request, selectors.EVENT_READ, data=self.read)
        self.server.write_selector.register(self.request, selectors.EVENT_WRITE, data=self.write)
        # self.server.read_selector.register(self.request, selectors.EVENT_READ | selectors.EVENT_WRITE, data=lambda x:self.read(x))
        # self.server.write_selector.register(self.request, selectors.EVENT_WRITE, data=self.write)

        print("Registered!")
        while self.running:
            time.sleep(1)
            # print("Thread alive!")
        # print("Exit thread")
        # self.server.write_selector.register(self.request, selectors.EVENT_WRITE)

        # self.request.sendall(data.upper())


class MyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    sockets = []
    users = {}
    read_selector = _ServerSelector()
    write_selector = _ServerSelector()

    def process_request(self, request, client_address):
        return super(MyTCPServer, self).process_request(request, client_address)


    def service_actions(self) -> None:
        try:
            # print("Lets try ...")
            # print(self.sockets)
            queue = []
            x = self.read_selector.select(timeout=0.5)
            print("alive!")
            if x:
                # print(x)
                for key, event in x:
                    # sock = key.fileobj
                    # print(key)
                    # raddr = key.raddr
                    gain_message = key.data
                    queue.append(gain_message())
            if queue:
                x = self.write_selector.select()
                for key, event in x:
                    write_message = key.data
                    write_message(queue)
            #         print(event == selectors.EVENT_WRITE)
            # y = self.write_selector.select(timeout=0.5)
            # print("It works!")
            print(queue)
            # print("Hi")
            # print(x,y)
            pass
        except OSError as e:
            print(e)
            pass
        except ValueError as e:
            print(e)
            # self.sockets = [s for s in self.sockets if s.fileno() >= 0]

            # self.shutdown()
            # sys.exit(0)
        except Exception as e:
            print(e)

        return super(MyTCPServer, self).service_actions()

    pass


with MyTCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=True) as server_socket:
    server_socket.serve_forever()

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.bind((IP, PORT))
# server_socket.listen()
# sockets_list = [server_socket]
# clients = {}
#
# print(f'Listening for connections on {IP}:{PORT}...')
#
# # Handles message receiving
# def receive_message(client_socket):
#     try:
#         message_header = client_socket.recv(HEADER_LENGTH)
#         if not len(message_header):
#             return False
#         message_length = int(message_header.decode('utf-8').strip())
#         return {'header': message_header, 'data': client_socket.recv(message_length)}
#
#     except:
#         # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
#         # or just lost his connection
#         # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
#         # and that's also a cause when we receive an empty message
#         return False
#
# while True:
#
#     # Calls Unix select() system call or Windows select() WinSock call with three parameters:
#     #   - rlist - sockets to be monitored for incoming data
#     #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
#     #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
#     # Returns lists:
#     #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
#     #   - writing - sockets ready for data to be send thru them
#     #   - errors  - sockets with some exceptions
#     # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
#     read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
#
#
#     # Iterate over notified sockets
#     for notified_socket in read_sockets:
#
#         # If notified socket is a server socket - new connection, accept it
#         if notified_socket == server_socket:
#
#             # Accept new connection
#             # That gives us new socket - client socket, connected to this given client only, it's unique for that client
#             # The other returned object is ip/port set
#             client_socket, client_address = server_socket.accept()
#
#             # Client should send his name right away, receive it
#             user = receive_message(client_socket)
#
#             # If False - client disconnected before he sent his name
#             if user is False:
#                 continue
#
#             # Add accepted socket to select.select() list
#             sockets_list.append(client_socket)
#
#             # Also save username and username header
#             clients[client_socket] = user
#
#             print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
#
#         # Else existing socket is sending a message
#         else:
#
#             # Receive message
#             message = receive_message(notified_socket)
#
#             # If False, client disconnected, cleanup
#             if message is False:
#                 print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
#
#                 # Remove from list for socket.socket()
#                 sockets_list.remove(notified_socket)
#
#                 # Remove from our list of users
#                 del clients[notified_socket]
#
#                 continue
#
#             # Get user by notified socket, so we will know who sent the message
#             user = clients[notified_socket]
#
#             print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
#
#             # Iterate over connected clients and broadcast message
#             for client_socket in clients:
#
#                 # But don't sent it to sender
#                 if client_socket != notified_socket:
#
#                     # Send user and message (both with their headers)
#                     # We are reusing here message header sent by sender, and saved username header send by user when he connected
#                     client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
#
#     # It's not really necessary to have this, but will handle some socket exceptions just in case
#     for notified_socket in exception_sockets:
#
#         # Remove from list for socket.socket()
#         sockets_list.remove(notified_socket)
#
#         # Remove from our list of users
#         del clients[notified_socket]
