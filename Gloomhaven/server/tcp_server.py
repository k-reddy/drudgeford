import socket
import threading
import queue
import json
from typing import List, Dict

class TCPServer:
    def __init__(self, host='localhost', port=8080, testing_mode=True):
        self.host = host
        self.port = port
        self.testing_mode = testing_mode
        self.tasks: List[Dict] = []
        self.user_input_queue = queue.Queue()
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Track all threads for clean shutdown
        self.threads = []
        self.accept_thread = None
        
        # Only set SO_REUSEADDR in testing mode
        if self.testing_mode:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.lock = threading.Lock()
        # Shutdown control
        self.running = False

    def start(self):
        """Start the server and listen for connections"""
        print(f"Server started on {self.host}:{self.port}" + (" (testing mode)" if self.testing_mode else ""))
        self.running = True
        self.accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
        self.accept_thread.start()

    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address}")
                client_socket.settimeout(0.5)  # Non-blocking client socket
                with self.lock:
                    self.clients.append(client_socket)
                client_thread = threading.Thread(target=self._handle_client, daemon=True, args=(client_socket,))
                with self.lock:
                    self.threads.append(client_thread)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only log if not shutting down
                    print(f"Accept error: {e}")
                break

    def _handle_client(self, client_socket: socket.socket):
        """Handle individual client connections"""
        while self.running:
            try:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                command = request.get('command')
                payload = request.get('payload')

                if command == 'get_task':
                    with self.lock:
                        task = self.tasks.pop(0) if self.tasks else None
                    response = {'task': task}
                elif command == 'post_task':
                    with self.lock:
                        self.tasks.append(payload)
                    response = {'status': 'success'}
                elif command == 'get_user_input':
                    user_input = self.user_input_queue.get()
                    response = {'user_input': user_input}
                elif command == 'post_user_input':
                    self.user_input_queue.put(payload)
                    response = {'status': 'success'}
                else:
                    response = {'error': 'Invalid command'}

                client_socket.send(json.dumps(response).encode('utf-8'))
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only log if not shutting down
                    print(f"Client handler error: {e}")
                break

    def stop(self):
        """Stop the server and clean up all resources gracefully"""
        print("Initiating server shutdown...")
        
        # Signal threads to stop
        self.running = False
        
        # Wait for accept thread to finish
        if self.accept_thread and self.accept_thread.is_alive():
            try:
                # Send a dummy connection to unblock accept() if needed
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.host, self.port))
            except:
                pass
            self.accept_thread.join(timeout=2)
        
        # Wait for client threads to finish (with timeout)
        active_threads = []
        with self.lock:
            active_threads = [t for t in self.threads if t.is_alive()]
        
        for thread in active_threads:
            thread.join(timeout=2)
        
        # Clear queue to unblock any waiting threads
        while not self.user_input_queue.empty():
            try:
                self.user_input_queue.get_nowait()
            except queue.Empty:
                break
        
        # Close all client connections
        for client_socket in self.clients[:]:  # Copy list to avoid modification while iterating
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        try:
            self.server_socket.close()
        except:
            pass
        
        # Clear remaining resources
        self.tasks.clear()
        self.threads.clear()
        
        print("Server shutdown complete")