# This application is a chatroom as a distributed system.

## We used Rabbitmq for asynchronous communication
- each agent has its queue where he receives encrypted messages binded with his username

## We need to encrypt messages with RSA protocol
- each agent generates its key pairs
- each agent registers its public key and username in the server

## exchanging messages
let's assume that Alice wants to send a message to Bob in an unsecured channel
- Alice configures that its destination is Bob
- Alice receives the public key of Bob
- Alice encrypts the message with the public key of Bob
- Alice sends the message to Bob
- Bob decrypts the message with his private key
