import socket

from rich.console import Console

from portal_platformer.server import ServerPlayer, ServerPlayers

console = Console()


class Client:
    def __init__(self, host: str = "127.0.0.1", port: int = 5558):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        self.connection = self.socket.connect((self.host, self.port))
        data = self.socket.recv(1024)
        self.player = ServerPlayer.parse_raw(data.decode())
        self.send("hi".encode())
        return self.connection

    def close(self):
        self.socket.close()

    # def send_receive(self, data):
    #     self.send(data)
    #     return self.receive()

    def send(self, data):
        self.socket.sendall(data)
        return self.receive()

    def receive(self):
        data = self.socket.recv(1024 * 1024)
        self.players = ServerPlayers.parse_raw(data.decode())
