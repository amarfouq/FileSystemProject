# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:15:09 2023

@author: Ayman
"""

# The copy module will be used during the copy method
import copy
import hashlib
from datetime import datetime

class Node:
    def __init__(self, name, parent=None, protected=False):
        if name == "":
            raise ValueError("A name cannot be blank")
        self.name = name
        self.parent = parent
        self.children = {}
        self.protected = protected
        self.permissions = {
            'move': set(),
            'rename': set(),
            'copy' : set(),
            'add_child': set(),
            'delete_child': set(),
        }
        
    def is_root(self):
        return self.parent is None

    def get_root(self):
        if self.is_root():
            return self
        else:
            return self.parent.get_root()

    def find_directory(self, name):
        if isinstance(self, Directory) and self.name == name:
            return self

        for child in self.children.values():
            if isinstance(child, Node):
                result = child.find_directory(name)
                if result:
                    return result

        return None

    def find_object(self, name):
        if self.name == name:
            return self

        for child in self.children.values():
            if isinstance(child, Node):
                result = child.find_object(name)
                if result is not None:
                    return result

        return None

    def get_site(self):
        node = self
        while node.parent is not None and not isinstance(node, Site):
            node = node.parent
        return node if isinstance(node, Site) else None

    def get_client(self):
        node = self
        while node.parent is not None and not isinstance(node, Client):
            node = node.parent
        return node if isinstance(node, Client) else None

    def add_permission(self, client_or_group, permission):
        if permission in self.permissions:
            self.permissions[permission].add(client_or_group)
        else:
            raise ValueError("Invalid permission.")
    
    def remove_permission(self, client_or_group, permission):
        if permission in self.permissions:
            if client_or_group in self.permissions[permission]:
                self.permissions[permission].remove(client_or_group)
            else:
                raise ValueError("Client or group does not have this permission.")
        else:
            raise ValueError("Invalid permission.")

    def has_permission(self, client, permission, force=0):
        if force==1:
            return True
        # Allow super admins to do anything
        if client.is_super_admin:
            return True
        # Admins can only modify nodes within their site
        elif client.is_admin and self.get_site() == client.get_site():
            return True
        # Regular clients check the specific permission
        else:
            if self.get_client() == client:
                return True
            return any(
                entity in self.permissions[permission]
                for entity in [client] + list(client.groups)
            )

    def add_child(self, client, child, force=0):
        if not self.has_permission(client, 'add_child', force):
            raise PermissionError("You do not have permission to add a child to this node.")
    
        if isinstance(self, File):
            raise TypeError("A file cannot have a child")
    
        if isinstance(child, Node):
            if child.name in self.children:
                raise ValueError("A child with the same name already exists in this directory.")
            child.parent = self  # Update the child's parent
            self.children[child.name] = child
        else:
            raise TypeError("Child must be an instance of Node or its subclass.")

    def delete_child(self, client, child_name, force=0):
        if not self.has_permission(client, 'delete_child', force):
            raise PermissionError("You do not have permission to delete a child from this node.")
        if child_name in self.children:
            child = self.children[child_name]
            if child.protected and not client.is_super_admin:
                raise PermissionError("Cannot delete protected child.")
            child.parent = None
            del self.children[child_name]
        else:
            raise ValueError("Child not found.")
    
    def move(self, client, new_parent, force=0):
        if not self.has_permission(client, 'move', force):
            raise PermissionError("You do not have permission to move this node.")
    
        current_site = self.get_site()
        new_parent_site = new_parent.get_site()

        #if not client.is_super_admin and current_site != new_parent_site:
        #    raise PermissionError("Cannot move to a different site.")
    
        if self.parent:
            if self.name in self.parent.children:
                self.parent.delete_child(client, self.name, 1)
        else:
            raise ValueError("Child not found in current parent's children.")
    
        new_parent.add_child(client, self, 1)

    
    def rename(self, client, new_name, force=0):
        if not self.has_permission(client, 'rename', force):
            raise PermissionError("You do not have permission to rename this node.")
        self.name = new_name
    
    def copy(self, client, new_parent, new_name=None, force=0):
        if not self.has_permission(client, 'copy'):
            raise PermissionError("You do not have permission to copy this node.")
        new_copy = copy.deepcopy(self)
        new_copy.name = new_name if new_name else self.name
        new_parent.add_child(client, new_copy, 1)

            
class Directory(Node):
    def __init__(self, name, parent=None, owner=None, protected=False):
        super().__init__(name, parent, protected)
        self.owner = owner  # Owner is the client who created the directory    

class Site(Directory): # A site is a directory
    def __init__(self, name, parent=None, protected=False):
        super().__init__(name, parent, protected)

class Client(Directory): # A client is a directory
    def __init__(self, name, parent=None, is_admin=False, is_super_admin=False, protected=False, password=None):
        super().__init__(name, parent, protected)
        self.is_admin = is_admin
        self.is_super_admin = is_super_admin
        self.groups = set()
        self.site = None
        self.password_hash = self._hash_password(password) if password else None
        self.log_file = LogFile(f"{name}_log", parent=self)
        self.add_child(self, self.log_file, 1)
        
    def set_admin_site(self, site):
        if self.is_admin:
            self.site = site
        else:
            raise ValueError("Only admin clients can have an associated site.")
            
    def _hash_password(self, password):
        salt = b'\x8fF\xd9Q\xf6\xb8\xa9\xf9\x93w\t\xed1\xdd\xad'
        password = password.encode('utf-8')
        hashed_password = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
        return hashed_password.hex()

class File(Node): # A is just a node
    def __init__(self, name, parent=None, content="", owner=None, protected=False):
        super().__init__(name, parent, protected)
        self.content = content
        self.owner = owner

class Root(Directory): # A root is a directory
    def __init__(self, name, parent=None, protected=True):
        super().__init__(name, parent, protected)


class Group:
    def __init__(self, name):
        self.name = name
        self.clients = set()

    def add_client(self, client):
        self.clients.add(client)
        client.groups.add(self)

    def remove_client(self, client):
        self.clients.remove(client)
        client.groups.remove(self)

    def has_client(self, client):
        return client in self.clients

class LogFile(File):
    def __init__(self, name, parent=None):
        super().__init__(name, parent, protected=True)

    def append_log(self, log):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] {log}\n"
        self.content += log_entry