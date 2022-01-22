from user import User

username = input('Username: ')
user = User(username)

change_destination = True
while change_destination:
    destination = input('Destination: ')
    change_destination = user.send(destination)
