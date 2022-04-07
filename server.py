# https://github.com/tornadoweb/tornado/tree/stable/demos/chat

import socket
import socketserver
import select, selectors
import time
import logging
import logging.config
import json
import sys

# HEADER_LENGTH = 10
BLOCK_LENGTH = 1024

HOST = "127.0.0.1"
PORT = 1234

logging.config.fileConfig("logging.conf")
# logging.disable(logging.INFO)
logging.FileHandler("syslog")

if hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
else:
    _ServerSelector = selectors.SelectSelector


class MyTCPHandler(socketserver.BaseRequestHandler):

    def send(self, raw, recipient=None):
        if recipient is None:
            self.logger.debug("Sending back response")
            self.logger.debug(raw)
            if len(raw) != self.request.send(raw):
                self.logger.warning(f"Message TO {self.user} was not delivered or wasn't fully delivered")
                raise Exception("Message was not delivered or wasn't fully delivered")
        self.logger.debug("Sending successfully!")

    def read(self):
        try:
            raw = self.request.recv(BLOCK_LENGTH)
            if not raw:
                raise OSError
            data = raw
            self.logger.debug("Incoming message (handler.read) ... ")
        except OSError as e:
            self.finish()
            data = b""
        except Exception as e:
            self.logger.warning(f"Unknown exception {e}")
            self.running = False
            data = b""
        finally:
            return data

    def handle(self):
        self.server.logger.info("First connection ... ")
        raw = self.request.recv(BLOCK_LENGTH)
        TYPE, DATA = self.server.unpack_message(raw)
        if TYPE == "HI":
            self.running = True
            self.logger = logging.getLogger(f"syslog")
            self.logger.info(f"Accepted new user {DATA}")
            self.user = DATA
            self.server.users[self.user] = self.send
            self.server.read_selector.register(self.request, selectors.EVENT_READ, data=self)
            self.server.write_selector.register(self.request, selectors.EVENT_WRITE, data=self.send)
            self.logger.debug(f"socket has been registered")
            raw = self.server.puck_message(TYPE="STATE", BODY=self.server.STATE)
            self.send(raw)
            self.logger.debug(f"socket alive")
            print(f"{self.user} has joined --- len users {len(self.server.users)}")
            while self.running:
                time.sleep(1)
            # self.logger.info(f"User {self.user} has left ... ")

        else:
            self.server.logger.warning("Connection denied")

    def finish(self):
        if self.running:
            self.server.read_selector.unregister(self.request)
            self.server.write_selector.unregister(self.request)
            del self.server.users[self.user]
            print(f"{self.user} has left ... len users {len(self.server.users)}")
            self.logger.info(f"User {self.user} has left ...")
            self.running = False

    def send_state(self):
        self.logger.debug("send_state")
        self.logger.info(f"{self.user} asks server status - {self.server.STATE}")
        raw = self.server.puck_message(TYPE="STATE", BODY=self.server.STATE)
        self.send(raw)

    def send_back_poll(self):
        self.logger.debug("send_back_poll")
        users = self.server.get_users_list()
        self.logger.debug(f"self.server.users.keys() {users}")
        self.logger.info(f"{self.user} asks server about active connections - {users}")
        raw = self.server.puck_message(TYPE="WHOAVAIL", BODY=users)
        self.send(raw)

    def send_from_to(self, message_pack):
        self.logger.debug("send_from_to")
        usr, msg = message_pack
        self.logger.info(f"{self.user} > {msg}")
        try:
            send_func = self.server.users.get(f"{usr}")
            raw = self.server.puck_message(TYPE="INCMESS", BODY=[self.user, msg])
            send_func(raw)
        except Exception as e:
            self.logger.error(e)
            self.logger.info(f"{self.user} <sending failure>")
            raw = self.server.puck_message(TYPE="MESSTAT",
                                           BODY=False)
            self.send(raw)

    def message_acc(self, meta):
        self.logger.debug("message_acc")
        self.logger.info(f"{self.user} : <accepted>")
        try:
            send_func = self.server.users[f"{meta}"]
            raw = self.server.puck_message(TYPE="MESSTAT", BODY=True)
            send_func(raw)
        except:
            self.logger.error(f"Error occurred while sending to {meta}")
            pass

    def send_broadcast(self, message):
        self.logger.debug("send_broadcast")
        raw = self.server.puck_message(TYPE="BROADCAST", BODY=[self.user, message])
        self.logger.info(f"{self.user} <broadcast> {message}")
        try:
            x = self.server.write_selector.select()
            for cmd, event in x:
                func = cmd.data
                func(raw)
            raw = self.server.puck_message(TYPE="MESSTAT", BODY=True)
            self.send(raw)
        except Exception as e:
            self.logger.error(e)
            self.logger.info(f"{self.user} <broadcast> {message} <failure>")
            raw = self.server.puck_message(TYPE="MESSTAT", BODY=False)
            self.send(raw)

    def close_connection(self):
        self.logger.debug("close_connection")
        self.logger.info(f"{self.user} leaves server")
        raw = self.server.puck_message(TYPE="BYE", BODY=False)
        self.send(raw)
        self.finish()

    def do_action(self, user_raw):
        self.logger.debug("Performing action ...")
        TYPE, BODY = user_raw
        self.logger.debug(f"query type: {TYPE} - {BODY}")
        match TYPE:
            case "STATE":
                self.send_state()
            case "WHOAVAIL":
                self.send_back_poll()
            case "SENDTO":
                self.send_from_to(BODY)
            case "MESSACC":
                self.message_acc(BODY)
            case "EVERY1":
                self.send_broadcast(BODY)
            case "BYE":
                self.close_connection()


class MyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    logger = logging.getLogger("MyTCPHandler")
    sockets = []
    users = {}
    read_selector = _ServerSelector()
    write_selector = _ServerSelector()

    def myinit(self):
        self._STATE = "WAIT4CLIENTS"

    @property
    def STATE(self):
        return self._STATE

    @STATE.setter
    def STATE(self, value):
        try:
            self.logger.info(f"changing state to {value}")
            x = self.write_selector.select()
            raw = self.puck_message(TYPE="STATE", BODY=value)

            for command, event in x:
                cmd = command.data
                cmd(raw)
            self._STATE = value
            self.logger.info(f"server at {self._STATE} state")
        except OSError as e:
            self.logger.warning(f"Error occurred: {e}")
            sys.exit(1)

    @STATE.getter
    def STATE(self):
        return self._STATE

    def get_users_list(self):
        return [*self.users.keys()]

    def puck_message(self, TYPE="STATE", BODY="BODY"):
        msg = {}
        msg['TYPE'] = TYPE
        msg['BODY'] = BODY
        return bytes(json.dumps(msg).encode("utf8"))

    def unpack_message(self, raw):
        message = json.loads(raw.decode("utf-8"))
        return message["TYPE"], message["BODY"]

    def send_to_user(self, request):
        pass

    def service_actions(self):
        # self.logger.debug("i'm alive")
        if len(self.users) < 2 and self.STATE == "READY2SERV":
            self.STATE = "WAIT4CLIENTS"  # magick property
        if len(self.users) >= 2 and self.STATE == "WAIT4CLIENTS":
            self.STATE = "READY2SERV"    # magick property

        try:
            x = self.read_selector.select(timeout=0.5)
            if x:
                for key, event in x:
                    query = key.data
                    user_raw = query.read()
                    user_query = self.unpack_message(user_raw)
                    query.do_action(user_query)
        except OSError as e:
            # self.logger.error(f"OSError : {e}")
            pass
        except ValueError as e:
            self.logger.error(f"ValueError : {e}")
            # sys.exit(0)
        except Exception as e:
            self.logger.error(f"Exception : {e}")
            sys.exit()

        return super(MyTCPServer, self).service_actions()

    pass


try:
    with MyTCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=True) as server_socket:
        server_socket.myinit()
        server_socket.serve_forever()
except Exception:
    print("CRITICAL - server dead")
