import json
from socket import *

NUMBER_ACCEPTABLE_USERS = 5


class Server:
    def __init__(self):
        print('Configuration ...')
        self.host = input('Host: ')
        self.port = int(input('Port: '))
        print('Listening on', self.host+':'+str(self.port))
        self.users = {}

    def register(self, username, public_key_n, public_key_e):
        if username not in self.users:
            self.users[username] = (public_key_n, public_key_e)
            print(username, 'joined the server')


def create_server():
    server = Server()
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.bind((server.host, server.port))
        server_socket.listen(NUMBER_ACCEPTABLE_USERS)
        while 1:
            (client_socket, address) = server_socket.accept()
            rd = client_socket.recv(5000).decode()
            user = json.loads(rd)
            if len(user) == 3:
                server.register(user['username'], user['public_key_n'], user['public_key_e'])
            else:
                username = user['username']
                if username in server.users:
                    data_to_send = json.dumps(
                        {'public_key_n': server.users[username][0], 'public_key_e': server.users[username][1]})
                    client_socket.sendall(data_to_send.encode())
                # TODO: else send not found
            client_socket.shutdown(SHUT_WR)
    except Exception as ex:
        print(ex)
    server_socket.close()


create_server()
