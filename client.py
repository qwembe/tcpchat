import socket
import selectors
import errno
import sys
import socketserver
import time
import json
import threading
import os
import logging
import logging.config

# if hasattr(selectors, 'PollSelector'):
#     _ServerSelector = selectors.PollSelector
# else:
#     _ServerSelector = selectors.SelectSelector

# HEADER_LENGTH = 10
BLOCK_LENGTH = 1024

IP = "127.0.0.1"
PORT = 1234

logging.config.fileConfig("logging.conf")
logging.disable(logging.INFO)


class MyClientTCPHandler(socketserver.BaseRequestHandler):
    logger = logging.getLogger("TCPHandler")

    def handle(self):
        self.logger.info("New message ...")
        try:
            raw = self.request.recv(BLOCK_LENGTH)
        except OSError:
            print("Server Dead. =(")
            self.server.server_close()
            self.server.shutdown()
            sys.exit()

        self.logger.debug(raw)
        TYPE, BODY = self.server.unpack_message(raw)
        match TYPE:
            case "STATE":
                self.server.STATE = BODY
                print(f"< Server is {self.server.STATE} >")
            case "INCMESS":
                log, message = BODY
                print(f"{log}  : {message}")
                raw = self.server.puck_message(TYPE="MESSACC", BODY=log)
                self.server.send(raw)
            case "MESSTAT":
                if BODY:
                    print("< Message have been delivered! >  =)")
                else:
                    print("< Message sending failure >       =(")
            case "BROADCAST":
                from_who, message = BODY
                print(f"broadcast - {from_who} : {message}")
            case "WHOAVAIL":
                print("Users:")
                print("; ".join(BODY))
                pass
            case "BYE":
                print("< Server Dead. =( >")
                self.server.server_close()
                self.server.shutdown()
                sys.exit()
            case _:
                self.logger.warning("unsupported message type")


class MyTCPServer(socketserver.TCPServer):
    STATE = ""

    logger = logging.getLogger("SocketClient")

    def unpack_message(self, raw):
        message = json.loads(raw.decode("utf-8"))
        return message["TYPE"], message["BODY"]

    def puck_message(self, TYPE="STATE", BODY="BODY"):
        msg = {}
        msg['TYPE'] = TYPE
        msg['BODY'] = BODY
        return bytes(json.dumps(msg).encode("utf8"))

    def send(self, raw):
        if len(raw) != self.socket.send(raw):
            self.logger.warning("Message was not delivered or wasn't fully delivered")
            raise Exception("Message was not delivered or wasn't fully delivered")
        self.logger.debug(f"msg sent - {raw}")

    # in-loop action

    def worker_input(self):
        print("< press <enter> to see menu: >")
        input()
        self.key_pressed = True

    def ask_state(self):
        raw = self.puck_message(TYPE="STATE")
        self.send(raw)
        self.logger.info("ask_state")
        # match self.STATE:
        #     case "WAIT4CLIENTS":
        #         print("Server is waiting for new users ...")
        #     case "READY2SERV":
        #         print("Server is active ...")
        #     case _:
        #         print("Unknown state")

    def ask_users(self):
        self.logger.info("ask_users")
        raw = self.puck_message(TYPE="WHOAVAIL")
        self.send(raw)

    def send_to(self):
        self.logger.info("send_to")
        log = input("Enter login: ")
        msg = input("Enter message: ")
        raw = self.puck_message(TYPE="SENDTO", BODY=[log, msg])
        self.send(raw)
        pass

    def send2all(self):
        self.logger.info("send2all")
        msg = input("Enter message: ")
        raw = self.puck_message(TYPE="EVERY1", BODY=msg)
        self.send(raw)
        pass

    def close_connection(self):
        self.logger.info("close_connection")
        raw = self.puck_message(TYPE="BYE")
        self.send(raw)
        pass

    def print_menu(self):
        print("< Hi! I'm a menu. Enter a command >")
        print("1. Is server available?")
        print("2. Who available?")
        print("3. Send to available client")
        print("4. Send message to all")
        print("5. Close connection")

        try:
            return int(input())
        except ValueError:
            return 0

    def service_actions(self):
        # print(self.key_pressed)
        if self.key_pressed:
            key = self.print_menu()
            match key:
                case 1:
                    self.ask_state()
                case 2:
                    self.ask_users()
                case 3:
                    self.send_to()
                case 4:
                    self.send2all()
                case 5:
                    self.close_connection()
                case _:
                    print("< Waiting for messages ... >")
            self.key_pressed = False
            self.wait_for_continue = threading.Thread(target=self.worker_input)
            self.wait_for_continue.start()

    # Init connection #

    def server_activate(self):
        try:
            self.socket.connect(self.server_address)
            self.socket.setblocking(False)
        except OSError:
            self.logger.critical("Wrong address or target server is not available")
            sys.exit()

        login = input("Enter login: ")
        raw = self.puck_message(TYPE="HI", BODY=login)
        self.send(raw)
        self.key_pressed = True

    # Supporting methods to make client

    def shutdown_request(self, request):
        pass

    def get_request(self):
        return self.socket, self.server_address

    def server_bind(self):
        pass

    def server_close(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except OSError:
            self.logger.critical("Server was never opened")
        self.wait_for_continue.join()
        self.logger.info("Server closed. Bye")
        sys.exit()
        return super(MyTCPServer, self).server_close()


def main():
    with MyTCPServer((IP, PORT), MyClientTCPHandler, bind_and_activate=True) as client_socket:
        client_socket.serve_forever()
        print("Sever closed")


if __name__ == "__main__":
    main()
