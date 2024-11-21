import threading
import time
from .tcp_server import TCPServer
from .tcp_client import TCPClient
server = TCPServer()
server.start()

def test_task():
    client = TCPClient()
    task_list = [{"task_type":"test_task"}, {"task_type":"test_task_2"}]
    for task in task_list:
        client.post_task(task)
    actual = client.get_task()
    assert actual == task_list[0]
    server.stop()

def test_user_input():
    server = TCPServer()
    server.start()
    client = TCPClient()
    user_input = {"input_test":"cool input"}
    client.post_user_input(user_input)
    actual = client.get_user_input() 
    assert actual == user_input
    server.stop()

def test_diff_clients():
    server = TCPServer()
    server.start()
    client = TCPClient()
    client_2 = TCPClient()
    user_input = {"input_test":"cool input"}
    client.post_user_input(user_input)
    actual = client_2.get_user_input()
    assert actual == user_input
    server.stop()

def test_get_user_input_blocks():
    server = TCPServer()
    server.start()
    client = TCPClient()
    
    # Flag to track if get_user_input completed
    completed = False
    
    def client_thread():
        nonlocal completed
        client.get_user_input()  # This should block
        completed = True
    
    # Start get_user_input in a separate thread
    thread = threading.Thread(target=client_thread, daemon=True)
    thread.start()
    
    # Wait for thread to finish
    thread.join(timeout=1)
    
    # Verify the call was blocked 
    assert not completed 
    server.stop()

def test_get_task_doesnt_block():
    server = TCPServer()
    server.start()
    client = TCPClient()
    
    # Flag to track if get_user_input completed
    completed = False
    
    def client_thread():
        nonlocal completed
        client.get_task()  # This should not block
        completed = True
    
    # Start get_user_input in a separate thread
    thread = threading.Thread(target=client_thread, daemon=True)
    thread.start()
    
    # Wait for thread to finish
    thread.join(timeout=1)
    
    # Verify the call was blocked 
    assert completed 
    server.stop()