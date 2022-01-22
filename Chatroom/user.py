import hashlib
import json
import sys
import threading
import pika
import rsa
from socket import *
from rsa import PublicKey

IP_ADDRESS = 'localhost'
PORT_NUMBER = 8000


class User:
    def __init__(self, username):
        # username is the messaging queue of this user
        self.username = username

        # generating keys
        self.pub_key, self.prv_key = rsa.newkeys(3072)

        # register to the server
        self.__register()

        # connection to the broker
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(IP_ADDRESS))
        channel = self.connection.channel()

        # create the queue if not exist
        channel.queue_declare(queue=username)

        # receive message if there is something in the queue
        self.thread = threading.Thread(target=self.__receive)
        self.thread.start()

    def send(self, receiver):
        # sending message to an empty exchange so we specify exactly to which queue to deliver the message
        channel = self.connection.channel()

        receiver_pub_key = self.__get_receiver_pub_key(receiver)

        while True:
            message = input('> ')
            if message == '':
                return True

            data = json.dumps({'username': self.username, 'message': message})

            encrypted_data = self.__encrypt(data, receiver_pub_key)

            channel.basic_publish(exchange='',
                                  routing_key=receiver,
                                  body=encrypted_data)

        # make sure the network buffers were flushed and our message was actually delivered to RabbitMQ
        # self.connection.close()

    def __receive(self):
        def callback(ch, method, properties, body):
            # callback function to be called when a message is received in the queue by the pika library
            data = json.loads(self.__decrypt(body))
            print(data['username'], ': ', data['message'], '\n> ', end='')

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(IP_ADDRESS))
        channel = self.connection.channel()

        # create the queue if not exist
        channel.queue_declare(queue=self.username)

        # bind the callback to the queue
        channel.basic_consume(queue=self.username,
                              auto_ack=True,
                              on_message_callback=callback)

        # receive a message:
        # an endless loop that runs the callback function when the message is red from the queue
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print('Interrupted')
            sys.exit(0)

    def __encrypt(self, message, pub_key):
        encoded_message = bytes(message, encoding="ascii")
        return rsa.encrypt(encoded_message, pub_key)

    def __decrypt(self, encrypted_message):
        return rsa.decrypt(encrypted_message, self.prv_key)

    def __sign(self, message):
        encoded_message = bytes(message, encoding="ascii")
        return rsa.sign(encoded_message, self.prv_key, 'sha512')

    def __verify(self, encrypted_message, signed_message, pub_key):
        return rsa.verify(encrypted_message, signed_message, pub_key)

    def __register(self):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, PORT_NUMBER))
        data = json.dumps({'username': self.username, 'public_key_n': self.pub_key.n, 'public_key_e': self.pub_key.e})
        client_socket.send(data.encode())
        client_socket.close()

    def __get_receiver_pub_key(self, username):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, PORT_NUMBER))
        # send username
        user = json.dumps({'username': username})
        client_socket.send(user.encode())
        # get public key
        rd = client_socket.recv(5000).decode()
        receiver_key_json = json.loads(rd)
        client_socket.close()
        return PublicKey(receiver_key_json['public_key_n'], receiver_key_json['public_key_e'])
