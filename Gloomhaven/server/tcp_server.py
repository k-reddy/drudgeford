import socket
import threading
from dataclasses import dataclass
import queue
import json
import time
import traceback
from typing import List, Dict, Optional
from enum import Enum


def send_message(sock: socket.socket, data: dict):
    message = json.dumps(data).encode("utf-8")
    message_length = len(message)
    sock.send(message_length.to_bytes(4, byteorder="big"))
    sock.send(message)


def receive_message(sock: socket.socket) -> dict:
    length_bytes = recv_all(sock, 4)
    if not length_bytes:
        raise ConnectionError("Connection closed")
    message_length = int.from_bytes(length_bytes, byteorder="big")

    message = recv_all(sock, message_length)
    if not message:
        raise ConnectionError("Connection closed")
    return json.loads(message.decode("utf-8"))


def recv_all(sock: socket.socket, n: int) -> bytes:
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
    client_id: str
    client_type: ClientType
    tasks: List[Dict]
    thread: threading.Thread
    last_active: float = time.time()
    DISCONNECT_TIMEOUT: float = 10.0


class TCPServer:
    def __init__(self, host="0.0.0.0", port=8080, testing_mode=True, max_players=3):
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientData] = {}
        self.frontend_counter = 0
        self.user_input_queue = queue.Queue()
        self.persistent_frontend_tasks: List[Dict] = []
        self.lock = threading.Lock()
        self.running = False
        self.accept_thread = None
        self.shutdown_thread = None
        self.max_players = max_players
        self.start_time = None

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(
                0.5
            )  # Allow checking running flag periodically
        except Exception as e:
            print(f"Failed to initialize server socket: {str(e)}")
            if hasattr(self, "server_socket"):
                try:
                    self.server_socket.close()
                except:
                    pass
            raise

    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                # Check for startup timeout
                if (
                    not self.clients and time.time() - self.start_time > 600
                ):  # 10 minutes
                    print("No clients connected within 10 minutes. Shutting down...")
                    self.stop()
                    return

                try:
                    client_socket, _ = self.server_socket.accept()
                except socket.timeout:
                    continue

                # give people 10 mins to join
                client_socket.settimeout(600)

                client_info = receive_message(client_socket)
                client_type = ClientType(client_info.get("client_type"))

                # If a frontend client connects and shutdown timer is running, stop it
                if client_type == ClientType.FRONTEND:
                    if (
                        self.shutdown_thread is not None
                        and self.shutdown_thread.is_alive()
                    ):
                        self.shutdown_thread = None
                        print("New player connected. Canceling shutdown timer.")

                client_id = self._generate_client_id(client_type)
                send_message(client_socket, {"client_id": client_id})

                client_thread = threading.Thread(
                    target=self._handle_client,
                    daemon=True,
                    args=(client_socket, client_id),
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
            except Exception as e:
                if not isinstance(e, (socket.timeout, ConnectionError)):
                    print(f"Critical error in accept connections: {str(e)}")
                    traceback.print_exc()
                    self.stop()
                    return

    def start(self):
        try:
            self.running = True
            self.start_time = time.time()
            print("Server started. Waiting 10 minutes for first client...")

            self.accept_thread = threading.Thread(
                target=self._accept_connections, daemon=True
            )
            self.accept_thread.start()
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()
            raise

    def _generate_client_id(self, client_type: ClientType) -> str:
        if client_type == ClientType.BACKEND:
            return "backend"

        # Find the lowest unused frontend number
        used_numbers = {
            int(c.client_id.split("_")[1])
            for c in self.clients.values()
            if c.client_type == ClientType.FRONTEND
        }
        for i in range(1, self.max_players + 1):
            if i not in used_numbers:
                return f"frontend_{i}"

    def _handle_client(self, client_socket: socket.socket, client_id: str):
        try:
            client_data = self.clients[client_id]

            if client_data.client_type == ClientType.FRONTEND:
                with self.lock:
                    for task in self.persistent_frontend_tasks:
                        client_data.tasks.append(task)

            while self.running:
                try:
                    request = receive_message(client_socket)
                    client_data.last_active = time.time()
                    command = request.get("command")
                    payload = request.get("payload", {})
                    response = self._process_command(command, payload, client_id)
                    send_message(client_socket, response)
                except socket.timeout:
                    if (
                        time.time() - client_data.last_active
                        > client_data.DISCONNECT_TIMEOUT
                    ):
                        break
                    continue
                except (ConnectionError, json.JSONDecodeError):
                    break
                except Exception as e:
                    print(f"Critical error in client handler: {str(e)}")
                    traceback.print_exc()
                    self.stop()
                    return
        finally:
            self._handle_client_disconnect(client_id)

    def _handle_client_disconnect(self, client_id: str):
        try:
            with self.lock:
                if client_id not in self.clients:
                    return

                client = self.clients[client_id]
                try:
                    client.socket.close()
                except:
                    pass

                del self.clients[client_id]

                # Only start shutdown timer if server is still running
                if self.running and not any(
                    c.client_type == ClientType.FRONTEND for c in self.clients.values()
                ):
                    self.shutdown_thread = threading.Thread(
                        target=self._shutdown_timer, daemon=True
                    )
                    print(
                        "All players disconnected. Starting 5-minute shutdown timer..."
                    )
                    self.shutdown_thread.start()
        except Exception as e:
            print(f"Error in client disconnect: {str(e)}")
            self.stop()

    def stop(self):
        """Stop the server and clean up all resources gracefully"""
        if not self.running:
            return

        print("Initiating server shutdown...")
        self.running = False

        try:
            # Close all client connections first
            with self.lock:
                for client_data in self.clients.values():
                    try:
                        client_data.socket.close()
                    except:
                        pass
                self.clients.clear()

            # Try to wake up accept thread
            if self.accept_thread and self.accept_thread.is_alive():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((self.host, self.port))
                except:
                    pass
                self.accept_thread.join(timeout=0.5)

            # Close server socket
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.server_socket.close()

            # Clear the input queue
            while not self.user_input_queue.empty():
                try:
                    self.user_input_queue.get_nowait()
                except queue.Empty:
                    break

            print("Server shutdown complete")
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
            traceback.print_exc()
            # Even if we hit an error, try one last time to close the server socket
            try:
                self.server_socket.close()
            except:
                pass

    def _shutdown_timer(self):
        try:
            start_time = time.time()
            while self.running:
                if any(
                    c.client_type == ClientType.FRONTEND for c in self.clients.values()
                ):
                    print("Player reconnected. Canceling shutdown timer.")
                    return

                if time.time() - start_time > 300:  # 5 minutes
                    print("No players for 5 minutes. Shutting down...")
                    self.stop()
                    return

                time.sleep(1)
        except Exception as e:
            print(f"Error in shutdown timer: {str(e)}")
            self.stop()

    def _process_command(self, command: str, payload: Dict, client_id: str) -> Dict:
        """Process commands and return appropriate response"""
        try:
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
                user_input_data = self.user_input_queue.get()
                return {"user_input": user_input_data}

            elif command == "post_user_input":
                if client_data.client_type != ClientType.FRONTEND:
                    return {"error": "Only frontend can post user input"}
                user_input_data = {"source_client_id": client_id, "input": payload}
                self.user_input_queue.put(user_input_data)
                return {"status": "success"}

            else:
                raise ValueError("unknown command")

        except Exception as e:
            print(f"Error processing command: {str(e)}")
            traceback.print_exc()
            self.stop()
            return {"error": "Server shutting down due to error"}

    def _process_post_task(self, payload):
        """Process post task command"""
        try:
            target_client_id = payload.get("target_client_id")
            task_data = payload.get("task")
            if not target_client_id:
                raise ValueError("No target client id")

            if target_client_id == "ALL_FRONTEND":
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
        except Exception as e:
            print(f"Error processing post task: {str(e)}")
            traceback.print_exc()
            self.stop()
            return {"error": "Server shutting down due to error"}

    def stop(self):
        """Stop the server and clean up all resources gracefully"""
        print("Initiating server shutdown...")

        self.running = False

        try:
            if self.accept_thread and self.accept_thread.is_alive():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.host, self.port))
                self.accept_thread.join(timeout=0.5)  # Shorter timeout

            with self.lock:
                active_threads = [
                    client.thread
                    for client in self.clients.values()
                    if client.thread.is_alive()
                ]

            for thread in active_threads:
                thread.join(timeout=0.5)  # Shorter timeout

            while not self.user_input_queue.empty():
                try:
                    self.user_input_queue.get_nowait()
                except queue.Empty:
                    break

            with self.lock:
                for client_data in self.clients.values():
                    try:
                        client_data.socket.close()
                    except:
                        pass
                self.clients.clear()

            self.server_socket.close()
            print("Server shutdown complete")
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
            traceback.print_exc()
