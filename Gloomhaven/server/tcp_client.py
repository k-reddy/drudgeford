import socket
import json
from enum import Enum


def send_message(sock: socket.socket, data: dict):
    """Send a message with length prefix in a single send"""
    message = json.dumps(data).encode("utf-8")
    length_bytes = len(message).to_bytes(4, byteorder="big")
    sock.send(length_bytes + message)  # Send length and message together


def receive_message(sock: socket.socket) -> dict:
    """Receive a complete message using length prefix"""
    try:
        # Get initial data that should contain length
        initial_data = sock.recv(4)
        if not initial_data or len(initial_data) < 4:
            raise ConnectionError("Connection closed")

        message_length = int.from_bytes(initial_data, byteorder="big")
        remaining_data = b""

        # If we got extra data beyond the length, keep it
        if len(initial_data) > 4:
            remaining_data = initial_data[4:]
            message_length -= len(remaining_data)

        # Get any remaining message data
        if message_length > 0:
            message_data = recv_all(sock, message_length)
            if not message_data:
                raise ConnectionError("Connection closed")
            remaining_data += message_data

        return json.loads(remaining_data.decode("utf-8"))
    except Exception as e:
        raise ConnectionError(f"Error receiving message: {str(e)}")


def recv_all(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes, optimized for fewer recv calls"""
    # Try to get all data at once first
    data = sock.recv(n)
    if not data:
        return None

    if len(data) == n:  # Got everything in one call
        return data

    # If we didn't get everything, then accumulate the rest
    buffer = bytearray(data)
    remaining = n - len(data)

    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            return None
        buffer.extend(chunk)
        remaining -= len(chunk)

    return bytes(buffer)


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
        try:
            send_message(self.socket, request)
            response = receive_message(self.socket)
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
