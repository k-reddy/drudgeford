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
