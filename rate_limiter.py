import time

class RateLimiter:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clients = {}

    def is_allowed(self, client_ip):
        current_time = time.time()
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        self.clients[client_ip] = [t for t in self.clients[client_ip] if current_time - t < self.window_seconds]
        if len(self.clients[client_ip]) < self.limit:
            self.clients[client_ip].append(current_time)
            return True
        return False
