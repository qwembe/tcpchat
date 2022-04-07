from tcp.client import MyTCPClient, MyClientTCPHandler
from tcp.server import MyTCPServer, MyServerTCPHandler
import sys
import logging

logging.config.fileConfig("logging.conf")
logging.disable(logging.INFO)

def main():
    flag = "server"
    HOST = "localhost"
    PORT = 6060
    if len(sys.argv) == 1:
        print("Usage python <server|client> <Host> <Port:int>")
    elif len(sys.argv) == 2:
        flag = sys.argv[1]
        if flag != "server" and flag != "client":
            print("Wrong parameters")
            sys.exit(1)
    else:
        try:
            if len(sys.argv) != 4:
                raise ValueError
            flag = sys.argv[1]
            if flag != "server" and flag != "client":
                raise ValueError
            HOST = sys.argv[2]
            PORT = int(sys.argv[3])
        except ValueError:
            print("Wrong parameters")
            sys.exit(1)
    print(f"{flag} (HOST,PORT) set to ({HOST},{PORT})")



    if flag == "server":
        with open("syslog", "a") as log:
            with MyTCPServer((HOST, PORT), MyServerTCPHandler, bind_and_activate=True) as server_socket:
                server_socket.myinit()
                server_socket.serve_forever()
    else:
        with MyTCPClient((HOST, PORT), MyClientTCPHandler, bind_and_activate=True) as client_socket:
            client_socket.serve_forever()

    print("Shutdown ... ")

if __name__ == '__main__':
    main()
