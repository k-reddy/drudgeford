import threading
import time
from server.tcp_server import TCPServer
from server.tcp_client import TCPClient, ClientType
from server.task_jsonifier import TaskJsonifier
from pyxel_ui.models import tasks


def test_task():
    server = TCPServer()
    server.start()
    backend = TCPClient(ClientType.BACKEND)
    frontend = TCPClient(ClientType.FRONTEND)
    task_list = [{"task_type":"test_task"}, {"task_type":"test_task_2"}]
    for task in task_list:
        backend.post_task(task, frontend.id)
    actual = frontend.get_task()
    assert actual == task_list[0]
    server.stop()

def test_user_input():
    server = TCPServer()
    server.start()
    frontend = TCPClient(ClientType.FRONTEND)
    backend = TCPClient(ClientType.BACKEND)
    user_input = {"input_test":"cool input"}
    frontend.post_user_input(user_input)
    actual = backend.get_user_input() 
    assert actual['input'] == user_input
    server.stop()

def test_diff_clients():
    server = TCPServer()
    server.start()
    frontend = TCPClient(ClientType.FRONTEND)
    backend = TCPClient(ClientType.BACKEND)
    user_input = {"input_test":"cool input"}
    frontend.post_user_input(user_input)
    actual = backend.get_user_input()
    assert actual['input'] == user_input
    server.stop()

def test_get_user_input_blocks():
    server = TCPServer()
    server.start()
    backend = TCPClient(ClientType.BACKEND)
    
    # Flag to track if get_user_input completed
    completed = False
    
    def client_thread():
        nonlocal completed
        backend.get_user_input()  # This should block
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
    frontend = TCPClient(ClientType.FRONTEND)
    
    # Flag to track if get_user_input completed
    completed = False
    
    def client_thread():
        nonlocal completed
        frontend.get_task()  # This should not block
        completed = True
    
    # Start get_user_input in a separate thread
    thread = threading.Thread(target=client_thread, daemon=True)
    thread.start()
    
    # Wait for thread to finish
    thread.join(timeout=1)
    
    # Verify the call was blocked 
    assert completed 
    server.stop()

def test_task_with_real_task():
    server = TCPServer()
    server.start()
    backend = TCPClient(ClientType.BACKEND)
    frontend = TCPClient(ClientType.FRONTEND)
    task = tasks.LoadLogTask(["hi","hello"])
    tj = TaskJsonifier()
    jsonified_task = tj.convert_task_to_json(task)
    backend.post_task(jsonified_task, frontend.id)
    actual = frontend.get_task()
    assert actual == jsonified_task
    server.stop()

def test_multi_client():
    # have frontend2 try to get a task when only task for 
    # frontend1 is loaded
    server = TCPServer()
    server.start()
    backend = TCPClient(ClientType.BACKEND)
    frontend = TCPClient(ClientType.FRONTEND)
    frontend2 = TCPClient(ClientType.FRONTEND)
    task = tasks.LoadLogTask(["hi","hello"])
    tj = TaskJsonifier()
    jsonified_task = tj.convert_task_to_json(task)
    backend.post_task(jsonified_task, frontend.id)
    frontend2_task = frontend2.get_task()
    frontend_task = frontend.get_task()

    assert frontend2_task == None
    assert frontend_task == jsonified_task


