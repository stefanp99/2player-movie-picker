import socket
import pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('192.168.0.105', 12345))
sock.listen()

clients = []
addresses = []

liked_shows1 = []
liked_shows2 = []


def handle(client):
    if len(addresses) == 1:
        liked_shows1.append(pickle.loads(client.recv(1024)))
        print(f'{client.getpeername()[0]} sent data!')
        print(liked_shows1[0])
    elif len(addresses) == 2:
        liked_shows2.append(pickle.loads(client.recv(1024)))
        print(f'{client.getpeername()[0]} sent data!')
        print(liked_shows2[0])


def receive():
    while True and len(liked_shows2) == 0:
        client, address = sock.accept()
        clients.append(client)
        addresses.append(address)
        handle(client)


print('Server started!')
receive()
liked_shows1 = liked_shows1[0]
liked_shows2 = liked_shows2[0]
common_shows = set(liked_shows1) & set(liked_shows2)
common_shows = list(common_shows)
print('Common: ')
print(common_shows)
data = pickle.dumps(common_shows)
for client in clients:
    client.send(data)
    print(f'{client.getpeername()[0]} received data!')
sock.close()
