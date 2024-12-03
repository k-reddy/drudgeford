import socket
import threading
from dataclasses import dataclass
import queue
import json
from typing import List, Dict
from enum import Enum


def send_message(sock: socket.socket, data: dict):
    """Send a message with length prefix"""
    message = json.dumps(data).encode("utf-8")
    message_length = len(message)
    # Send length as 4-byte integer
    sock.send(message_length.to_bytes(4, byteorder="big"))
    # Send actual message
    sock.send(message)


def receive_message(sock: socket.socket) -> dict:
    """Receive a complete message using length prefix"""
    # Get message length (4 bytes)
    length_bytes = recv_all(sock, 4)
    if not length_bytes:
        raise ConnectionError("Connection closed")
    message_length = int.from_bytes(length_bytes, byteorder="big")

    # Get actual message
    message = recv_all(sock, message_length)
    if not message:
        raise ConnectionError("Connection closed")
    return json.loads(message.decode("utf-8"))


def recv_all(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


class ClientType(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"


@dataclass
class ClientData:
    socket: socket.socket
    client_id: str  # "backend" or "frontend_1", "frontend_2", etc.
    client_type: ClientType
    tasks: List[Dict]
    thread: threading.Thread


class TCPServer:
    def __init__(self, host="0.0.0.0", port=8080, testing_mode=True):
        self.host = host
        self.port = port
        self.testing_mode = testing_mode
        self.clients: Dict[str, ClientData] = {}  # client_id -> ClientData
        self.frontend_counter = 0
        self.user_input_queue = queue.Queue()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.persistent_frontend_tasks: List[Dict] = []

        if self.testing_mode:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.lock = threading.Lock()
        self.running = False
        self.accept_thread = None

    def _generate_client_id(self, client_type: ClientType) -> str:
        """Generate a unique client ID based on type"""
        if client_type == ClientType.BACKEND:
            return "backend"
        self.frontend_counter += 1
        return f"frontend_{self.frontend_counter}"

    def start(self):
        """Start the server and listen for connections"""
        self.running = True
        self.accept_thread = threading.Thread(
            target=self._accept_connections, daemon=True
        )
        self.accept_thread.start()

    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            client_socket, _ = self.server_socket.accept()
            client_socket.settimeout(0.5)

            # Wait for client to identify itself
            client_info = receive_message(client_socket)
            client_type = ClientType(client_info.get("client_type"))

            # Generate client ID and send it back
            client_id = self._generate_client_id(client_type)
            send_message(client_socket, {"client_id": client_id})

            # Create and start client thread
            client_thread = threading.Thread(
                target=self._handle_client, daemon=True, args=(client_socket, client_id)
            )

            with self.lock:
                self.clients[client_id] = ClientData(
                    socket=client_socket,
                    client_id=client_id,
                    client_type=client_type,
                    tasks=[],
                    thread=client_thread,
                )

            client_thread.start()

    def _handle_client(self, client_socket: socket.socket, client_id: str):
        """Handle individual client connections"""
        client_data = self.clients[client_id]
        # before anything else, load all the persistent tasks you missed
        if client_data.client_type == ClientType.FRONTEND:
            with self.lock:
                for task in self.persistent_frontend_tasks:
                    client_data.tasks.append(task)
        while self.running:
            try:
                request = receive_message(client_socket)
                command = request.get("command")
                payload = request.get("payload", {})
                response = self._process_command(command, payload, client_id)
                send_message(client_socket, response)
            except socket.timeout:
                continue

    def _process_command(self, command: str, payload: Dict, client_id: str) -> Dict:
        """Process commands and return appropriate response"""
        client_data = self.clients[client_id]

        if command == "get_task":
            with self.lock:
                task = None
                if client_data.tasks:
                    task = client_data.tasks.pop(0)
            return {"task": task}

        elif command == "post_task":
            return self._process_post_task(payload)

        elif command == "get_user_input":
            if client_data.client_type != ClientType.BACKEND:
                raise PermissionError(
                    "Only backend client is allowed to get user input"
                )
            # Get user input with source client information
            user_input_data = self.user_input_queue.get()
            return {"user_input": user_input_data}

        elif command == "post_user_input":
            if client_data.client_type != ClientType.FRONTEND:
                return {"error": "Only frontend can post user input"}

            # Include client ID with user input
            user_input_data = {"source_client_id": client_id, "input": payload}
            self.user_input_queue.put(user_input_data)
            return {"status": "success"}

        else:
            raise ValueError("unknown command")

    def _process_post_task(self, payload):
        target_client_id = payload.get("target_client_id")
        task_data = payload.get("task")
        if not target_client_id:
            raise ValueError("No target client id")

        if target_client_id == "ALL_FRONTEND":
            # we add all ALL_FRONTEND tasks to the persistent list
            # so that late-coming clients can still get the important info
            with self.lock:
                self.persistent_frontend_tasks.append(task_data)

                for client_data in self.clients.values():
                    if client_data.client_type == ClientType.FRONTEND:
                        client_data.tasks.append(task_data)
        elif target_client_id in self.clients:
            with self.lock:
                self.clients[target_client_id].tasks.append(task_data)
        else:
            raise ValueError("unknown client id")
        return {"status": "success"}

    def stop(self):
        """Stop the server and clean up all resources gracefully"""
        print("Initiating server shutdown...")

        self.running = False

        if self.accept_thread and self.accept_thread.is_alive():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
            self.accept_thread.join(timeout=2)

        # Wait for client threads to finish
        with self.lock:
            active_threads = [
                client.thread
                for client in self.clients.values()
                if client.thread.is_alive()
            ]

        for thread in active_threads:
            thread.join(timeout=2)

        # Clear queue
        while not self.user_input_queue.empty():
            try:
                self.user_input_queue.get_nowait()
            except queue.Empty:
                break

        # Close all client connections
        with self.lock:
            for client_data in self.clients.values():
                client_data.socket.close()
            self.clients.clear()

        # Close server socket
        self.server_socket.close()

        print("Server shutdown complete")
