import queue
import socket
from threading import Thread
from abc import ABC
from Constants import PACKET_SIZE


class RATConnection(ABC):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.packet_callback = lambda data: ()
        self.packet_queue = queue.Queue()
        Thread(target=self._packet_loop, daemon=True).start()

    def send_packet(self, buffer):
        self.packet_queue.put(buffer)

    def _packet_loop(self):
        while True:
            buffer = self.packet_queue.get()
            try:
                self.get_sock().send(buffer)
            except:
                pass

    def _listen_for_packets(self):
        buffer = bytearray()

        while True:
            try:
                data = self.get_sock().recv(PACKET_SIZE)
            except:
                # Client disconnected, break out of loop
                break

            if data:
                buffer.extend(data)

                while len(buffer) >= PACKET_SIZE:
                    chunk = bytes(buffer[:PACKET_SIZE])
                    buffer = buffer[PACKET_SIZE:]
                    self.packet_callback(chunk)

    def get_sock(self):
        return self.socket


class RATClient(RATConnection):

    def __init__(self):
        super().__init__()
        self.connected_callback = lambda: ()

    def connect(self, host, port):
        self.socket.connect((host, port))
        self.connected_callback()
        self._listen_for_packets()


class RATServer(RATConnection):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.client_address = None
        self.client_disconnected_callback = lambda: ()

    def listen(self, port):
        self.socket.bind(('0.0.0.0', port))

        while True:
            # Start listening for incoming connections
            self.socket.listen(1)

            # Wait for a client to connect
            self.client_socket, self.client_address = self.socket.accept()
            print(f"Client connected from {self.client_address}")

            # Call the listen_for_packets function to handle incoming packets
            self._listen_for_packets()
            self.client_disconnected_callback()

    def get_sock(self):
        return self.client_socket
