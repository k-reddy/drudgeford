import socket
import json

class TCPClient:
    def __init__(self, host='localhost', port=8080):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def _send_request(self, command, payload=None):
        request = {'command': command}
        if payload is not None:
            request['payload'] = payload
        
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            data = self.socket.recv(1024).decode('utf-8')
            if not data:  # Connection closed
                raise ConnectionError("Connection closed by server")
            return json.loads(data)
        except (json.JSONDecodeError, ConnectionError) as e:
            self.close()
            raise ConnectionError(f"Connection error: {str(e)}")

    def get_task(self):
        response = self._send_request('get_task')
        return response['task']

    def post_task(self, task):
        return self._send_request('post_task', task)

    def get_user_input(self):
        try:
            response = self._send_request('get_user_input')
            if 'user_input' in response:
                return response['user_input']
            return None
        except ConnectionError:
            # If server closes connection during blocking operation,
            # that's expected behavior for the blocking test
            return None

    def post_user_input(self, user_input):
        return self._send_request('post_user_input', user_input)

    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # Socket might already be closed
        self.socket.close()