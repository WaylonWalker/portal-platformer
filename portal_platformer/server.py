import socket
import threading
import time
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


class ServerPlayer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    addr: tuple[str, int]
    name: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    map: Optional[str] = None


class ServerPlayers(BaseModel):
    players: dict[UUID, ServerPlayer]


class Server:
    def __init__(self, port: int = 5558):
        self.port = port
        self.players = ServerPlayers(players={})
        self.lock = (
            threading.Lock()
        )  # To ensure thread-safe operations on the players list

    def handle_player(self, conn, addr):
        player = ServerPlayer(addr=addr)
        with self.lock:
            self.players.players[player.id] = player
            console.log(f"New player connected: {player}")
            console.log(f"Connected by {addr}")
            console.log(f"Current players: {self.players}")
            conn.sendall(str(player.json()).encode())

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    _player = ServerPlayer.parse_raw(data.decode())
                    _player.id = player.id
                    player = _player
                    with self.lock:
                        self.players.players[_player.id] = _player
                        console.log(f"Received from {addr}: {data}")
                        console.log(f"Current players: {self.players}")

                except Exception as e:
                    console.log(e)

                print(f"Received from {addr}: {data}")
                conn.sendall(str(self.players.json()).encode())
        finally:
            with self.lock:
                del self.players.players[player.id]
                console.log(f"Disconnected from {addr}")
                console.log(f"Current players: {self.players}")
            conn.close()

    def run(self):
        print(f"Listening on port {self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", self.port))
            s.listen()
            last_print_time = 0
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=self.handle_player, args=(conn, addr))
                thread.start()

                if time.time() - last_print_time > 5:
                    console.log(f"Current players: {self.players}")
                    last_print_time = time.time()
                else:
                    console.log(f"Connected by {addr}")


# Example usage:
if __name__ == "__main__":
    server = Server()
    server.run()
