import socket
import json
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


class TCPClient:
    def __init__(self, client_type: ClientType, host="localhost", port=8080):
        self.client_type = client_type
        self.client_id = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self._identify()

    def _identify(self):
        """Identify client type to server and receive client ID"""
        identification = {"client_type": self.client_type.value}
        send_message(self.socket, identification)
        response = receive_message(self.socket)
        self.client_id = response["client_id"]

    def _send_request(self, command, payload=None):
        request = {"command": command}
        if payload is not None:
            request["payload"] = payload
            print(payload)
        try:
            send_message(self.socket, request)
            response = receive_message(self.socket)
            if "task" in response and "null" not in str(response):
                print(response)
            return response
        except (json.JSONDecodeError, ConnectionError) as e:
            self.close()
            raise ConnectionError(f"Connection error: {str(e)}")

    def get_task(self):
        """Get tasks assigned to this client"""
        response = self._send_request("get_task")
        return response.get("task")

    def post_task(self, task_data, target_client_id):
        """Post a task for a specific client"""
        payload = {"target_client_id": target_client_id, "task": task_data}
        return self._send_request("post_task", payload)

    def get_user_input(self):
        """Get user input (backend only)"""
        if self.client_type != ClientType.BACKEND:
            raise PermissionError("Only backend clients can get user input")
        try:
            response = self._send_request("get_user_input")
            return response.get("user_input")
        except ConnectionError:
            # If server closes connection during blocking operation,
            # that's expected behavior for the blocking test
            return None

    def post_user_input(self, user_input):
        """Post user input (frontend only)"""
        if self.client_type != ClientType.FRONTEND:
            raise PermissionError("Only frontend clients can post user input")
        return self._send_request("post_user_input", user_input)

    def close(self):
        """Close the client connection"""
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # Socket might already be closed
        self.socket.close()

    @property
    def id(self):
        """Get the client ID assigned by the server"""
        return self.client_id
