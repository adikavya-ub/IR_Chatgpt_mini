from hashlib import new
from tkinter.messagebox import NO
import math


class Node:
    def __init__(self, value, tfidf=None) -> None:
        self.next = None
        self.value = value
        self.skip_pointer = None
        self.tfidf = tfidf


class LinkedList:
    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.length, self.n_skips = 0, 0
        self.skip_length = 0

    def traverse_list(self):
        traversal = []
        if self.start_node:
            temp = self.start_node
            while temp:
                traversal.append(temp.value)
                temp = temp.next
        return traversal

    def traverse_skips(self):
        traversal = []
        if self.start_node:
            temp = self.start_node
            while temp:
                traversal.append(temp.value)
                temp = temp.skip_pointer
                    
        return traversal

    def add_skip_connections(self):
        n_skips = math.floor(math.sqrt(self.length))
        skip_length = round(math.sqrt(self.length), 0)
        if n_skips * n_skips == self.length:
            n_skips = n_skips - 1
            
        if n_skips < 3:
            return
        
        i = 0
        j = 0
        temp_start = self.start_node
        while i < n_skips:
            temp = temp_start
            while j != skip_length:
                j+=1
                if temp is not None:
                    temp = temp.next
            if j == skip_length:
                if temp_start is not None:
                  temp_start.skip_pointer = temp
                self.skip_length += 1
                j = 0
                temp_start = temp
            i += 1

    def insert_at_end(self, value, tfidf=None):
        new_node = Node(value, tfidf=tfidf)
        if self.start_node is None:
            self.start_node = new_node
            self.end_node = new_node
        elif self.end_node.value < value:
            temp = self.end_node
            self.end_node = new_node
            temp.next = self.end_node
        else:
            temp = self.start_node
            previous_node = None
            while temp and temp.value!=value:
                if value < temp.value:
                  if previous_node is None:
                    self.start_node = new_node
                    new_node.next = temp
                    break
                  else:
                    previous_node.next = new_node
                    new_node.next = temp
                    break
                previous_node = temp
                temp = temp.next
        self.length += 1
        return new_node
                            