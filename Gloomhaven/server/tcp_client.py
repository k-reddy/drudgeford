import socket
import json
from enum import Enum


class ClientType(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"


class TCPClient:
    def __init__(self, client_type: ClientType, host="13.59.128.25", port=8080):
        self.client_type = client_type
        self.client_id = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self._identify()

    def _identify(self):
        """Identify client type to server and receive client ID"""
        identification = {"client_type": self.client_type.value}
        self.socket.send(json.dumps(identification).encode("utf-8"))
        data = self.socket.recv(4096).decode("utf-8")
        response = json.loads(data)
        self.client_id = response["client_id"]

    def _send_request(self, command, payload=None):
        request = {"command": command}
        if payload is not None:
            request["payload"] = payload

        try:
            self.socket.send(json.dumps(request).encode("utf-8"))
            data = self.socket.recv(4096).decode("utf-8")
            if not data:  # Connection closed
                raise ConnectionError("Connection closed by server")
            return json.loads(data)
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
