import socket
import selectors
import errno
import sys
import socketserver
import time
import atexit
import threading
import os
import unicurses


def clear(): os.system('cls')


screen = ""
prompt = ""

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
CURSOR_DOWN = '\x1b[B'
SCROL_UP = '\x1b[S'
SCROL_DOWN = '\x1b[T'

if hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
else:
    _ServerSelector = selectors.SelectSelector

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
read_selector = _ServerSelector()


# my_username = input("Username: ")

def printToScreen(s):
    global screen, prompt
    clear()
    screen += (s + '\n')
    print(screen)
    print(prompt)


def promptToScreen(p):
    global screen, prompt
    clear()
    print(screen)
    s = input(p)
    prompt = p + s
    return s


# try:
def waiting_for_input_from_server():
    while True:
        x = read_selector.select()

        if x:
            selobj, event = x[0]
            # print(selobj)
            con = selobj.fileobj
            msg = con.recv(1024).decode('utf8')

            # print(u"\u001b[s", end="")  # Save current cursor position
            # print(u"\u001b[F", end="")  # Moves cursor to beginning of the line n (default 1) lines up.
            # # print(u"\u001b[999D", end="")  # Move cursor to beginning of line
            # print(u"\u001b[T", end="")  # Scroll up/pan window down 1 line
            # print(u"\u001b[L", end="")  # Insert new line
            #
            # # printToScreen(msg)  # Print output status msg
            # # print(CURSOR_UP_ONE + ERASE_LINE + msg, end="")
            # # print(SCROL_DOWN + msg, end="")
            # print(msg)
            # # printToScreen(msg)
            #
            # print(u"\u001b[u", end="")  # Jump back to saved cursor position

            # print(chr(27) + f'[2A{msg}')

            # print(chr(27) + f'[2A{msg}')
            # print()

            print("\u001B[s", end="")  # Save current cursor position
            print("\u001B[999D", end="")  # Move cursor to beginning of line
            print("\u001b[E",end="")         # New line above input
            print()
            # print("\u001B[A", end="")  # Move cursor up one line
            # print("\u001B[A", end="")  # Move cursor up one line
            print("\u001B[S", end="")  # Scroll up/pan window down 1 line
            print("\u001B[L", end="")  # Insert new line
            print(msg, end="")  # Print output status msg
            print("\u001B[u", end="")  # Jump back to saved cursor position

        # print(x)
        # print(con.recv(1024).decode('utf8'))


def wait_input_from_main():
    i = 1
    msg = " "
    while msg:
        i += 1

        # msg = promptToScreen(user + " (you) >")
        msg = input(user + " (you) >")
        # print(msg)
        client_socket.sendall(bytes(msg.encode("utf-8")))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((IP, PORT))
    os.system('cls')
    print("\u001b[31mHelloWorld\u001b[0m")
    user = input("Enter login ")
    # print(msg)
    client_socket.sendall(bytes(user.encode("utf-8")))

    read_selector.register(client_socket, selectors.EVENT_READ)

    mythread = threading.Thread(target=waiting_for_input_from_server)
    mainthread = threading.Thread(target=wait_input_from_main)
    mythread.start()
    mainthread.start()
    mainthread.join()
    print("End")

    # client_socket.sendall(bytes(f"poll {i}".encode("utf-8")))
    # client_socket.flush()
    # print(client_socket)
    # time.sleep(2)
# except Exception as e:
#     print(e)
# finally:
#     client_socket.shutdown()
#     client_socket.close()
#     sys.exit()
# # Create a socket
# # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# # Connect to a given ip and port
# client_socket.connect((IP, PORT))
#
# # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
# client_socket.setblocking(False)
#
# # Prepare username and header and send them
# # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
# username = my_username.encode('utf-8')
# username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
# client_socket.send(username_header + username)
#
# while True:
#
#     # Wait for user to input a message
#     message = input(f'{my_username} > ')
#
#     # If message is not empty - send it
#     if message:
#
#         # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
#         message = message.encode('utf-8')
#         message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
#         client_socket.send(message_header + message)
#
#     try:
#         # Now we want to loop over received messages (there might be more than one) and print them
#         while True:
#
#             # Receive our "header" containing username length, it's size is defined and constant
#             username_header = client_socket.recv(HEADER_LENGTH)
#
#             # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
#             if not len(username_header):
#                 print('Connection closed by the server')
#                 sys.exit()
#
#             # Convert header to int value
#             username_length = int(username_header.decode('utf-8').strip())
#
#             # Receive and decode username
#             username = client_socket.recv(username_length).decode('utf-8')
#
#             # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
#             message_header = client_socket.recv(HEADER_LENGTH)
#             message_length = int(message_header.decode('utf-8').strip())
#             message = client_socket.recv(message_length).decode('utf-8')
#
#             # Print message
#             print(f'{username} > {message}')
#
#     except IOError as e:
#         # This is normal on non blocking connections - when there are no incoming data error is going to be raised
#         # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
#         # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
#         # If we got different error code - something happened
#         if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
#             print('Reading error: {}'.format(str(e)))
#             sys.exit()
#
#         # We just did not receive anything
#         continue
#
#     except Exception as e:
#         # Any other exception - something happened, exit
#         print('Reading error: '.format(str(e)))
#         sys.exit()
