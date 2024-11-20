import requests
from queue import Queue
from threading import Thread
import time

class ClientTaskQueue:
    """
    A wrapper that makes getting tasks from the server feel like using a regular Queue
    """
    def __init__(self, server_url, player_id):
        self.server_url = server_url
        self.player_id = player_id
        self.local_queue = Queue()  # Buffer for received tasks
        self.running = True
    
    def start_fetch_loop(self):
        # Start background thread to fetch tasks
        self.fetch_thread = Thread(target=self._fetch_loop, daemon=True)
        self.fetch_thread.start()

    def _fetch_loop(self):
        """
        Background thread that continuously fetches tasks from server
        """
        while self.running:
            try:
                response = requests.post(
                    f'{self.server_url}/get_tasks',
                    json={'player_id': self.player_id}
                )
                tasks = response.json()['tasks']
                # Put received tasks in local queue
                for task in tasks:
                    self.local_queue.put(task)
                time.sleep(5)  # Don't spam the server
            except Exception as e:
                print(f"Error fetching tasks: {e}")
    
    def get(self):
        """
        Gets next task from queue. Works just like Queue.get()
        """
        return self.local_queue.get()
    
    def empty(self):
        """
        Check if queue is empty. Works just like Queue.empty()
        """
        return self.local_queue.empty()
