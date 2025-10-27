import threading
from collections import deque


class BoundedQueue:    
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = deque()
        self.mutex = threading.Lock()
        self.not_full = threading.Condition(self.mutex)
        self.not_empty = threading.Condition(self.mutex)
        self.all_done = False
    
    def put(self, item):
        with self.not_full:
            while len(self.queue) >= self.max_size and not self.all_done:
                self.not_full.wait()
            
            if not self.all_done:
                self.queue.append(item)
                self.not_empty.notify()
    
    def get(self):
        with self.not_empty:
            while len(self.queue) == 0 and not self.all_done:
                self.not_empty.wait()
            
            if self.all_done and len(self.queue) == 0:
                return None
            
            item = self.queue.popleft()
            self.not_full.notify()
            return item
    
    def mark_done(self):   
        with self.mutex:
            self.all_done = True
            self.not_empty.notify_all()

