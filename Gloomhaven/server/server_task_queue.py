from flask import Flask, jsonify, request
from queue import Queue
from threading import Thread, Event
from werkzeug.serving import make_server

class ServerTaskQueue:
    def __init__(self):
        self.tasks = {}  # Dictionary of queues, one per player
        self.app = Flask(__name__)
        self.server = None
        self.is_running = Event()
        
        # Register routes directly using decorators
        @self.app.route('/get_tasks', methods=['POST'])
        def get_tasks():
            data = request.get_json()
            player_id = data['player_id']
            player_queue = self.tasks.get(player_id, Queue())
            tasks = []
            while not player_queue.empty():
                tasks.append(player_queue.get())
            
            return jsonify({'tasks': tasks})
            
        @self.app.route('/add_player', methods=['POST'])
        def add_player():
            data = request.get_json()
            player_id = data['player_id']
            if player_id not in self.tasks:
                self.tasks[player_id] = Queue()
            return jsonify({'success': True})
    
    def put(self, task, player_id):
        if player_id not in self.tasks:
            self.tasks[player_id] = Queue()
        self.tasks[player_id].put(task)
    
    def broadcast(self, task):
        for player_id in self.tasks:
            self.put(task, player_id)
    
    def start(self, port=5000):
        """
        Starts the server in a separate thread.
        Returns immediately, doesn't block.
        """
        def run_flask():
            self.server = make_server('0.0.0.0', port, self.app)
            self.is_running.set()
            self.server.serve_forever()

        self.server_thread = Thread(target=run_flask, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start (but with timeout)
        if not self.is_running.wait(timeout=5.0):
            raise RuntimeError("Server failed to start within 5 seconds")
        
        print(f"Server started on port {port}")
    
    def stop(self):
        """
        Cleanly shuts down the server
        """
        if self.server:
            print("Shutting down server...")
            self.server.shutdown()
            self.is_running.clear()
            self.server_thread.join()
            print("Server stopped")